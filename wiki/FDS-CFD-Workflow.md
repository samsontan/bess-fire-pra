---
tags: [workflow, FDS, CFD, fire-simulation, reusable]
date: 2026-05-17
---

# FDS CFD Workflow for Fire Papers

Reusable workflow established for EQIX SG4-4A BESS paper. Copy for next fire paper.

## Prerequisites

| Tool | Path |
|------|------|
| FDS 6.10.1 | `C:\FDS_extract\firemodels\FDS6\bin\fds.exe` |
| MPI | `C:\FDS_extract\firemodels\FDS6\bin\mpi\mpiexec.exe` |
| Smokeview | `C:\FDS_extract\firemodels\SMV6\smokeview.exe` |
| Python packages | fdsreader, numpy, scipy, matplotlib, python-docx, Pillow |

## Step 1: Geometry Setup

Critical rules:
- Cabinet row: minimum 1.0 m clearance from all walls
- Mesh split (X=mid): never place VENT or OBST edge exactly on split
- Fire VENT: on exposed face of fire cabinet, at least 1 cell from split
- dx = 0.10-0.15 m for room-scale (7-10 m) fires

Validation run first (T_END=10 s) to verify geometry before full run.

## Step 2: Species + SURF

```fortran
&SPEC ID='HYDROGEN FLUORIDE', MW=20.01 /
&SPEC ID='HYDROGEN', MW=2.016 /
&SURF ID='TR_FIRE_SURF', HRRPUA=200., RAMP_Q='TR_HRR_RAMP',
      MASS_FLUX(1)=0.002, MASS_FLUX(2)=0.001,
      SPEC_ID(1)='HYDROGEN FLUORIDE', SPEC_ID(2)='HYDROGEN' /
```

## Step 3: Standard Slice Set (minimum)

```fortran
! Breathing zone Z=1.50 m
&SLCF PBZ=1.50, QUANTITY='MASS FRACTION', SPEC_ID='HYDROGEN FLUORIDE' /
&SLCF PBZ=1.50, QUANTITY='MASS FRACTION', SPEC_ID='HYDROGEN' /
&SLCF PBZ=1.50, QUANTITY='TEMPERATURE' /
! Ceiling Z=2.70 m
&SLCF PBZ=2.70, QUANTITY='MASS FRACTION', SPEC_ID='HYDROGEN FLUORIDE' /
&SLCF PBZ=2.70, QUANTITY='TEMPERATURE' /
! South aisle section (Y = cabinet south face - 0.50 m)
&SLCF PBY=1.50, QUANTITY='MASS FRACTION', SPEC_ID='HYDROGEN FLUORIDE' /
&SLCF PBY=1.50, QUANTITY='TEMPERATURE' /
! Vertical section through fire cabinet centre
&SLCF PBX=3.24, QUANTITY='HRRPUV' /
&SLCF PBX=3.24, QUANTITY='MASS FRACTION', SPEC_ID='HYDROGEN FLUORIDE' /
```

## Step 4: Run

```python
python "05_FDS_CFD-Simulation\scripts\launch_preview.py"
# Monitors C:\FDS_runs\eqix_preview\preview_run.log
```

Runtime: ~2 hours for 7.5x5x3 m room, 600 s simulation, dx=0.15 m, 2-mesh MPI.

## Step 5: Post-Processing (9 Figures)

```python
python "05_FDS_CFD-Simulation\scripts\fds_postprocess_bess.py"
```

Outputs to `05_FDS_CFD-Simulation\figures\`:
- Fig 14: HF BZ plan (PBZ=1.50)
- Fig 15: HF section south aisle (PBY=1.50)
- Fig 16: Temperature BZ plan
- Fig 17: Temperature ceiling
- Fig 18: HF ceiling
- Fig 19: H2 ceiling with LFL contour
- Fig 20: H2 BZ plan
- Fig 21: Fire section (HRRPUV + Temp + HF)
- Fig 22: HF sensor time history

## Known Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Cabinet against wall | Unrealistic plume, blocked aisle | Move to Y=2.00-2.90 m |
| VENT on mesh boundary | Fire halved or zeroed silently | Keep 1+ cell from split |
| fdsreader frame count | Only 16 frames after 61-frame run | Use `_read_sf_file()` directly |
| PBY slice in cabinet | All-zero plot (inside solid) | Move to south aisle (Y=1.50) |
| FDS title strip in figure | Text in published figure | White-out top 40px with Pillow |

## Full Skill Reference

`C:\Users\sbhta\.claude\skills\fds-cfd-fire\`
