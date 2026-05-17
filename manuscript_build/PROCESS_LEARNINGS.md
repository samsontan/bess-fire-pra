# BESS Fire Safety Paper -- Manuscript Process Learnings

**Prepared**: 2026-05-17
**Author**: Claude Code (Lily) with Samson Tan
**Purpose**: Capture everything hard-won in building this manuscript so the next FDS + Event Tree paper goes faster.

---

## Executive Summary

This paper took approximately 3 weeks of AI-assisted work across multiple Claude Code sessions. The final v11 manuscript is publication-quality. The journey involved:

- A full NIST FDS CFD simulation (600 s, 2-mesh MPI)
- 9 publication figures generated from FDS binary slice files
- A custom event tree (Fig 7) built iteratively with matplotlib
- FN curve (Fig 13) built in Excel and Python
- Monte Carlo PRA (N=10,000) in Python
- 33 SciSpace-verified references, numbered by order of appearance
- Figure renumbering across a 22-figure manuscript without destroying captions
- Tracked change stripping without destroying document structure
- Author block rebuild with proper superscript affiliations
- PDF export via Word COM

The key insight: **each step of this pipeline is now documented and reusable**. The next paper should take 30-40% less effort because all the tools, bugs, and patterns are captured.

---

## Phase 1: FDS CFD Simulation

### What we did
- Designed a 7.50 x 5.00 x 3.00 m BESS room with 7 NMC battery cabinets
- Ran a 600 s thermal runaway fire simulation with HF and H2 species
- Generated 9 publication PNGs from binary slice (.sf) files

### Critical bugs encountered

**Bug 1: Cabinet row placed against south wall**
- Initial geometry had cabinets at Y=0.10-1.00 m (touching the wall)
- This produced unrealistic plume behaviour and made the aisle inaccessible
- Fix: Move to Y=2.00-2.90 m (centred in room, realistic 1 m clearance each side)
- Lesson: Always check cabinet geometry against room dimensions manually before running

**Bug 2: VENT on mesh boundary (X=3.70 m)**
- Fire VENT placed exactly on mesh split boundary
- FDS trims geometry at mesh boundaries -- fire VENT was halved silently
- Fix: Move VENT at least one cell (0.15 m) away from boundary
- Lesson: Never place any VENT or OBST edge exactly on a mesh split line

**Bug 3: fdsreader frame count bug**
- fdsreader (Python library) caches frame count when run is first opened
- After completion it reported 16 frames when there were 61
- Fix: Use direct binary reader (`_read_sf_file()`) bypassing fdsreader entirely
- Lesson: Never use `fds_reader.slices[n].get_data()` on a completed run without checking frame count

**Bug 4: PBY slice inside cabinet solid**
- `SLCF PBY=2.50` sliced through the cabinet interior (Y=2.00-2.90 = cabinet body)
- The plot showed solid black (all zeros -- inside obstruction)
- Fix: Move to PBY=1.50 (south aisle, 0.50 m in front of cabinet south face)
- Lesson: Always verify slice plane coordinates against OBST coordinates before interpreting figures

### What worked well
- 2-mesh MPI with `mpiexec -n 2` ran in ~2 hours for 600 s simulation
- Direct binary `.sf` reader is reliable and fast
- 5-panel time sequence plots (t=120, 240, 360, 480, 600 s) tell the story clearly
- Separate plots for BZ plan (Z=1.50 m) and ceiling (Z=2.70 m) are essential for stratification

---

## Phase 2: Event Tree (Fig 7)

### What we did
- Designed a 4-branch event tree comparing Design A (gas+water) vs Design B (water-only)
- Each branch has initiating event, 4 probability nodes, 2 outcomes (fire/no fire)
- ERL calculated for each design, ratio = 80.3% reduction

### Critical bugs encountered

**Bug 1: NO label placement**
- NO branch labels were placed at the same Y as YES labels
- They overlapped with the branch lines
- Fix: Offset NO labels upward by 0.35 units above the branch line midpoint
- Lesson: For event trees, YES label goes below the upper branch; NO label goes ABOVE the lower branch

**Bug 2: Initiating Event box too narrow**
- IE box width was set equal to first tree column width
- This made the IE label overflow the box
- Fix: Set IE box width to 1.5x first column, add text wrap with `\n`
- Lesson: Always render a test figure and check text overflow before finalising

**Bug 3: Barry format reference**
- The first event tree used a non-standard format
- Barry's textbook format requires: horizontal top spine, vertical drops at each node, horizontal branch lines
- Fix: Rebuild entire figure following Barry's Risk-Informed, Performance-Based Industrial Fire Protection (Fig reference from book)
- Lesson: Have a reference figure from Barry before starting any event tree

### What worked well
- matplotlib with explicit coordinate calculation is controllable and reproducible
- Saving workbook data (XLSX) alongside the PNG allows easy recalculation
- The `generate_figure7.py` script is self-contained and runnable without a Claude session

---

## Phase 3: PRA Monte Carlo

