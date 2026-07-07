# Revision round 1 (fire-4382023, 2026-07-07)

Materials referenced in the round-1 response letters.

- `fds_corrected/`: corrected FDS input (`eqix_corrected.fds`; HRRPUA 419.58 kW/m2,
  correcting a W/m2 unit-entry error in the original `eqix_preview_ORIGINAL_erroneous.fds`),
  run log, HRR and device outputs (corrected peak 713 kW at t = 385 s).
- `figures_original_run/`: the nine CFD figures as originally submitted (erroneous run).
- `figures_corrected_run/`: all twelve revised figures (corrected run + rebuilt event tree,
  F-N curves, and sensitivity tornado).
- `analysis/`: event-tree uncertainty propagation and tornado sensitivity
  (`event_tree_uncertainty.py`, N = 100,000, seed 42) and box-model vs FDS comparison
  numbers (`compute_r1_numbers.py`).
- `figure_scripts/`: generation scripts for every figure.
