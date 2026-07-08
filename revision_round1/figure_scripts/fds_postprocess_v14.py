"""
FDS post-processor: EQIX SG4-4A BESS fire simulation
Generates Fig 12 (PBY=2.50 centreline section) and Fig 14 (PBZ=1.50 breathing
zone plan) for journal paper. Also plots HF sensor time history.

Reads from preview run (600 s, 0.15 m mesh). Re-run at any time during or
after the FDS run -- uses whatever frames are already written.

Usage:
    python fds_postprocess_bess.py
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator
import warnings
warnings.filterwarnings('ignore')

try:
    import fdsreader
except ImportError:
    print("ERROR: fdsreader not installed. Run: pip install fdsreader")
    sys.exit(1)

# =============================================================================
# PATHS
# =============================================================================
FDS_DIR = r"C:\FDS_runs\eqix_corrected"
CHID    = "eqix_corrected"
OUT_DIR = "C:/temp_bess_v14/figures/fds"
os.makedirs(OUT_DIR, exist_ok=True)

# =============================================================================
# HF CONCENTRATION THRESHOLDS
# =============================================================================
MW_HF  = 20.01   # g/mol
MW_AIR = 28.97   # g/mol

def mf_to_ppm(arr):
    """Convert HF mass fraction (kg/kg) to volume ppm."""
    return np.asarray(arr) * (MW_AIR / MW_HF) * 1e6

TLV_C = 3.0    # ppm (ACGIH STEL)
IDLH  = 30.0   # ppm

# =============================================================================
# CABINET GEOMETRY
# =============================================================================
# (X_min, X_max, Y_min, Y_max) -- 7 Galaxy LBF cabinets
CABINETS = [
    (0.20, 1.00, 2.00, 2.90),
    (1.10, 1.90, 2.00, 2.90),
    (2.00, 2.80, 2.00, 2.90),
    (2.90, 3.70, 2.00, 2.90),  # CAB-4 TR origin
    (3.80, 4.60, 2.00, 2.90),
    (4.70, 5.50, 2.00, 2.90),
    (5.60, 6.40, 2.00, 2.90),
]
TR_CAB = 3  # CAB-4 index (0-based)
CAB_H  = 2.20  # cabinet height (m)

# Exhaust grille positions (ceiling, Z=3.0) -- Y=2.10-2.70 above cabinet row
EXHAUST_X = [(0.90, 1.50), (6.00, 6.60)]  # (X1, X2) pairs

# Custom colormap: white -> yellow -> orange -> red (HF hazard)
_hf_colors = ['#FFFFFF', '#FFFACD', '#FFD700', '#FF8C00', '#FF2200', '#8B0000']
CMAP_HF = matplotlib.colormaps.get_cmap('jet')


# =============================================================================
# MESH GEOMETRY (hardcoded for eqix_corrected two-mesh setup)
# MESH_1: XB=0.00-3.70, YB=0.00-5.00, ZB=0.00-3.00, IJK=24,33,20
# MESH_2: XB=3.70-7.50, YB=0.00-5.00, ZB=0.00-3.00, IJK=25,33,20
# =============================================================================
MESH_GEOM = [
    {'xb': (0.00, 3.70), 'yb': (0.00, 5.00), 'zb': (0.00, 3.00), 'ijk': (24, 33, 20)},
    {'xb': (3.70, 7.50), 'yb': (0.00, 5.00), 'zb': (0.00, 3.00), 'ijk': (25, 33, 20)},
]

def _mesh_nodes(geom):
    """Return (x_nodes, y_nodes, z_nodes) for a mesh."""
    ni, nj, nk = geom['ijk']
    x0, x1 = geom['xb']; y0, y1 = geom['yb']; z0, z1 = geom['zb']
    return (np.linspace(x0, x1, ni + 1),
            np.linspace(y0, y1, nj + 1),
            np.linspace(z0, z1, nk + 1))


# =============================================================================
# DIRECT BINARY READER -- bypasses fdsreader's stale frame-count bug
# =============================================================================
import struct

def _read_sf_file(filepath):
    """Read a FDS Fortran-unformatted slice file.
    Returns (times, data) where data shape is (n_t, ni, nj) with the
    collapsed axis already squeezed out.
    """
    def _rec(f):
        h = f.read(4)
        if len(h) < 4:
            return None
        n = struct.unpack('<i', h)[0]
        d = f.read(n)
        f.read(4)
        return d

    with open(filepath, 'rb') as f:
        _rec(f); _rec(f); _rec(f)   # quantity, short_name, units strings
        idx = _rec(f)
        if idx is None:
            return None, None
        imin, imax, jmin, jmax, kmin, kmax = struct.unpack('<6i', idx)
        ni = imax - imin + 1
        nj = jmax - jmin + 1
        nk = kmax - kmin + 1

        times, frames = [], []
        while True:
            t_rec = _rec(f)
            if t_rec is None or len(t_rec) < 4:
                break
            t = struct.unpack('<f', t_rec[:4])[0]
            d_rec = _rec(f)
            if d_rec is None:
                break
            arr = np.frombuffer(d_rec, dtype='<f4').reshape((ni, nj, nk), order='F').squeeze()
            times.append(t)
            frames.append(arr)

    if not frames:
        return None, None
    return np.array(times, dtype=float), np.stack(frames, axis=0)


def load_slice_direct(fds_dir, chid, sf_entries, orientation):
    """Load and combine two-mesh slice data from .sf binary files directly.

    sf_entries: list of (mesh_num, slice_num, filename) from smv_mapping entries
    orientation: 1=X-plane, 2=Y-plane, 3=Z-plane

    Returns: (times, data, h_coords, v_coords) where data shape is (n_t, nh, nv)
    """
    all_times, all_data = [], []
    mesh_nodes_list = []

    for mesh_num, slice_num, fname in sf_entries:
        fn = os.path.join(fds_dir, fname)  # use exact filename from SMV
        if not os.path.exists(fn):
            print(f"  WARNING: {fn} not found")
            continue
        times, data = _read_sf_file(fn)
        if times is None:
            continue
        all_times.append(times)
        all_data.append(data)
        mesh_nodes_list.append(_mesh_nodes(MESH_GEOM[mesh_num - 1]))

    if not all_data:
        return None, None, None, None

    # Verify all meshes have same time array (they should)
    ref_times = all_times[0]

    if len(all_data) == 1:
        data_combined = all_data[0]
        x_n, y_n, z_n = mesh_nodes_list[0]
        if orientation == 3:    # Z-plane: axes are x, y
            return ref_times, data_combined, x_n, y_n
        elif orientation == 2:  # Y-plane: axes are x, z
            return ref_times, data_combined, x_n, z_n
        else:                   # X-plane: axes are y, z
            return ref_times, data_combined, y_n, z_n

    # Combine two meshes along X (the split axis for this run)
    # data[0] shape: (n_t, ni1, nv)   data[1] shape: (n_t, ni2, nv)
    # Drop shared boundary column at X=3.70 (last col of mesh1 = first col of mesh2)
    d1, d2 = all_data[0], all_data[1]
    data_combined = np.concatenate([d1, d2[..., 1:, :] if d2.ndim == 3 else
                                    np.concatenate([d1, d2[:, 1:, :]], axis=1)], axis=1) \
                    if False else np.concatenate([d1, d2[:, 1:, :]], axis=1)

    x1_n = mesh_nodes_list[0][0]
    x2_n = mesh_nodes_list[1][0][1:]   # drop shared boundary
    x_combined = np.concatenate([x1_n, x2_n])
    y_n = mesh_nodes_list[0][1]
    z_n = mesh_nodes_list[0][2]

    if orientation == 3:    # Z-plane: h=x, v=y
        return ref_times, data_combined, x_combined, y_n
    elif orientation == 2:  # Y-plane: h=x, v=z
        return ref_times, data_combined, x_combined, z_n
    else:
        return ref_times, data_combined, y_n, z_n


def parse_smv_slices(smv_path):
    """Parse SMV file to extract slice file index mapping.
    Key = (quantity_keyword, orientation, plane_idx) where plane_idx is
    kmin for Z-planes, jmin for Y-planes, imin for X-planes.
    Returns dict: {key: [(mesh_num, slice_num, filename), ...]}
    """
    mapping = {}
    with open(smv_path, 'r') as f:
        lines = [l.rstrip() for l in f]
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('SLCF'):
            parts = line.split()
            try:
                mesh_num = int(parts[1])
                # indices: "# STRUCTURED & imin imax jmin jmax kmin kmax"
                amp_idx  = line.index('&')
                bang_idx = line.index('!')
                idx_vals = list(map(int, line[amp_idx+1:bang_idx].split()))
                imin, imax, jmin, jmax, kmin, kmax = idx_vals
                tail     = line[bang_idx+1:].split()
                slcf_num = int(tail[0])
                orient   = int(tail[2])
            except (ValueError, IndexError):
                i += 1; continue

            # plane_idx: collapsed axis index
            if orient == 3:   plane_idx = kmin
            elif orient == 2: plane_idx = jmin
            else:             plane_idx = imin

            if i + 2 < len(lines):
                fname    = lines[i + 1].strip()
                qty_name = lines[i + 2].strip().upper()
                key = (qty_name, orient, plane_idx)
                mapping.setdefault(key, []).append((mesh_num, slcf_num, fname))
            i += 3
        else:
            i += 1
    return mapping


# =============================================================================
# OVERLAY HELPERS
# =============================================================================
def add_cabinet_patches_plan(ax):
    for i, (x1, x2, y1, y2) in enumerate(CABINETS):
        fc = 'lightcoral' if i == TR_CAB else 'lightgray'
        ec = 'red'        if i == TR_CAB else 'dimgray'
        lw = 2.0          if i == TR_CAB else 1.0
        ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1,
                                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=5))
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, f'C{i+1}',
                ha='center', va='center', fontsize=8, color='black', zorder=6)
    # Mark exhaust grilles (ceiling projection at Y=2.10-2.70)
    for x1, x2 in EXHAUST_X:
        ax.add_patch(Rectangle((x1, 2.10), x2 - x1, 0.60,
                                facecolor='none', edgecolor='#0055CC',
                                linewidth=0.8, linestyle='--', zorder=6))
    # North wall supply (OPEN, Y=5.0)
    ax.add_patch(Rectangle((0.00, 4.75), 7.50, 0.25,
                            facecolor='#DDFFDD', edgecolor='#009900',
                            linewidth=0.6, alpha=0.5, zorder=3))
    ax.text(3.75, 4.87, 'Supply (OPEN)', ha='center', va='center',
            fontsize=8, color='#006600', zorder=6)
    # South aisle label
    ax.text(3.75, 1.00, 'South aisle', ha='center', va='center',
            fontsize=8, color='#555555', style='italic', zorder=6)
    ax.text(3.75, 3.95, 'North aisle', ha='center', va='center',
            fontsize=8, color='#555555', style='italic', zorder=6)


def add_cabinet_patches_section(ax):
    for i, (x1, x2, _, _) in enumerate(CABINETS):
        fc = 'lightcoral' if i == TR_CAB else 'silver'
        ec = 'red'        if i == TR_CAB else 'dimgray'
        ax.add_patch(Rectangle((x1, 0.0), x2 - x1, CAB_H,
                                facecolor=fc, edgecolor=ec, linewidth=1.0, zorder=5))
    # Mark exhaust grilles at ceiling
    for x1, x2 in EXHAUST_X:
        ax.add_patch(Rectangle((x1, 3.00 - 0.05), x2 - x1, 0.05,
                                facecolor='#99CCFF', edgecolor='#0055CC',
                                linewidth=0.8, zorder=6))


# =============================================================================
# FIGURE 14 -- PBZ=1.50 breathing zone plan view
# =============================================================================
def make_fig14(smv_mapping, fds_dir, chid):
    print("\n--- Fig 14: PBZ=1.50 breathing zone plan ---")
    # HF MASS FRACTION at Z=1.50 (k=10, orientation=3)
    key = ('HYDROGEN FLUORIDE MASS FRACTION', 3, 10)
    if key not in smv_mapping:
        print("  Slice PBZ HF not found in SMV.")
        return None
    entries = smv_mapping[key]

    times, all_data, h_vec, v_vec = load_slice_direct(fds_dir, chid, entries, 3)
    if times is None:
        print("  ERROR loading slice data.")
        return None

    t_max = times[-1]
    print(f"  Available: t=0--{t_max:.0f} s  ({len(times)} frames, DT_SLCF=10 s)")

    snap_targets = [120, 240, 360, 480, 600]
    snaps = [t for t in snap_targets if t <= t_max + 5]
    if not snaps:
        snaps = [t_max]

    n = len(snaps)
    n_col = 3 if n > 3 else n
    n_row = (n + n_col - 1) // n_col
    fig, axes = plt.subplots(n_row, n_col, figsize=(4.6 * n_col, 3.9 * n_row), sharey=True, sharex=True,
                             facecolor='white', constrained_layout=True)
    axes = np.atleast_1d(axes).flatten()
    for _ax in axes[n:]:
        _ax.set_visible(False)
    axes = axes[:n]

    ppm_max = max(1.0, float(np.nanmax(mf_to_ppm(all_data))))
    vmax = max(ppm_max * 1.05, IDLH * 2)
    XX, YY = np.meshgrid(h_vec, v_vec)       # both (nv, nh)

    for ax, t_target in zip(axes, snaps):
        tidx = int(np.argmin(np.abs(times - t_target)))
        t_act = times[tidx]
        data = all_data[tidx]                # shape (nh, nv)

        hf_ppm = mf_to_ppm(data)
        Z_plot = hf_ppm.T                    # (nv, nh) -- matches meshgrid shape

        ax.pcolormesh(XX, YY, Z_plot, cmap=CMAP_HF,
                      vmin=0, vmax=vmax, shading='auto', zorder=2)

        # Threshold contours
        for lvl, col, lbl in [(TLV_C, 'white', f'{TLV_C} ppm'),
                               (IDLH,  'black',    f'{IDLH} ppm')]:
            if np.nanmax(hf_ppm) > lvl:
                cs = ax.contour(XX, YY, Z_plot, levels=[lvl],
                                colors=[col], linewidths=1.2, zorder=7)
                try:
                    ax.clabel(cs, fmt={lvl: lbl}, fontsize=8.5, inline=True)
                except Exception:
                    pass

        add_cabinet_patches_plan(ax)
        ax.set_xlim(0, 7.5)
        ax.set_ylim(0, 5.0)
        ax.set_aspect('equal')
        ax.set_xlabel('X (m)', fontsize=11)
        t_str = f't = {t_act:.0f} s'
        if t_act < t_target - 5:
            t_str += ' (latest)'
        ax.set_title(t_str, fontsize=11, fontweight='bold')
        ax.grid(which='major', color='#CCCCCC', linewidth=0.4, zorder=1)
        ax.xaxis.set_minor_locator(MultipleLocator(0.5))
        ax.yaxis.set_minor_locator(MultipleLocator(0.5))

    axes[0].set_ylabel('Y (m)', fontsize=11)

    # Shared colorbar
    sm = plt.cm.ScalarMappable(cmap=CMAP_HF, norm=mcolors.Normalize(0, vmax))
    sm.set_array([])
    cb = fig.colorbar(sm, ax=axes, fraction=0.025, pad=0.02, aspect=25)
    cb.set_label('HF concentration (ppm)', fontsize=10)
    for lvl, col in [(TLV_C, 'white'), (IDLH, 'black')]:
        cb.ax.axhline(lvl / vmax, color=col, linewidth=1.2)

    (lambda *a, **k: None)(
        'Figure 14: HF Concentration at Breathing Zone (Z = 1.50 m)\n'
        'EQIX SG4-4A BESS Room 1 | 9 ACH Stage 0 Purge | NMC Galaxy LBF 242.76 kWh',
        fontsize=12, fontweight='bold')

    out_path = os.path.join(OUT_DIR, 'Fig14_HF_BZ_Plan_PBZ150.png')
    fig.savefig(out_path, dpi=600, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {out_path}")
    return out_path


# =============================================================================
# FIGURE 12 -- PBY=2.50 room centreline X-Z section
# =============================================================================
def make_fig12(smv_mapping, fds_dir, chid):
    print("\n--- Fig 12: PBY=1.50 south aisle section (in front of fire face) ---")
    # Y=1.50 m (j=10, orientation=2) -- south aisle cross-section
    key_hf   = ('HYDROGEN FLUORIDE MASS FRACTION', 2, 10)
    key_temp = ('TEMPERATURE', 2, 10)
    if key_hf not in smv_mapping:
        print("  Slice PBY HF not found in SMV.")
        return None

    entries_hf   = smv_mapping[key_hf]
    entries_temp = smv_mapping[key_temp] if key_temp in smv_mapping else []

    times, all_hf, h_vec, v_vec = load_slice_direct(fds_dir, chid, entries_hf, 2)
    if times is None:
        print("  ERROR loading HF slice.")
        return None

    t_max = times[-1]
    print(f"  HF slice available: t=0--{t_max:.0f} s  ({len(times)} frames)")

    snap_targets = [150, 300, 450, 600]
    snaps = [t for t in snap_targets if t <= t_max + 5]
    if not snaps:
        snaps = [t_max]

    n = len(snaps)
    fig, axes = plt.subplots(n, 1, figsize=(12, 3.2 * n),
                             facecolor='white', constrained_layout=True)
    axes = np.atleast_1d(axes).flatten()
    for _ax in axes[n:]:
        _ax.set_visible(False)
    axes = axes[:n]

    ppm_max = max(1.0, float(np.nanmax(mf_to_ppm(all_hf))))
    vmax = min(max(ppm_max * 1.05, IDLH * 2), 2000.0)
    XX, ZZ = np.meshgrid(h_vec, v_vec)        # both (nv, nh)

    # Pre-load temperature
    all_temp = XT = ZT = t_times = None
    if entries_temp:
        t_t, all_temp, th, tv = load_slice_direct(fds_dir, chid, entries_temp, 2)
        if all_temp is not None:
            XT, ZT = np.meshgrid(th, tv)
            t_times = t_t

    for ax, t_target in zip(axes, snaps):
        tidx = int(np.argmin(np.abs(times - t_target)))
        t_act = times[tidx]

        hf_ppm = mf_to_ppm(all_hf[tidx])
        Z_plot = hf_ppm.T                      # (nv, nh)

        ax.pcolormesh(XX, ZZ, Z_plot, cmap=CMAP_HF,
                      vmin=0, vmax=vmax, shading='auto', zorder=2, alpha=0.85)

        # Temperature contours if available
        if all_temp is not None:
            tidx_t  = int(np.argmin(np.abs(t_times - t_act)))
            T_plot  = all_temp[tidx_t].T       # (nv, nh)
            temp_levels = [50, 100, 200, 400]
            try:
                ct = ax.contour(XT, ZT, T_plot, levels=temp_levels,
                                colors=['black'],
                                linewidths=1.0, zorder=6)
                ax.clabel(ct, fmt='%d C', fontsize=8.5, inline=True)
            except Exception:
                pass

        # HF threshold contours
        for lvl, col, lbl in [(TLV_C, 'white', f'{TLV_C} ppm'),
                               (IDLH,  'black',    f'{IDLH} ppm')]:
            if np.nanmax(hf_ppm) > lvl:
                cs = ax.contour(XX, ZZ, Z_plot, levels=[lvl],
                                colors=[col], linewidths=1.0, linestyles='--', zorder=7)
                try:
                    ax.clabel(cs, fmt={lvl: lbl}, fontsize=8.5, inline=True)
                except Exception:
                    pass

        add_cabinet_patches_section(ax)

        ax.axhline(y=3.0, color='#666666', linewidth=1.2, zorder=8)
        ax.axhline(y=1.5, color='royalblue', linewidth=0.9, linestyle=':',
                   zorder=8, label='BZ z=1.5 m')

        ax.set_xlim(0, 7.5)
        ax.set_ylim(0, 3.2)
        ax.set_xlabel('X (m)', fontsize=11)
        ax.set_ylabel('Z (m)', fontsize=11)
        t_str = f't = {t_act:.0f} s'
        if t_act < t_target - 5:
            t_str += ' (latest)'
        ax.set_title(t_str, fontsize=11, fontweight='bold', pad=3)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(which='major', color='#CCCCCC', linewidth=0.4, zorder=1)
        ax.xaxis.set_minor_locator(MultipleLocator(0.5))
        ax.yaxis.set_minor_locator(MultipleLocator(0.25))

        # Shared colorbar on first panel only
        sm = plt.cm.ScalarMappable(cmap=CMAP_HF, norm=mcolors.Normalize(0, vmax))
        sm.set_array([])
        cb = fig.colorbar(sm, ax=ax, fraction=0.018, pad=0.01)
        cb.set_label('HF (ppm)', fontsize=9)
        for lvl, col in [(TLV_C, 'white'), (IDLH, 'black')]:
            cb.ax.axhline(lvl / vmax, color=col, linewidth=1.0)

    (lambda *a, **k: None)(
        'Figure 12: Fire Sequence -- HF Concentration + Temperature\n'
        'Vertical Section Y = 1.50 m (South Aisle, in front of CAB-4 fire face) | EQIX SG4-4A BESS Room 1\n'
        'Colour fill = HF (ppm) | Red-orange contours = temperature (deg C)',
        fontsize=12, fontweight='bold')

    out_path = os.path.join(OUT_DIR, 'Fig12_HF_Section_PBY150.png')
    fig.savefig(out_path, dpi=600, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {out_path}")
    return out_path


# =============================================================================
# FIGURE -- HF and H2 at CEILING (Z=2.70 m)
# =============================================================================
def make_fig_ceiling(smv_mapping, fds_dir, chid):
    print("\n--- Ceiling slices: HF and H2 at Z=2.70 m ---")
    H2_LFL_MF = 0.04 * 2.016 / 28.97   # 4% vol LFL in mass fraction

    # HF ceiling
    key_hf = ('HYDROGEN FLUORIDE MASS FRACTION', 3, 18)   # k=18 -> Z=2.70
    key_h2 = ('HYDROGEN MASS FRACTION', 3, 18)

    results = []
    for label, key, threshold, thr_label, cmap_name in [
        ('HF at Ceiling (Z=2.70 m)', key_hf, IDLH * MW_HF / MW_AIR / 1e6,
         f'IDLH {IDLH} ppm', CMAP_HF),
        ('H2 at Ceiling (Z=2.70 m)', key_h2, H2_LFL_MF,
         '4% LFL', None),
    ]:
        if key not in smv_mapping:
            print(f"  Slice {key} not found in SMV -- skipping.")
            continue
        entries = smv_mapping[key]
        times, all_data, h_vec, v_vec = load_slice_direct(fds_dir, chid, entries, 3)
        if times is None:
            continue

        snap_targets = [120, 240, 360, 480, 600]
        snaps = [t for t in snap_targets if t <= times[-1] + 5] or [times[-1]]
        n = len(snaps)

        _cmap = matplotlib.colormaps.get_cmap('jet')

        n_col = 3 if n > 3 else n
        n_row = (n + n_col - 1) // n_col
        fig, axes = plt.subplots(n_row, n_col, figsize=(4.6 * n_col, 3.9 * n_row), sharey=True, sharex=True,
                                 facecolor='white', constrained_layout=True)
        axes = np.atleast_1d(axes).flatten()
        for _ax in axes[n:]:
            _ax.set_visible(False)
        axes = axes[:n]

        vmax = max(float(np.nanmax(all_data)) * 1.05, threshold * 3)
        XX, YY = np.meshgrid(h_vec, v_vec)

        for ax, t_target in zip(axes, snaps):
            tidx  = int(np.argmin(np.abs(times - t_target)))
            t_act = times[tidx]
            data  = all_data[tidx]
            ax.pcolormesh(XX, YY, data.T, cmap=_cmap,
                          vmin=0, vmax=vmax, shading='auto', zorder=2)
            if np.nanmax(data) > threshold:
                cs = ax.contour(XX, YY, data.T, levels=[threshold],
                                colors=['red'], linewidths=1.5, zorder=7)
                try:
                    ax.clabel(cs, fmt={threshold: thr_label}, fontsize=8.5, inline=True)
                except Exception:
                    pass
            add_cabinet_patches_plan(ax)
            ax.set_xlim(0, 7.5); ax.set_ylim(0, 5.0); ax.set_aspect('equal')
            ax.set_xlabel('X (m)', fontsize=11)
            t_str = f't = {t_act:.0f} s'
            if t_act < t_target - 5:
                t_str += ' (latest)'
            ax.set_title(t_str, fontsize=11, fontweight='bold')
            ax.grid(which='major', color='#CCCCCC', linewidth=0.4, zorder=1)
            ax.xaxis.set_minor_locator(MultipleLocator(0.5))
            ax.yaxis.set_minor_locator(MultipleLocator(0.5))

        axes[0].set_ylabel('Y (m)', fontsize=11)
        sm = plt.cm.ScalarMappable(cmap=_cmap, norm=mcolors.Normalize(0, vmax))
        sm.set_array([])
        cb = fig.colorbar(sm, ax=axes, fraction=0.025, pad=0.02, aspect=25)
        is_hf = 'HF' in label
        cb_lbl = 'HF mass fraction (kg/kg)' if is_hf else 'H2 mass fraction (kg/kg)'
        cb.set_label(cb_lbl, fontsize=10)

        (lambda *a, **k: None)(f'{label}\nEQIX SG4-4A BESS Room 1 | 9 ACH Stage 0 Purge',
                     fontsize=12, fontweight='bold')

        slug = 'HF_Ceiling_PBZ270' if is_hf else 'H2_Ceiling_PBZ270'
        out_path = os.path.join(OUT_DIR, f'{slug}.png')
        fig.savefig(out_path, dpi=600, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"  Saved: {out_path}")
        results.append(out_path)

    return results


# =============================================================================
# FIGURE -- H2 at BREATHING ZONE (Z=1.50 m)
# =============================================================================
def make_fig_h2_bz(smv_mapping, fds_dir, chid):
    print("\n--- H2 at breathing zone Z=1.50 m ---")
    key = ('HYDROGEN MASS FRACTION', 3, 10)   # k=10 -> Z=1.50
    if key not in smv_mapping:
        print("  Slice H2 Z=1.50 not found.")
        return None
    entries = smv_mapping[key]
    times, all_data, h_vec, v_vec = load_slice_direct(fds_dir, chid, entries, 3)
    if times is None:
        return None

    H2_LFL_MF  = 0.04 * 2.016 / 28.97
    H2_STEL_MF = 0.25 * 2.016 / 28.97   # 25% LFL (detection threshold common in BESS)

    snap_targets = [120, 240, 360, 480, 600]
    snaps = [t for t in snap_targets if t <= times[-1] + 5] or [times[-1]]
    n = len(snaps)

    _cmap = mcolors.LinearSegmentedColormap.from_list(
        'h2_bz', ['#FFFFFF', '#E8F4FF', '#99CCFF', '#3377FF', '#0000BB', '#000044'], N=256)

    n_col = 3 if n > 3 else n
    n_row = (n + n_col - 1) // n_col
    fig, axes = plt.subplots(n_row, n_col, figsize=(4.6 * n_col, 3.9 * n_row), sharey=True, sharex=True,
                             facecolor='white', constrained_layout=True)
    axes = np.atleast_1d(axes).flatten()
    for _ax in axes[n:]:
        _ax.set_visible(False)
    axes = axes[:n]

    vmax = max(float(np.nanmax(all_data)) * 1.05, H2_LFL_MF * 0.5)
    XX, YY = np.meshgrid(h_vec, v_vec)

    for ax, t_target in zip(axes, snaps):
        tidx  = int(np.argmin(np.abs(times - t_target)))
        t_act = times[tidx]
        data  = all_data[tidx]
        ax.pcolormesh(XX, YY, data.T, cmap=_cmap,
                      vmin=0, vmax=vmax, shading='auto', zorder=2)
        for lvl, col, lbl in [(H2_STEL_MF, 'orange', '25% LFL'),
                               (H2_LFL_MF,  'red',    '100% LFL')]:
            if np.nanmax(data) > lvl:
                cs = ax.contour(XX, YY, data.T, levels=[lvl],
                                colors=[col], linewidths=1.2, zorder=7)
                try:
                    ax.clabel(cs, fmt={lvl: lbl}, fontsize=8.5, inline=True)
                except Exception:
                    pass
        add_cabinet_patches_plan(ax)
        ax.set_xlim(0, 7.5); ax.set_ylim(0, 5.0); ax.set_aspect('equal')
        ax.set_xlabel('X (m)', fontsize=11)
        t_str = f't = {t_act:.0f} s'
        if t_act < t_target - 5:
            t_str += ' (latest)'
        ax.set_title(t_str, fontsize=11, fontweight='bold')
        ax.grid(which='major', color='#CCCCCC', linewidth=0.4, zorder=1)
        ax.xaxis.set_minor_locator(MultipleLocator(0.5))
        ax.yaxis.set_minor_locator(MultipleLocator(0.5))

    axes[0].set_ylabel('Y (m)', fontsize=11)
    sm = plt.cm.ScalarMappable(cmap=_cmap, norm=mcolors.Normalize(0, vmax))
    sm.set_array([])
    cb = fig.colorbar(sm, ax=axes, fraction=0.025, pad=0.02, aspect=25)
    cb.set_label('H2 mass fraction (kg/kg)', fontsize=10)
    (lambda *a, **k: None)('H2 Concentration at Breathing Zone (Z = 1.50 m)\n'
                 'EQIX SG4-4A BESS Room 1 | 9 ACH Stage 0 Purge',
                 fontsize=12, fontweight='bold')
    out_path = os.path.join(OUT_DIR, 'H2_BZ_Plan_PBZ150.png')
    fig.savefig(out_path, dpi=600, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {out_path}")
    return out_path


# =============================================================================
# FIGURE -- X=3.24 m VERTICAL SECTION THROUGH FIRE (HRRPUV + TEMP + HF)
# =============================================================================
def make_fig_fire_section(smv_mapping, fds_dir, chid):
    print("\n--- X=3.24 m vertical section through CAB-4 fire ---")
    # i=21 in MESH_1 → X = 21/24 * 3.70 = 3.2375 m
    keys = {
        'HRRPUV':  ('HRRPUV', 1, 21),
        'TEMP':    ('TEMPERATURE', 1, 21),
        'HF':      ('HYDROGEN FLUORIDE MASS FRACTION', 1, 21),
    }
    datasets = {}
    for label, key in keys.items():
        if key not in smv_mapping:
            print(f"  {label} slice not found -- skipping.")
            continue
        entries = smv_mapping[key]
        times, data, h_vec, v_vec = load_slice_direct(fds_dir, chid, entries, 1)
        if times is not None:
            datasets[label] = (times, data, h_vec, v_vec)

    if not datasets:
        print("  No X-section slices loaded.")
        return None

    snap_targets = [150, 300, 450, 600]
    ref_times = list(datasets.values())[0][0]
    snaps = [t for t in snap_targets if t <= ref_times[-1] + 5] or [ref_times[-1]]
    n_col = len(snaps)
    n_row = len(datasets)

    fig, axes = plt.subplots(n_row, n_col,
                             figsize=(3.2 * n_col, 3.0 * n_row),
                             facecolor='white', constrained_layout=True)
    if n_row == 1:
        axes = axes[np.newaxis, :]
    if n_col == 1:
        axes = axes[:, np.newaxis]

    row_titles = {'HRRPUV': 'HRRPUV (kW/m3)', 'TEMP': 'Temperature (C)', 'HF': 'HF (ppm)'}
    row_cmaps  = {
        'HRRPUV': mcolors.LinearSegmentedColormap.from_list(
                      'hrr', ['#FFFFFF','#FFFACD','#FFD700','#FF4500','#8B0000'], N=256),
        'TEMP':   mcolors.LinearSegmentedColormap.from_list(
                      'tmp', ['#EEF0FF','#AADDFF','#FFCC00','#FF4400','#660000'], N=256),
        'HF':     CMAP_HF,
    }

    # Cabinet cross-section overlay for X=3.24 (through CAB-4): Y=2.00-2.90, Z=0.00-2.20
    def add_cab_section_xplane(ax):
        ax.add_patch(Rectangle((2.00, 0.00), 0.90, CAB_H,
                                facecolor='lightcoral', edgecolor='red',
                                linewidth=1.2, zorder=5))
        ax.text(2.45, CAB_H / 2, 'CAB-4\n(TR)',
                ha='center', va='center', fontsize=8.5, color='black', zorder=6)

    for r_idx, (qty_label, (times_q, all_data, h_vec, v_vec)) in enumerate(datasets.items()):
        XX, ZZ = np.meshgrid(h_vec, v_vec)   # h=Y(0-5), v=Z(0-3)
        scale  = 1e-3 if qty_label == 'HRRPUV' else (MW_AIR / MW_HF * 1e6 if qty_label == 'HF' else 1.0)
        vmax   = float(np.nanmax(all_data)) * scale * 1.05
        vmax   = max(vmax, 1.0)

        for c_idx, t_target in enumerate(snaps):
            ax = axes[r_idx, c_idx]
            tidx  = int(np.argmin(np.abs(times_q - t_target)))
            t_act = times_q[tidx]
            frame = all_data[tidx].T * scale   # (nv, nh)
            frame = np.maximum(frame, 0)

            ax.pcolormesh(XX, ZZ, frame, cmap=row_cmaps[qty_label],
                          vmin=0, vmax=vmax, shading='auto', zorder=2)

            # Threshold lines
            if qty_label == 'TEMP':
                for lvl, col in [(100, '#FF8800'), (300, '#FF2200'), (600, '#880000')]:
                    if frame.max() > lvl:
                        cs = ax.contour(XX, ZZ, frame, levels=[lvl], colors=[col],
                                        linewidths=0.8, zorder=7)
                        try:
                            ax.clabel(cs, fmt=f'{lvl}C', fontsize=8, inline=True)
                        except Exception:
                            pass
            elif qty_label == 'HF':
                for lvl, col, lbl in [(TLV_C, 'white', f'{TLV_C} ppm'),
                                       (IDLH,  'black',    f'{IDLH} ppm')]:
                    if frame.max() > lvl:
                        cs = ax.contour(XX, ZZ, frame, levels=[lvl], colors=[col],
                                        linestyles='--', linewidths=0.8, zorder=7)
                        try:
                            ax.clabel(cs, fmt={lvl: lbl}, fontsize=8, inline=True)
                        except Exception:
                            pass

            add_cab_section_xplane(ax)
            ax.axhline(1.5, color='royalblue', linewidth=0.7, linestyle=':', zorder=8)
            ax.set_xlim(0, 5.0); ax.set_ylim(0, 3.2)
            ax.set_aspect('equal')
            ax.grid(which='major', color='#CCCCCC', linewidth=0.4, zorder=1)
            ax.yaxis.set_minor_locator(MultipleLocator(0.25))
            ax.xaxis.set_minor_locator(MultipleLocator(0.5))

            if r_idx == 0:
                t_str = f't = {t_act:.0f} s'
                if t_act < t_target - 5:
                    t_str += ' (latest)'
                ax.set_title(t_str, fontsize=11, fontweight='bold')
            if r_idx == n_row - 1:
                ax.set_xlabel('Y (m)', fontsize=11)
            if c_idx == 0:
                ax.set_ylabel(f'Z (m)\n{row_titles[qty_label]}', fontsize=10)

            # Per-row colorbar on last column
            if c_idx == n_col - 1:
                sm = plt.cm.ScalarMappable(cmap=row_cmaps[qty_label],
                                           norm=mcolors.Normalize(0, vmax))
                sm.set_array([])
                fig.colorbar(sm, ax=ax, fraction=0.05, pad=0.02,
                             label=row_titles[qty_label], )

    (lambda *a, **k: None)('Vertical Section X = 3.24 m (through CAB-4 fire) | EQIX SG4-4A BESS\n'
                 'Top: HRRPUV   Middle: Temperature   Bottom: HF concentration',
                 fontsize=12, fontweight='bold')

    out_path = os.path.join(OUT_DIR, 'FireSection_X324.png')
    fig.savefig(out_path, dpi=600, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {out_path}")
    return out_path


# =============================================================================
# HF SENSOR TIME HISTORY
# =============================================================================
def make_device_plot(sim):
    print("\n--- HF sensor time history ---")
    try:
        devc = sim.devices
    except Exception as e:
        print(f"  Device data not available: {e}")
        return None

    # DeviceCollection: first device is 'Time', rest are sensors
    dev_list = list(devc)
    time_arr = np.array(dev_list[0].data)  # Time pseudo-device gives t array
    hf_devs = {d.id: d for d in dev_list[1:]
               if 'HF' in getattr(d, 'id', '').upper()}

    if not hf_devs:
        print("  No HF devices found.")
        return None

    fig, ax = plt.subplots(figsize=(10, 4.5), facecolor='white',
                           constrained_layout=True)
    line_colors = ['#CC0000', '#FF6600', '#0055CC', '#009900', '#AA00AA']

    for (dev_id, dev), col in zip(hf_devs.items(), line_colors):
        try:
            d_arr   = np.array(dev.data)
            ppm_arr = mf_to_ppm(d_arr)
            pretty = {'HF_NORTH_AISLE_BZ': 'North aisle (breathing zone)',
                      'HF_DOOR_BZ': 'Door (breathing zone)',
                      'HF_CEILING_CAB4': 'Ceiling above CAB-4'}
            ax.plot(time_arr, ppm_arr, color=col, linewidth=1.5,
                    label=pretty.get(dev_id, dev_id))
        except Exception as e:
            print(f"  WARNING: {dev_id}: {e}")

    ax.axhline(IDLH,  color='black',   linewidth=1.5, linestyle='-',  alpha=0.85,
               label=f'IDLH = {IDLH} ppm')
    ax.axhline(TLV_C, color='#555555', linewidth=1.2, linestyle='--', alpha=0.85,
               label=f'STEL = {TLV_C} ppm')
    ax.axhline(0.5,   color='#999999', linewidth=1.0, linestyle=':',  alpha=0.85,
               label='Ceiling = 0.5 ppm')

    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel('HF concentration (ppm)', fontsize=12)
    ax.legend(fontsize=10, loc='lower right', ncol=2)
    ax.set_xlim(left=0)
    ax.set_yscale('log')
    ax.set_ylim(0.3, 3000)
    ax.grid(which='major', alpha=0.35)
    ax.xaxis.set_minor_locator(MultipleLocator(30))

    out_path = os.path.join(OUT_DIR, 'HF_Sensor_TimeHistory.png')
    fig.savefig(out_path, dpi=600, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {out_path}")
    return out_path


# =============================================================================
# FIGURE -- TEMPERATURE at CEILING (Z=2.70 m, plan view)
# =============================================================================
def make_fig_temp_ceiling(smv_mapping, fds_dir, chid):
    print("\n--- Temperature at ceiling Z=2.70 m (plan view) ---")
    key = ('TEMPERATURE', 3, 18)   # k=18 -> Z=2.70
    if key not in smv_mapping:
        print("  Slice TEMP Z=2.70 not found (requires new FDS run with PBZ=2.70 TEMPERATURE slice).")
        return None
    entries = smv_mapping[key]
    times, all_data, h_vec, v_vec = load_slice_direct(fds_dir, chid, entries, 3)
    if times is None:
        return None

    snap_targets = [120, 240, 360, 480, 600]
    snaps = [t for t in snap_targets if t <= times[-1] + 5] or [times[-1]]
    n = len(snaps)

    _cmap = matplotlib.colormaps.get_cmap('jet')
    T_amb = 20.0
    T_max = max(float(np.nanmax(all_data)), 200.0)
    vmax  = T_max * 1.05

    n_col = 3 if n > 3 else n
    n_row = (n + n_col - 1) // n_col
    fig, axes = plt.subplots(n_row, n_col, figsize=(4.6 * n_col, 3.9 * n_row), sharey=True, sharex=True,
                             facecolor='white', constrained_layout=True)
    axes = np.atleast_1d(axes).flatten()
    for _ax in axes[n:]:
        _ax.set_visible(False)
    axes = axes[:n]

    XX, YY = np.meshgrid(h_vec, v_vec)

    for ax, t_target in zip(axes, snaps):
        tidx  = int(np.argmin(np.abs(times - t_target)))
        t_act = times[tidx]
        data  = all_data[tidx]
        T_plot = data.T

        ax.pcolormesh(XX, YY, T_plot, cmap=_cmap,
                      vmin=T_amb, vmax=vmax, shading='auto', zorder=2)

        for lvl, col in [(50, 'black'), (100, 'black'),
                         (200, 'black'), (400, 'black')]:
            if np.nanmax(data) > lvl:
                cs = ax.contour(XX, YY, T_plot, levels=[lvl],
                                colors=[col], linewidths=1.0, zorder=7)
                try:
                    ax.clabel(cs, fmt=f'{lvl}C', fontsize=8.5, inline=True)
                except Exception:
                    pass

        add_cabinet_patches_plan(ax)
        ax.set_xlim(0, 7.5)
        ax.set_ylim(0, 5.0)
        ax.set_aspect('equal')
        ax.set_xlabel('X (m)', fontsize=11)
        t_str = f't = {t_act:.0f} s'
        if t_act < t_target - 5:
            t_str += ' (latest)'
        ax.set_title(t_str, fontsize=11, fontweight='bold')
        ax.grid(which='major', color='#CCCCCC', linewidth=0.4, zorder=1)
        ax.xaxis.set_minor_locator(MultipleLocator(0.5))
        ax.yaxis.set_minor_locator(MultipleLocator(0.5))

    axes[0].set_ylabel('Y (m)', fontsize=11)

    sm = plt.cm.ScalarMappable(cmap=_cmap, norm=mcolors.Normalize(T_amb, vmax))
    sm.set_array([])
    cb = fig.colorbar(sm, ax=axes, fraction=0.025, pad=0.02, aspect=25)
    cb.set_label('Temperature (deg C)', fontsize=10)

    (lambda *a, **k: None)(
        'Temperature at Ceiling (Z = 2.70 m) -- Plan View\n'
        'EQIX SG4-4A BESS Room 1 | 9 ACH Stage 0 Purge | NMC Galaxy LBF 242.76 kWh',
        fontsize=12, fontweight='bold')

    out_path = os.path.join(OUT_DIR, 'Temp_Ceiling_PBZ270.png')
    fig.savefig(out_path, dpi=600, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {out_path}")
    return out_path


# =============================================================================
# FIGURE -- TEMPERATURE at BREATHING ZONE (Z=1.50 m, plan view)
# =============================================================================
def make_fig_temp_bz(smv_mapping, fds_dir, chid):
    print("\n--- Temperature at breathing zone Z=1.50 m (plan view) ---")
    key = ('TEMPERATURE', 3, 10)   # k=10 -> Z=1.50
    if key not in smv_mapping:
        print("  Slice TEMP Z=1.50 not found.")
        return None
    entries = smv_mapping[key]
    times, all_data, h_vec, v_vec = load_slice_direct(fds_dir, chid, entries, 3)
    if times is None:
        return None

    snap_targets = [120, 240, 360, 480, 600]
    snaps = [t for t in snap_targets if t <= times[-1] + 5] or [times[-1]]
    n = len(snaps)

    _cmap = matplotlib.colormaps.get_cmap('jet')

    n_col = 3 if n > 3 else n
    n_row = (n + n_col - 1) // n_col
    fig, axes = plt.subplots(n_row, n_col, figsize=(4.6 * n_col, 3.9 * n_row), sharey=True, sharex=True,
                             facecolor='white', constrained_layout=True)
    axes = np.atleast_1d(axes).flatten()
    for _ax in axes[n:]:
        _ax.set_visible(False)
    axes = axes[:n]

    T_amb  = 20.0
    T_max  = max(float(np.nanmax(all_data)), 200.0)
    vmax   = T_max * 1.05

    XX, YY = np.meshgrid(h_vec, v_vec)

    for ax, t_target in zip(axes, snaps):
        tidx  = int(np.argmin(np.abs(times - t_target)))
        t_act = times[tidx]
        data  = all_data[tidx]   # shape (nh, nv)
        T_plot = data.T          # (nv, nh)

        ax.pcolormesh(XX, YY, T_plot, cmap=_cmap,
                      vmin=T_amb, vmax=vmax, shading='auto', zorder=2)

        # Contours at 50, 100, 200, 400 C
        for lvl, col in [(50, 'black'), (100, 'black'),
                         (200, 'black'), (400, 'black')]:
            if np.nanmax(data) > lvl:
                cs = ax.contour(XX, YY, T_plot, levels=[lvl],
                                colors=[col], linewidths=1.0, zorder=7)
                try:
                    ax.clabel(cs, fmt=f'{lvl}C', fontsize=8.5, inline=True)
                except Exception:
                    pass

        add_cabinet_patches_plan(ax)
        ax.set_xlim(0, 7.5)
        ax.set_ylim(0, 5.0)
        ax.set_aspect('equal')
        ax.set_xlabel('X (m)', fontsize=11)
        t_str = f't = {t_act:.0f} s'
        if t_act < t_target - 5:
            t_str += ' (latest)'
        ax.set_title(t_str, fontsize=11, fontweight='bold')
        ax.grid(which='major', color='#CCCCCC', linewidth=0.4, zorder=1)
        ax.xaxis.set_minor_locator(MultipleLocator(0.5))
        ax.yaxis.set_minor_locator(MultipleLocator(0.5))

    axes[0].set_ylabel('Y (m)', fontsize=11)

    sm = plt.cm.ScalarMappable(cmap=_cmap, norm=mcolors.Normalize(T_amb, vmax))
    sm.set_array([])
    cb = fig.colorbar(sm, ax=axes, fraction=0.025, pad=0.02, aspect=25)
    cb.set_label('Temperature (deg C)', fontsize=10)
    for lvl, col in [(50, 'black'), (100, 'black'), (200, 'black'), (400, 'black')]:
        cb.ax.axhline((lvl - T_amb) / (vmax - T_amb), color=col, linewidth=1.0)

    (lambda *a, **k: None)(
        'Temperature at Breathing Zone (Z = 1.50 m) -- Plan View\n'
        'EQIX SG4-4A BESS Room 1 | 9 ACH Stage 0 Purge | NMC Galaxy LBF 242.76 kWh',
        fontsize=12, fontweight='bold')

    out_path = os.path.join(OUT_DIR, 'Temp_BZ_Plan_PBZ150.png')
    fig.savefig(out_path, dpi=600, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {out_path}")
    return out_path


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=" * 65)
    print("FDS Post-processor: EQIX SG4-4A BESS (preview run)")
    print(f"  Run dir : {FDS_DIR}")
    print(f"  Output  : {OUT_DIR}")
    print("=" * 65)

    smv = os.path.join(FDS_DIR, f"{CHID}.smv")
    if not os.path.exists(smv):
        print(f"ERROR: {smv} not found. Start the FDS run first.")
        sys.exit(1)

    # Parse SMV for slice file mapping
    smv_path = os.path.join(FDS_DIR, f"{CHID}.smv")
    smv_map  = parse_smv_slices(smv_path)
    print(f"Slice types in SMV: {len(smv_map)}")
    for (qty, orient, pidx), entries in smv_map.items():
        print(f"  orient={orient} plane={pidx} | {qty} | files: {[e[2] for e in entries]}")

    f14      = make_fig14(smv_map, FDS_DIR, CHID)
    f12      = make_fig12(smv_map, FDS_DIR, CHID)
    f_ceil   = make_fig_ceiling(smv_map, FDS_DIR, CHID)
    f_h2bz   = make_fig_h2_bz(smv_map, FDS_DIR, CHID)
    f_fire   = make_fig_fire_section(smv_map, FDS_DIR, CHID)
    f_temp   = make_fig_temp_bz(smv_map, FDS_DIR, CHID)
    f_tempc  = make_fig_temp_ceiling(smv_map, FDS_DIR, CHID)

    # Devices via fdsreader (frame count not affected by the bug)
    print("\nLoading devices via fdsreader...")
    try:
        sim = fdsreader.Simulation(FDS_DIR)
        fdt = make_device_plot(sim)
    except Exception as e:
        print(f"  Device load failed: {e}")
        fdt = None

    print("\n" + "=" * 65)
    print("COMPLETE. Figures:")
    all_figs = [f14, f12] + (f_ceil or []) + [f_h2bz, f_fire, f_temp, f_tempc, fdt]
    for p in all_figs:
        if p:
            print(f"  {p}")
    print("=" * 65)


if __name__ == '__main__':
    main()