### What worked
- `pra_simulation.py` with N=10,000 iterations is fast (~30 seconds)
- JSON output files allow figures to be regenerated without re-running simulation
- Sensitivity analysis (tornado chart) immediately shows which parameters drive risk

### Lessons
- Always save MC raw data to JSON before generating figures -- regeneration is fast, re-running is not
- Use `scipy.stats` distributions (lognormal, beta, uniform) to match literature parameterisation
- Document all input parameter sources in the paper (Section 3) -- reviewers will ask

---

## Phase 4: Manuscript Building (python-docx Pipeline)

### The pipeline (v9 -> v10 -> v11)

```
v9_base.docx
  → finalize_manuscript_v9.py   (figure renumbering + FDS image white-outs + event tree v4)
  → BESS_Fire_Safety_Paper_Q1_revised_v9.docx
  → build_v10_citations.py       (19 citation insertions + reference renumbering + remove old section)
  → BESS_Fire_Safety_Paper_Q1_revised_v10.docx
  → [Sam's manual edits]         (THORisk [23], DS 5-33, key distinctions text)
  → BESS_Fire_Safety_Paper_Draft_260517.docx  (ground truth)
  → save_as_v11.py               (copy + PDF export)
  → BESS_Fire_Safety_Paper_Q1_revised_v11.docx + v11.pdf
```

Also:
```
v10.docx
  → prepare_bess_draft_for_reviewers.py  (tracked change strip + (EN) removal + 4-author block + PDF)
  → Manuscript Draft to Khalid and Paul - 2026-05-17\BESS_Fire_Safety_Paper_Draft_260517.docx
```

### Critical bugs encountered

**Bug 1: Caption corruption from generic text replacement**
- Replacement tuple `('Figure 4', 'Figure 3')` matched caption lines as well as body text
- Result: Caption "Figure 4: ..." became "Figure 3: ..." corrupting the caption numbering
- Fix: Add caption guard before all replacements:
  ```python
  IS_CAPTION = re.compile(r'^Figure \d+[:\.]', re.IGNORECASE)
  if IS_CAPTION.match(para.text.strip()): continue
  ```
- Lesson: ALWAYS add caption guard. Generic figure number replacements are dangerous.

**Bug 2: Tracked changes still showing after COM AcceptAllRevisions**
- Word COM's AcceptAllRevisions() failed silently for some document states
- The sidebar still showed grey revision marks even after the call
- Fix: Strip tracked changes directly from the ZIP XML using lxml (see memory.md for code)
- Lesson: Never rely on COM for tracked change stripping -- use lxml directly

**Bug 3: PermissionError WinError 32 on destination file**
- First script run crashed mid-way, leaving destination docx locked by Word
- Next run: PermissionError trying to overwrite
- Fix: Always run `taskkill /F /IM WINWORD.EXE` before any COM call; write to temp then copy
- Lesson: Put taskkill at top of every script that uses COM

**Bug 4: ValueError in paragraphs.index()**
- `doc.paragraphs.index(author_para)` raised ValueError
- The paragraph object from scanning was not the same instance as in doc.paragraphs
- Fix: Track positional index during scanning (`author_idx = i`) and use `paras[author_idx]` directly
- Lesson: Never call `.index()` on python-docx paragraph lists -- track indices during your own scan

**Bug 5: Cross-run text mismatch**
- A phrase like "[25]" was split across two runs in the XML: "[" in run[0], "25]" in run[1]
- Simple `run.text.replace()` only checked run by run -- missed split phrases
- Fix: Concatenate all run text, replace in combined string, rebuild runs[0] with full text, clear runs[1:]
- Lesson: ALWAYS use the cross-run replacement pattern (see memory.md)

**Bug 6: Tables missing from paragraph scan**
- References in table cells were not matched by the replacement loop
- `doc.paragraphs` does NOT include table cell paragraphs
- Fix: Use `all_paragraphs(doc)` iterator that yields body + table cell paragraphs
- Lesson: ALWAYS use all_paragraphs() iterator, never doc.paragraphs alone

### What worked well
- Dry-run flag (`DRY_RUN = '--execute' not in sys.argv`) saved from many mistakes
- Verification block (print first 12 paragraphs after save) catches corruption immediately
- Numbering citations by order-of-appearance (not alphabetical) is standard for this journal
- The 19-replacement list in build_v10_citations.py is a good pattern: explicit, auditable

---

## Phase 5: Reference Management

### What we did
- Started with an unnumbered "Additional Sources" section
- Inserted 9 new citations ([25]-[33]) at precise points in the text
- Deleted the old unnumbered section
- Verified all 33 references are sequential and correctly placed

### Lessons

**SciSpace verification is essential**: SciSpace found that our reference for FM Global was for DS 5-32 (Pumping Equipment) not DS 5-33 (BESS). This would have been a reviewer red flag. Always run SciSpace verification before any submission.

**Citation insertion order matters**: Citations must be inserted from LAST to FIRST in the document. If you insert [25] first, [26] next, etc., the paragraph indices shift and you corrupt the order. Work backwards through the document.

