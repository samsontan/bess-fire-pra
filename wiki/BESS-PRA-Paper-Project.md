---
tags: [project, fire-engineering, BESS, PRA, FDS, CFD, journal-paper, staarch]
project: EQIX-SG4-4A BESS Fire Safety Paper
status: under-review
date: 2026-05-17
---

# BESS Fire Safety Paper -- Project Overview

## Identity

**Title**: Probabilistic Risk Assessment of Grid-Scale Lithium-Ion Battery Energy Storage System Fire Hazards: A Monte Carlo Simulation Framework for Hydrogen Fluoride Toxicity and Suppression Effectiveness

**Journal**: Fire and Materials (Wiley), Q1
**Status**: v11 complete, sent to co-authors 2026-05-17 for review

## Authors

| Author | Affiliation | Role |
|--------|------------|------|
| Samson Tan | VU ISILC + Staarch | Corresponding author |
| Teoh Teik Toe | NTU AI/NBS + Staarch | Co-author |
| Paul Joseph | VU ISILC | Co-author |
| Khalid Moinuddin | VU ISILC | Co-author |

## Context

This paper arose from a SCDF NFPA 855 Hazard Mitigation Analysis (HMA) report that STAARCH prepared for a 485.52 kWh NMC battery energy storage system at a data centre (7 Tai Seng Ave, Singapore) operated by Equinix. The BESS is classified as Level 5 under SCDF Fire Code and required prior approval via the NFPA 855 Exception (1) pathway.

The installation used two suppression layers (Fluoro-K/HFC-227ea pre-action + water mist sprinkler), which contradicts FM Global DS 5-33 (which prescribes water only). The PRA provides quantitative justification for the dual suppression design.

## Key Results

| Metric | Water-only (B) | Gas+Water (A) | Ratio |
|--------|--------------|--------------|-------|
| Annual ERL | 1.22 x 10^-4 | 2.40 x 10^-5 | -80.3% |
| ALARP band | Tolerable boundary | Broadly acceptable | |
| HF exceeds IDLH | 100% scenarios | N/A | |
| Single-stage suppression eff. | 37.9% mean | - | |
| Time to IDLH (BZ) | ~120 s (FDS CFD) | - | |

## Folder

`G:\My Drive\SAI\Projects\EQIX_SG4-4A_NFPA855_HMA_Waiver_Report\__Mickey7_BESS_Fire_Safety_Paper\`

## Related Wiki

- [[FDS-CFD-Workflow]] -- How to run FDS simulations for fire papers
- [[Event-Tree-Workflow]] -- How to build publication event trees
- [[BESS-Fire-Domain-Knowledge]] -- Battery fire safety technical knowledge
- [[Python-DOCX-Manuscript-Toolkit]] -- python-docx patterns for manuscript building
