#!/usr/bin/env python3
"""
EQIX SG4-4A BESS Fire Safety PRA - Figure 13: F-N Curves (v4 final)
Societal risk presentation per Vrijling et al. (1995) and UK HSE R2P2 (2001).

Revisions v3→v4:
- Tolerance line labels now horizontal, anchored inside plot area
- Cleaner reduction badge text
- Slight tightening of axis range
- Better legend positioning
"""

import os
import sys
import subprocess

# Dependency check
try:
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import numpy as np
except ImportError:
    print("Installing required packages: matplotlib, numpy")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "numpy"])
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PNG_PATH = os.path.join(SCRIPT_DIR, "EQIX-SG4-4A_Figure13_FNCurves.png")
SVG_PATH = os.path.join(SCRIPT_DIR, "EQIX-SG4-4A_Figure13_FNCurves.svg")

# ============================================================
# SCENARIO DATA (manuscript Section 4.6)
# ============================================================
scenarios = [
    {
        "label": "1-Comp (hypothetical), Water-only",
        "color": "#D8743B", "marker": "s",
        "fn1": 2.5e-5, "fn2": 1.8e-6,
    },
    {
        "label": "2-Comp, Water-only",
        "color": "#C0392B", "marker": "o",
        "fn1": 2.1e-5, "fn2": 1.5e-6,
    },
    {
        "label": "2-Comp, Gas+Water dual",
        "color": "#1F6FAB", "marker": "D",
        "fn1": 4.3e-6, "fn2": 3.1e-7,
    },
    {
        "label": "2-Comp, Gas+Water + improved BMS",
        "color": "#1D7A4D", "marker": "^",
        "fn1": 1.4e-6, "fn2": 1.0e-7,
    },
]

fn1_water = 2.1e-5
fn1_gas = 4.3e-6
reduction_fn = (fn1_water - fn1_gas) / fn1_water * 100
print(f"F(N≥1) reduction water-only → gas+water: {reduction_fn:.1f}%")

# ============================================================
# FIGURE
# ============================================================
fig, ax = plt.subplots(figsize=(11, 7.5))
fig.patch.set_facecolor('white')

x_min, x_max = 0.8, 4.0
y_min, y_max = 1e-9, 5e-4

N_band = np.logspace(np.log10(x_min), np.log10(x_max), 200)
F_upper = 1e-3 / N_band
F_lower = 1e-5 / N_band

# Background tolerance zones
ax.fill_between(N_band, F_upper, y_max, color='#F5C6C6', alpha=0.35, zorder=1)
ax.fill_between(N_band, F_lower, F_upper, color='#FBE5C0', alpha=0.35, zorder=1)
ax.fill_between(N_band, y_min, F_lower, color='#D4ECD4', alpha=0.35, zorder=1)

# Tolerance boundary lines
ax.plot(N_band, F_upper, '--', color='#B23B3B', linewidth=1.5, alpha=0.9, zorder=2)
ax.plot(N_band, F_lower, '--', color='#0F6E56', linewidth=1.5, alpha=0.9, zorder=2)

# ============================================================
# TOLERANCE LINE LABELS - horizontal, with leader hint, positioned right of data
# ============================================================
# F = 10^-3/N anchored at N=2.5 (clear of data points), text at N=3.0
ax.annotate(r'F = 10$^{-3}$/N',
            xy=(2.5, 1e-3/2.5), xytext=(3.0, 1.2e-4),
            fontsize=9.5, color='#B23B3B', fontweight='600',
            ha='left', va='center',
            arrowprops=dict(arrowstyle='-', color='#B23B3B', lw=0.8, alpha=0.5),
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor='#B23B3B', linewidth=0.6, alpha=0.95),
            zorder=7)

# F = 10^-5/N anchored at N=2.5, text at N=3.0
ax.annotate(r'F = 10$^{-5}$/N',
            xy=(2.5, 1e-5/2.5), xytext=(3.0, 1.2e-6),
            fontsize=9.5, color='#0F6E56', fontweight='600',
            ha='left', va='center',
            arrowprops=dict(arrowstyle='-', color='#0F6E56', lw=0.8, alpha=0.5),
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor='#0F6E56', linewidth=0.6, alpha=0.95),
            zorder=7)

# ============================================================
# ZONE LABELS - right margin, pinned in clear space at x=3.8
# ============================================================
ax.text(3.8, 4e-4, 'INTOLERABLE',
        fontsize=11, fontweight='bold', color='#791F1F',
        ha='right', va='center',
        bbox=dict(boxstyle='round,pad=0.35', facecolor='#F5C6C6',
                  edgecolor='#B23B3B', linewidth=0.9, alpha=0.92))

# ALARP positioned at mid-band height (geometric mean of band edges at x=3.8)
# Upper: 10^-3/3.8 = 2.6e-4, Lower: 10^-5/3.8 = 2.6e-6, mid = ~2.6e-5
ax.text(3.8, 2.5e-5, 'ALARP',
        fontsize=11, fontweight='bold', color='#7A4A0B',
        ha='right', va='center',
        bbox=dict(boxstyle='round,pad=0.35', facecolor='#FBE5C0',
                  edgecolor='#BA7517', linewidth=0.9, alpha=0.92))

ax.text(3.8, 8e-9, 'BROADLY\nACCEPTABLE',
        fontsize=10, fontweight='bold', color='#085041',
        ha='right', va='center',
        bbox=dict(boxstyle='round,pad=0.35', facecolor='#D4ECD4',
                  edgecolor='#0F6E56', linewidth=0.9, alpha=0.92))