**The "ground truth" problem**: Sam made manual edits to the review draft (THORisk [23], DS 5-33, key distinctions). These edits were superior to what any script could produce. Always treat Sam's manually edited file as ground truth and work forward from it, not backward.

---

## Phase 6: Review Draft Preparation

### What we did
- Stripped tracked changes from v10
- Removed (EN) suffixes from section headings (artifact from multi-language template)
- Rebuilt author block to 4-author format with superscript affiliations
- Removed ORCID and Correspondence lines (not needed for reviewer draft)
- Created email draft document (Word) with full project context for co-authors
- Sent draft + email via Outlook

### Lessons

**The (EN) labels**: These came from a multi-language Word template. They are not visible in print but appear in the XML as part of the heading text. Always check for and remove these in the final draft.

**Reviewer-facing vs canonical**: The reviewer copy (Draft_260517.docx) intentionally has no ORCID, no correspondence email, and a simplified header. The canonical v11.docx retains these for internal tracking. Maintain this distinction.

**Email context matters**: Khalid and Paul are academics and co-authors, not clients. The email explained (a) why the paper exists, (b) the FM Global tension, (c) the NMC/LFP regulatory challenge, (d) the SCDF context. This level of context enables them to give useful technical review rather than just copyediting.

---

## Template for Future Fire Engineering Papers

Based on this experience, here is the recommended workflow for the next FDS + event tree paper:

### Pre-work (before writing)
1. Confirm room geometry and fire scenario parameters
2. Write event tree structure (Barry format) before any Python code
3. Set up FDS model with validation geometry (T_END=10 first)
4. Run PRA Monte Carlo simulation and save results to JSON

### Writing phase
1. Write paper body in Markdown first (easier to edit than Word)
2. Convert to Word (.docx) with pandoc or python-docx
3. Insert analytical figures first (fig1-fig13), verify numbering
4. Insert CFD figures last (fig14+), verify numbering
5. Add references in order of appearance as you write (not at end)

### Finalisation phase
1. Run SciSpace verification on all references
2. Insert/correct citations with build script (dry-run first)
3. Generate clean copy: strip tracked changes, fix headings, rebuild author block
4. PDF export via Word COM
5. Create reviewer copy and email

### Scripts to have ready (copy from this paper's 08_MANUSCRIPT_Build-Scripts\)
- `finalize_manuscript_vN.py` -- figure renumbering + image processing
- `build_vN_citations.py` -- citation insertion + reference reordering
- `prepare_draft_for_reviewers.py` -- tracked change strip + author block + PDF
- `save_as_vN.py` -- copy canonical + PDF export

---

## Time Estimate for Next Paper (with these tools)

| Phase | This paper | Next paper (estimated) |
|-------|-----------|----------------------|
| FDS model setup + run | 3 days | 1 day (copy eqix_preview.fds, adapt) |
| FDS post-processing + 9 figures | 2 days | 4 hours (fds_postprocess_bess.py ready) |
| Event tree (Fig 7) | 2 days | 2 hours (generate_figure7.py ready) |
| PRA Monte Carlo | 2 days | 1 day (pra_simulation.py ready) |
| Manuscript writing | 5 days | 3 days |
| Manuscript build pipeline | 3 days | 4 hours (scripts ready) |
| Reference management | 1 day | 4 hours |
| Review draft prep | 1 day | 1 hour |
| **Total** | **~19 days** | **~7 days** |

---

## Reusable Assets (copy these for next paper)

| Asset | Location | What to change |
|-------|----------|---------------|
| FDS input | `05_FDS_CFD-Simulation\input\eqix_preview.fds` | Room geometry, CHID, cabinet positions |
| FDS post-processor | `05_FDS_CFD-Simulation\scripts\fds_postprocess_bess.py` | FIGS_DIR, CHID, species, thresholds |
| FDS launch script | `05_FDS_CFD-Simulation\scripts\launch_preview.py` | RUN_DIR, CHID |
| Event tree generator | `11_FIGURE_DEVELOPMENT_EventTree-FNCurve\Eqix_Event_tree_Fig7_opus4.7\EQIX_SG44A_Figure7_EventTree_Package\generate_figure7.py` | Branch probabilities, labels |
| FN curve generator | `11_FIGURE_DEVELOPMENT_EventTree-FNCurve\Eqix_FNCurve_Fig13_Final_260515\EQIX_SG44A_Figure13_FNCurves\generate_figure13.py` | FN data, ALARP thresholds |
| PRA simulation | `02_PRA_Monte-Carlo-Simulation-Scripts\pra_simulation.py` | TR frequency, HF parameters |
| Manuscript build | `08_MANUSCRIPT_Build-Scripts\*.py` | Paths, replacement tuples, author block |

---

## The Single Most Important Lesson

**Document Sam's manual edits as ground truth immediately.**

When Sam edits a file manually and says "this is now the ground truth", capture it as a new named version (v11, in this case) and work forward from it. Never try to reconstruct manual edits by running scripts on an older base. The manual edit contains judgment that no script can reproduce.
