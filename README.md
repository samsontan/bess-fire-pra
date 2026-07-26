# BESS Fire Safety Paper -- Scripts and Models

**Paper**: Probabilistic Risk Assessment of Grid-Scale Lithium-Ion Battery Energy Storage System Fire Hazards: A Monte Carlo Simulation Framework for Hydrogen Fluoride Toxicity and Suppression Effectiveness

**Journal**: Fire and Materials (Wiley, Q1) -- under review 2026

**Authors**: Samson Tan, Teoh Teik Toe, Paul Joseph, Khalid Moinuddin

---

## Repository Structure

```
pra/                    Monte Carlo PRA simulation scripts
  pra_simulation.py     Main simulation (N=10,000 iterations)
  sensitivity_analyses.py
  suppression_erl_model.py
  generate_figures.py
  generate_docx.py
  results/              JSON output files (pra_results, sensitivity, suppression)

fds/
  input/                FDS 6.10.1 input file (eqix_preview.fds)
  scripts/
    fds_postprocess_bess.py   Post-processor: 9 publication figures from FDS binary
    launch_preview.py         FDS launch (2-mesh MPI)
    open_smokeview.py

figures/
  event_tree/           Event tree Fig 7 generator (matplotlib, Barry format)
  fn_curve/             FN curve Fig 13 generator (ALARP regions)

manuscript_build/       Python scripts that built manuscript v9-v11
  finalize_manuscript_v9.py
  build_v10_citations.py
  prepare_bess_draft_for_reviewers.py
  save_as_v11.py
  PROCESS_LEARNINGS.md  Full lessons from this paper -- read before next paper

wiki/                   Obsidian wiki files (domain knowledge + reusable workflows)
  FDS-CFD-Workflow.md
  Event-Tree-Workflow.md
  Python-DOCX-Manuscript-Toolkit.md
  BESS-Fire-Domain-Knowledge.md
```

## Key Results

| Metric | Water-only | Gas+Water |
|--------|-----------|-----------|
| Annual ERL | 1.22 x 10^-4 | 2.40 x 10^-5 |
| ALARP band | Tolerable boundary | Broadly acceptable |
| ERL reduction | -- | **80.3%** |

HF exceeds NIOSH IDLH (30 ppm) in 100% of Monte Carlo scenarios.
FDS CFD (NIST FDS 6.10.1) confirms HF reaches IDLH at breathing zone from t~120 s.

## Requirements

```
pip install numpy scipy matplotlib python-docx Pillow fdsreader pywin32
```

FDS 6.10.1: https://github.com/firemodels/fds/releases

## Context

This paper arose from a SCDF NFPA 855 HMA report for a 485.52 kWh NMC BESS installation
at a data centre (7 Tai Seng Ave, Singapore). The dual-suppression design (clean agent +
water mist) contradicts FM Global DS 5-33 prescription (water only). This PRA provides
the quantitative justification for the two-stage design.

## License

Code: MIT License
Data: CC BY 4.0

## Paths referenced in the published paper

Fire (MDPI), fire-4382023. Each path below resolves as printed:

| Paper refers to | Location |
|---|---|
| `pra_simulation.py` (from repository root) | root shim -> `pra/pra_simulation.py` |
| `fds_input/eqix_sg4_4a.fds` | `fds_input/` (copy of `fds/input/eqix_preview.fds`) |
| `pra_results.json` | `pra/results/pra_results.json` |
| `suppression_erl_results.json` | `pra/results/suppression_erl_results.json` |
| Figure S-A.1 (convergence) | `figures/` |
