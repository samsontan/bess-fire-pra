# EQIX SG4-4A Figure 7 — Event Tree Analysis (Staircase Format)

**Manuscript:** Probabilistic Risk Assessment of Grid-Scale Lithium-Ion Battery Energy Storage System Fire Hazards
**Target journal:** Fire and Materials
**Prepared by:** Samson Tan PhD (BOA Reg. No. 1324) | STAARCH Pte Ltd
**Source data:** BESS_Event_Tree.xlsx — Monte Carlo PRA (N = 10,000) | EQIX SG4-4A HMA

---

## Purpose

This figure replaces the jumbled Figure 11 Panel D in the v6 manuscript draft with
an industry-standard event tree presentation following the staircase convention used in
BESS fire literature (Wang et al. 2022; Liao et al. 2020; Bugryniec et al. 2024)
and the canonical orthogonal-branch geometry described in Barry, T.F. (2002),
*Risk-Informed, Performance-Based Industrial Fire Protection*, Fig 2.15 and similar.

The geometry uses **pure horizontal and vertical line segments only** — no diagonal steps.
Each barrier is a single vertical drop at its column position, with YES exiting horizontally
at the parent trunk level and NO continuing as the new trunk below. This produces clean
visual hierarchy where every scenario path can be traced as a sequence of orthogonal moves.

## What changed from the v6 manuscript

- **Topology corrected**: Proper staircase Yes/No branching at each barrier node (BMS → UL 9540A → Suppression), not stacked flow boxes
- **Column headers**: Initiating Event | BMS Detection | UL 9540A Barrier | Suppression (Branch A/B), each with branch probability stated explicitly
- **Branch A and Branch B**: Parallel design alternatives shown at the same node (water-only vs gas+water dual), each with two outcome paths
- **Six scenarios**: Sc.1 (No Propagation), Sc.2 (UL contained), Sc.3A/4A (water-only), Sc.3B/4B (gas+water dual) — matching BESS_Event_Tree.xlsx exactly
- **ERL summary table**: Structured 4-column comparison at the bottom, ALARP classifications, 80.1% ERL reduction badge

## Files in this package

| File | Purpose |
|------|---------|
| `EQIX-SG4-4A_Figure7_EventTree.svg` | Master vector source (editable in Inkscape, Illustrator, or browser) |
| `EQIX-SG4-4A_Figure7_EventTree.png` | Rendered PNG at 2800px width (~300 dpi for A4 landscape print) |
| `generate_figure7.py` | Python regeneration script (re-renders PNG from SVG) |
| `generate_figure7.bat` | Windows launcher (double-click) |
| `generate_figure7.sh` | macOS/Linux launcher (chmod +x then ./generate_figure7.sh) |
| `EQIX-SG4-4A_Figure7_EventTree_Workbook.xlsx` | Excel reconstruction (editable cells + embedded PNG) |

## Regenerating the figure

### Windows
Double-click `generate_figure7.bat`. The script will auto-install cairosvg if needed.

### macOS / Linux
```bash
chmod +x generate_figure7.sh
./generate_figure7.sh
```

Or directly:
```bash
pip install cairosvg
python3 generate_figure7.py
```

## Manuscript integration instructions

In the manuscript v6 PDF (BESS_Fire_Safety_Paper_Q1_revised_v6.pdf):

1. **Replace Figure 7** (page 9) with the PNG in this package
2. **Delete Figure 11 Panel D** (page 24, "Event Tree Comparison" — the boxes-and-arrows flow diagram). Panels A, B, C remain useful and should be kept.
3. **Update Figure 11 caption** to reflect three panels only: A (Annual ERL), B (ERL breakdown by hazard component), C (Individual annual risk)
4. **Update Section 4.5.3** to point readers back to Figure 7 for the event tree comparison: "The event tree comparison (Figure 7, Section 4.3) shows the branching outcomes for water-only (Branch A) and gas+water dual (Branch B) suppression designs..."

## Numerical values (verification)

All values in this figure reconcile exactly with BESS_Event_Tree.xlsx:

| Node | Probability | Calculation |
|------|-------------|-------------|
| Initiating event | 1.50 × 10⁻⁴/yr | P_multi annual (per workbook) |
| BMS YES (Sc.1) | 0.85 | Sc.1 freq = 1.50e-4 × 0.85 = 1.275e-4 |
| BMS NO → UL YES (Sc.2) | 0.15 × 0.92 | Sc.2 freq = 1.50e-4 × 0.15 × 0.92 = 2.07e-5 |
| Suppression node | 1.80 × 10⁻⁶/yr | 1.50e-4 × 0.15 × 0.08 |
| Branch A water YES (Sc.3A) | 0.378 | Mean Monte Carlo effectiveness |
| Branch A water NO (Sc.4A) | 0.622 | 1 − 0.378 |
| Branch B gas+water YES (Sc.3B) | 0.876 | 1 − (0.622 × 0.20) |
| Branch B gas+water NO (Sc.4B) | 0.124 | 0.622 × 0.20 (both fail) |
| ERL Branch A | 1.12 × 10⁻⁶/yr | Sc.4A frequency, worst-case |
| ERL Branch B | 2.23 × 10⁻⁷/yr | Sc.4B frequency, worst-case |
| ERL Reduction | 80.1% | (1.12e-6 − 2.23e-7) / 1.12e-6 |

## Editing the SVG

The SVG can be opened in any modern browser to inspect, or edited in:
- **Inkscape** (free, cross-platform): native SVG editor
- **Adobe Illustrator**: open SVG, edit, save as SVG
- **Affinity Designer**: native SVG support
- **VS Code with SVG Preview extension**: text edit with live preview

After editing, re-run the generator to produce an updated PNG.

## Print considerations

The SVG renders at viewBox 1400 × 720 (aspect ratio 1.94:1). For Fire and Materials:
- **Double-column figure**: PNG at 2800 × 1440 px scales to ~150 mm wide at 300 dpi — fits standard double-column layout
- **Full-width figure**: Acceptable for a complex multi-panel event tree; recommend Editor request for full-width placement
- **Greyscale fallback**: All elements are differentiated by both colour AND position/typography — figure remains legible in B&W print

## Version history

| Version | Date | Notes |
|---------|------|-------|
| v1 | 15 May 2026 | Initial rebuild from BESS_Event_Tree.xlsx; staircase format per Option A reference |
| v2 | 15 May 2026 | Geometry refined to Barry (2002) pure orthogonal H/V style; eliminated all diagonal step segments; YES/NO probability labels moved onto horizontal segments; design alternative shown as labelled badges (A/B) on verticals |
| v3 | 15 May 2026 | Column verticals extended upward to anchor visually to column headers via dashed grey "stems" (per Sam markup); makes column→tree relationship explicit. Active branch segments (red NO drops) remain distinct from structural stems. Legend updated. |