# ============================================================
# SCENARIO F-N CURVES
# ============================================================
for s in scenarios:
    N_pts = [1, 2]
    F_pts = [s["fn1"], s["fn2"]]
    ax.plot(N_pts, F_pts, '-', color=s["color"], linewidth=2.0,
            alpha=0.9, zorder=3)
    ax.plot(N_pts, F_pts, s["marker"], color=s["color"], markersize=11,
            markeredgecolor='white', markeredgewidth=1.5,
            label=s["label"], zorder=4)

# ============================================================
# ============================================================
# COMPARTMENTATION-ALONE ANNOTATION
# Note explaining why 1-Comp and 2-Comp Water-only are close on F(N≥1)
# ============================================================
# 1-Comp F(N≥1) = 2.5e-5, 2-Comp Water-only F(N≥1) = 2.1e-5 → 16% reduction
ax.annotate(
    'Compartmentation alone:\nonly 16% F(N≥1) reduction\n(consequence bounded per\ncompartment, not installation)',
    xy=(1.0, 2.3e-5),            # point to between the orange and red markers at N=1
    xytext=(1.5, 1.5e-4),        # text in upper-right area within ALARP zone
    fontsize=8, fontweight='500', color='#7A4A0B', style='italic',
    ha='left', va='center',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#FBE5C0',
              edgecolor='#BA7517', linewidth=0.7, alpha=0.85),
    arrowprops=dict(arrowstyle='->', color='#BA7517', lw=0.9, alpha=0.6,
                    connectionstyle='arc3,rad=-0.2'),
    zorder=6)

# ============================================================
# REDUCTION ARROW (vertical, at N=1)
# ============================================================
arrow_x = 1.0
ax.annotate('', xy=(arrow_x, 4.3e-6), xytext=(arrow_x, 2.1e-5),
            arrowprops=dict(arrowstyle='->', color='#0F6E56',
                            lw=2.5, alpha=0.95, mutation_scale=18),
            zorder=5)

# Reduction badge - placed in clear space below the curves, with leader arrow to the data
ax.annotate(
    '79.5% reduction in F(N$\\geq$1)\nby adding gas suppression\n(Branch B vs Branch A)',
    xy=(1.0, 1e-5),              # arrow tip points to the midpoint of the vertical reduction arrow
    xytext=(1.45, 5e-8),         # text anchored in the clear broadly-acceptable zone (lower-right of N=1)
    fontsize=9, fontweight='600', color='#085041',
    ha='left', va='center',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#E8F4EE',
              edgecolor='#0F6E56', linewidth=1.2, alpha=0.97),
    arrowprops=dict(arrowstyle='-', color='#0F6E56', lw=1, alpha=0.6,
                    connectionstyle='arc3,rad=-0.2'),
    zorder=6)

# ============================================================
# AXIS STYLING
# ============================================================
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

ax.xaxis.set_major_locator(mticker.FixedLocator([1, 2]))
ax.xaxis.set_minor_locator(mticker.NullLocator())
ax.set_xticklabels(['1', '2'])

ax.axvline(x=2, color='#888888', linestyle=':', linewidth=0.8, alpha=0.4, zorder=1)
ax.text(2.05, 3e-9, 'N$_{max}$ = 2\n(operator + responder)',
        fontsize=8, color='#5f5e5a', ha='left', va='bottom', style='italic')

ax.set_xlabel('Number of Fatalities, N',
              fontsize=11.5, fontweight='600', labelpad=8)
ax.set_ylabel(r'Annual Frequency of N or more Fatalities, F(N$\geq$n) [yr$^{-1}$]',
              fontsize=11.5, fontweight='600', labelpad=6)

ax.grid(True, which='major', linestyle=':', linewidth=0.5, alpha=0.5, zorder=0)
ax.grid(True, which='minor', axis='y', linestyle=':', linewidth=0.3, alpha=0.3, zorder=0)

for spine in ax.spines.values():
    spine.set_edgecolor('#555555')
    spine.set_linewidth(0.8)

# ============================================================
# LEGEND
# ============================================================
legend = ax.legend(loc='lower left', fontsize=9, framealpha=0.97,
                   edgecolor='#888888', fancybox=False,
                   title='Scenarios', title_fontsize=9.5)
legend.get_title().set_fontweight('bold')

# ============================================================
# TITLES
# ============================================================
plt.suptitle('Figure 13 — Societal Risk F-N Curves, BESS Fire Scenarios',
             fontsize=13, fontweight='bold', y=0.98)
plt.title('EQIX SG4-4A, Singapore  |  NMC 485.52 kWh total  |  Two-Compartment Design',
          fontsize=10, color='#5f5e5a', pad=10)

fig.text(0.99, 0.005,
         'Tolerance criteria: UK HSE R2P2 (2001)  |  Monte Carlo PRA N=10,000  |  '
         r'P$_{occ}$=0.15, P$_{fatal}$=0.825 per occupant',
         ha='right', va='bottom', fontsize=7.5, color='#888888', style='italic')

plt.tight_layout()
plt.subplots_adjust(top=0.92, bottom=0.10)

plt.savefig(PNG_PATH, dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig(SVG_PATH, bbox_inches='tight', facecolor='white')
print(f"Saved: {PNG_PATH}")
print(f"Saved: {SVG_PATH}")
plt.close()
