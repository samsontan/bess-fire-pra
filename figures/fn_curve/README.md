# EQIX SG4-4A Figure 13 — Societal Risk F-N Curves

**Manuscript:** Probabilistic Risk Assessment of Grid-Scale Lithium-Ion Battery Energy Storage System Fire Hazards
**Target journal:** Fire and Materials
**Prepared by:** Samson Tan PhD (BOA Reg. No. 1324) | STAARCH Pte Ltd
**Source data:** Manuscript Section 4.6, Monte Carlo PRA (N = 10,000)

---

## Purpose

F-N curves present societal risk per the convention of Vrijling et al. (1995) and the UK HSE
*Reducing Risks, Protecting People* (R2P2, 2001) tolerance criteria. Plot annual frequency
F(N≥n) against number of fatalities N, with tolerance bands shaded as background zones:
- **Intolerable** (above F = 10⁻³/N): risk must be reduced regardless of cost
- **ALARP** (between F = 10⁻⁵/N and F = 10⁻³/N): risk reduced to As Low As Reasonably Practicable
- **Broadly acceptable** (below F = 10⁻⁵/N): no further reduction needed, monitor only

## Key revisions from manuscript v6

The v6 manuscript figure had four issues that this rebuild addresses:

| Issue (v6) | Fix (v4 rebuild) |
|-----------|------------------|
| Cluttered legend inside plot area | Legend in lower-left empty space, four distinct markers (square/circle/diamond/triangle) |
| "80.3% reduction" stated on F-N chart was actually the ERL reduction | Corrected to **79.5% F(N≥1) reduction**; equivalence to 80.3% ERL noted in badge |
| Tolerance lines without zone shading — hard to read where each band starts/ends | HSE tolerance zones now shaded (pink/peach/green) as continuous background |
| Wasted right-side chart area with no data beyond N=2 | X-axis tightened to N=0.8–3.2 with N_max=2 indicator |

## Files in this package

| File | Purpose |
|------|---------|
| `EQIX-SG4-4A_Figure13_FNCurves.png` | Rendered PNG at 300 dpi (publication quality) |
| `EQIX-SG4-4A_Figure13_FNCurves.svg` | Vector source (editable in Inkscape/Illustrator) |
| `generate_figure13.py` | Python regeneration script (matplotlib-based) |
| `generate_figure13.bat` | Windows launcher |
| `generate_figure13.sh` | macOS/Linux launcher |
| `EQIX-SG4-4A_Figure13_FNCurves_Workbook.xlsx` | Excel data table + embedded PNG |

## Regenerating

### Windows
Double-click `generate_figure13.bat`. Auto-installs matplotlib and numpy if not present.

### macOS / Linux
```bash
chmod +x generate_figure13.sh
./generate_figure13.sh
```

Or directly:
```bash
pip install matplotlib numpy
python3 generate_figure13.py
```

## Numerical values (verification)

All values from manuscript Section 4.6, Table on page 12:

| Scenario | F(N≥1) [/yr] | F(N≥2) [/yr] | Classification |
|----------|-------------:|-------------:|:---------------|
| 1-Comp (hypothetical), Water-only | 2.5 × 10⁻⁵ | 1.8 × 10⁻⁶ | ALARP |
| 2-Comp, Water-only (Branch A baseline) | 2.1 × 10⁻⁵ | 1.5 × 10⁻⁶ | ALARP |
| 2-Comp, Gas+Water dual (Branch B) | 4.3 × 10⁻⁶ | 3.1 × 10⁻⁷ | **Broadly Acceptable** |
| 2-Comp, Gas+Water + improved BMS (P=0.05) | 1.4 × 10⁻⁶ | 1.0 × 10⁻⁷ | **Broadly Acceptable** |

### Reduction calculations

- **F(N≥1) reduction, Branch B vs Branch A**: (2.1×10⁻⁵ − 4.3×10⁻⁶) / 2.1×10⁻⁵ = **79.5%**
- **ERL reduction, Branch B vs Branch A** (per Section 4.5.5): (1.22×10⁻⁴ − 2.4×10⁻⁵) / 1.22×10⁻⁴ = **80.3%**

These are different metrics; the manuscript v6 figure conflated them as "80.3% reduction" on the F-N plot, which was strictly incorrect for F(N≥1). The rebuild reports the correct F(N≥1) reduction (79.5%) and notes the equivalent ERL reduction (80.3%) as a related metric.

