---
tags: [workflow, event-tree, PRA, risk-analysis, reusable, matplotlib]
date: 2026-05-17
---

# Event Tree Workflow for Fire Engineering Papers

Established for EQIX SG4-4A BESS paper (Fig 7). Reusable for all fire PRA papers.

## Reference Standard

Barry, R.G. (1983). Risk-Informed, Performance-Based Industrial Fire Protection.
This book defines the canonical event tree format used by fire risk professionals.
Format: horizontal top spine, vertical drops at each node, horizontal branch lines, probability annotations.

## Template Script

```
11_FIGURE_DEVELOPMENT_EventTree-FNCurve\Eqix_Event_tree_Fig7_opus4.7\
  EQIX_SG44A_Figure7_EventTree_Package\generate_figure7.py
```

Copy and adapt for new papers. Change: branch probabilities, labels, design names (A/B).

## Key Design Rules

1. NO branch label: offset **0.35 units ABOVE** the branch line (not at same Y as YES)
2. YES branch label: offset below the upper branch
3. IE box width: 1.5x column width to avoid text overflow
4. Spine: solid horizontal line at top; vertical drops at each node
5. Two designs (A/B) shown on same tree using colour coding (blue=A, red=B)
6. Always save both PNG and SVG (SVG for journal submission if required)

## ERL Calculation

```python
ERL_A = sum(P(branch_i) * N_fatality_i for all branches in Design A)
ERL_B = sum(P(branch_i) * N_fatality_i for all branches in Design B)
reduction = (ERL_B - ERL_A) / ERL_B * 100  # percent
```

Compare against UK HSE criteria:
- > 1e-4/yr: Intolerable
- 1e-4 to 1e-6/yr: ALARP
- < 1e-6/yr: Broadly Acceptable

## Known Bugs

| Bug | Fix |
|-----|-----|
| NO label overlaps branch line | Offset NO label Y by +0.35 above midpoint |
| IE box text overflow | Set IE box width = 1.5 x column spacing |
| Excel format: text overlaps at all zoom levels | Use matplotlib not Excel for publication figures |

## FN Curve Template

```
11_FIGURE_DEVELOPMENT_EventTree-FNCurve\Eqix_FNCurve_Fig13_Final_260515\
  EQIX_SG44A_Figure13_FNCurves\generate_figure13.py
```

ALARP regions from HSE R2P2 (2001):
- Intolerable: N>=1 fatality line F > 1e-4/yr
- Broadly acceptable: N>=1 line F < 1e-6/yr
- ALARP: between the two lines

## Full Skill Reference

`C:\Users\sbhta\.claude\skills\event-tree\`