### F-N equations (per manuscript Section 4.6)

For occupant count N_occ = 2 (operator + responder), independent Bernoulli P_occ = 0.15 per person, conditional fatality probability P_fatal = 0.825:

$$F(N \geq 1) = P_{unc,annual} \times \left[1 - (1 - P_{occ} \cdot P_{fatal})^{N_{occ}}\right]$$

$$F(N \geq 2) = P_{unc,annual} \times (P_{occ} \cdot P_{fatal})^{N_{occ}}$$

where P_unc,annual = P_multi,annual × P(suppression fails).

## Manuscript integration instructions

In the manuscript v6 PDF:

1. **Replace Figure 13** (page 13) with the PNG in this package
2. **Update Figure 13 caption** to read:
   > Figure 13. F-N curves for BESS fire scenarios, EQIX SG4-4A. UK HSE R2P2 (2001) tolerance bands shown as background shading: intolerable (above F = 10⁻³/N), ALARP (between F = 10⁻⁵/N and F = 10⁻³/N), and broadly acceptable (below F = 10⁻⁵/N). Four scenarios plotted: 1-comp water-only (orange square), 2-comp water-only (red circle), 2-comp gas+water dual (blue diamond), and 2-comp gas+water with improved BMS (green triangle). Voluntary dual suppression reduces F(N≥1) from 2.1×10⁻⁵ to 4.3×10⁻⁶/yr (79.5% reduction, equivalent to 80.3% ERL reduction per Section 4.5.5), crossing the broadly acceptable boundary.

3. **Update Section 4.6 text** to use 79.5% for F(N≥1) reduction (currently the section text correctly leaves the F-N numbers but the figure annotation conflated them with ERL). Specifically:

   - Page 12 last paragraph currently says "Dual suppression reduces F(N≥1) from 2.1×10⁻⁵ to 4.3×10⁻⁶/yr, crossing the broadly acceptable boundary."
   - Suggest extending to: "...crossing the broadly acceptable boundary (a 79.5% reduction in F(N≥1), equivalent to the 80.3% ERL reduction reported in Section 4.5.5)."

## Reviewer considerations for Fire and Materials

- **Tolerance criteria attribution**: HSE R2P2 (2001) is the standard reference; cited in references list as Health and Safety Executive (HSE). (2001). *Reducing Risks, Protecting People*. HSE Books.
- **Vrijling et al. (1995)** is the methodological reference for the F-N format itself; already in references list.
- **Two-point curves**: F-N curves with only N=1 and N=2 are mathematically correct given N_max=2 occupants. A reviewer may ask why we don't extrapolate; answer: occupant model bounds maximum fatalities at 2, so F(N≥3) = 0 by construction. Two data points are necessary and sufficient.
- **Comparison with NFPA 855 5×5 matrix**: This F-N presentation provides the quantitative granularity that the NFPA 855 qualitative matrix cannot — a key contribution of this paper.

## Print considerations

- **Single-column figure**: PNG at 300 dpi, ~95 mm wide → scales cleanly
- **Double-column figure**: Preferred for this figure (multiple curves, zone labels); ~190 mm wide
- **Greyscale fallback**: Distinct marker shapes (square/circle/diamond/triangle) ensure scenarios remain distinguishable in B&W; tolerance band shading degrades gracefully

## Version history

| Version | Date | Notes |
|---------|------|-------|
| v1 | 15 May 2026 | Initial rebuild, basic structure |
| v2 | 15 May 2026 | Tightened x-axis, repositioned zone labels |
| v3 | 15 May 2026 | Corrected reduction value from 80.3% to 79.5% (F(N≥1) basis); separated ERL reduction note |
| v4 | 15 May 2026 | Final cleanup: horizontal tolerance line labels with leaders, suppressed minor x-ticks, clean reduction badge |
| v5 | 15 May 2026 | Widened x-axis to N=4 for zone label breathing room. Repositioned zone labels to mid-band y-positions. Added inline annotation explaining "Compartmentation alone: 16% F(N≥1) reduction" near the orange/red cluster (addresses reviewer question about why 1-Comp and 2-Comp Water-only curves nearly overlap). Tolerance line labels repositioned to N=3.0 anchor with leaders to N=2.5 on dashed lines. |

