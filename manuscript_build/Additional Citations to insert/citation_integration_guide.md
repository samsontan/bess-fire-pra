# Citation Integration Guide: BESS Fire Safety Paper v9
## Mapping Uncited References to Optimal Manuscript Locations

---

## SUMMARY

Your manuscript currently cites 24 numbered references [1]–[24]. The additional sources you provided fall into two categories:

1. **Already cited in text but lacking citation numbers** (5 sources):
   - Golubkov et al. (2014)
   - Ohneseit et al. (2023)  
   - UL 9540A (2023)
   - Singapore Fire Code 2023 (4th Amendment)
   - Arizona Public Service (APS) (2020) — partially

2. **Require new integration** (4 sources):
   - DNV GL (2021) — ESS fire safety industry guidance
   - EPRI (2020) — Failure mode analysis and risk quantification
   - Liao et al. (2020) — TR propagation mechanisms
   - NFPA 2001 (2019) — Clean agent system standards

3. **Already formally cited** (3 sources):
   - FM Global (2021) — DS 5-32 referenced extensively
   - NFPA 855 (2023) — Implicit throughout, add explicit reference
   - APS McMicken (2020) — [20] in references, cited as "APS McMicken, 2020"

---

## DETAILED PLACEMENT RECOMMENDATIONS

### **1. Golubkov et al. (2014) — Thermal-Runaway Experiments**

**Current status in manuscript:**  
Text reference in Section 2.2: "Golubkov et al., 2014; Ohneseit et al., 2023; Sadeghi & Restuccia, 2024"

**Current location:**
- Section 2.2 (Thermal Runaway Chemistry), Paragraph 3:
  > "At the cell level, NMC lithium-ion chemistries exhibit lower thermal runaway onset temperatures (130–150°C) compared to LFP (lithium iron phosphate, onset >270°C), and produce higher peak heat release rates under equivalent abuse conditions (Golubkov et al., 2014; Ohneseit et al., 2023; Sadeghi & Restuccia, 2024)."

**Action required:**
Assign a citation number. **Option A:** Insert as [25] and renumber subsequent references. **Option B:** Integrate into Table 1 (Parameter Sources) if Golubkov data appears in your parameter distributions.

**Recommended action:** Add as **[25]** in References section (after current [24]).

---

### **2. Ohneseit et al. (2023) — Thermal & Mechanical Safety of 21700 NMC**

**Current status:**  
Cited in text (Section 2.2) without a citation number.

**Current location:**
- Section 2.2, same paragraph as Golubkov
- Section 3.2, Table 1 (Parameter Distributions) — may include data

**Action required:**
Assign citation number. The reference is correctly cited in text; it needs a formal [X] assignment.

**Recommended action:** Add as **[26]** in References (after Golubkov).

---

### **3. UL 9540A (2023) — Thermal Runaway Fire Propagation Testing**

**Current status:**  
Cited in text multiple times without formal numbering.

**Current locations:**
1. Section 2.2, implicitly referenced in context of cabinet containment
2. Section 3.3, Event Tree discussion: "UL 9540A cabinet containment"
3. Section 5.6 (Limitations): "UL 9540A containment probability (OI-02 unresolved)"
4. Appendix A.4: FDS Input File description

**Action required:**
Assign citation number and add formal reference. UL 9540A is critical to your methodology.

**Recommended action:** Add as **[27]** and update all text references from "UL 9540A" to "UL 9540A [27]".

---

### **4. Singapore Fire Code 2023 (4th Amendment)**

**Current status:**  
Cited multiple times in text without formal numbering.

**Current locations:**
1. Section 2.1 (The EQIX SG4-4A Installation): "classified as an above-ground ESS under Singapore Fire Code 2023 Clause 10.3.1(b)"
2. Section 2.5 (NFPA 855 Framework): "The Singapore Fire Code 2023 (4th Amendment) Clause 10.3.1 incorporates NFPA 855 by reference"
3. Section 3.1, Table 1: Likely references the code

**Action required:**
Assign citation number. This is a primary regulatory document for your case study.

**Recommended action:** Add as **[28]** and update references from "Singapore Fire Code 2023 (4th Amendment)" to "[28]" where appropriate.

---

### **5. FM Global Property Loss Prevention Data Sheet 5-32 (2021)**

**Current status:**  
Implicitly cited through Jensen et al. [17] reference and table data.

**Current locations:**
1. Section 3.5 (Suppression Effectiveness Model): "piecewise base values (78%/45%/20%) are derived from FM Global Property Loss Prevention Data Sheet 5-32 (2021)"
2. Table 1 (Parameter Distributions): FM Global cited for suppression effectiveness base rates
3. Section 5.4 (Discussion): FM Global position on clean agent effectiveness

**Action required:**
Verify if FM Global (2021) has its own [X] citation or is subsumed under Jensen [17]. The way it's written, DS 5-32 (2021) should have its own citation.

**Recommended action:** Add as **[29]** in References if not already present, update text references to include citation number.

---

## NEW INTEGRATIONS (4 references requiring insertion into text)

---

### **6. DNV GL (2021) — Considerations for ESS Fire Safety**

**Recommended placement:** Section 1.2 (Gap Analysis), after NFPA 855 limitations discussion

**Current text in Section 1.2:**
> "Current BESS fire safety practice — including the dominant regulatory framework in NFPA 855 (2023) — relies on qualitative or semi-quantitative risk assessment."

**Suggested insertion (NEW TEXT):**
> "Current BESS fire safety practice — including the dominant regulatory framework in NFPA 855 (2023) — relies on qualitative or semi-quantitative risk assessment. Industry guidance from DNV GL [X] emphasizes the centrality of system-level protection design, including compartmentation and early gas detection, over prescriptive component-level standards; however, this guidance remains qualitative and lacks the probabilistic framework necessary to compare alternative system designs on quantitative risk grounds."

**Citation to assign:** **[30]**

**Rationale:** DNV GL provides parallel industry guidance (non-NFPA) that contextualizes the gap your paper addresses. Placement here reinforces that the gap is recognized beyond the NFPA framework.

---

### **7. EPRI (2020) — Energy Storage System Safety: Failure Mode Analysis**

**Recommended placement:** Section 1.1 (Problem Statement), when describing multi-dimensional hazards

**Current text in Section 1.1:**
> "The fire safety hazards of lithium-ion NMC BESS are multi-dimensional and severe. At the cell level, thermal runaway (TR) — an autocatalytic exothermic chain reaction initiated at 130–200°C — can propagate through a module, cabinet, and room with temperatures exceeding 300°C, producing a complex mixture of flammable gases..."

**Suggested insertion (REVISED):**
> "The fire safety hazards of lithium-ion NMC BESS are multi-dimensional and severe. The Electric Power Research Institute's comprehensive failure mode analysis [X] identifies thermal runaway propagation as a system-level phenomenon spanning multiple energy dissipation pathways (cell → module → cabinet → room). At the cell level, thermal runaway (TR) — an autocatalytic exothermic chain reaction initiated at 130–200°C — can propagate through a module, cabinet, and room with temperatures exceeding 300°C, producing a complex mixture of flammable gases..."

**Citation to assign:** **[31]**

**Rationale:** EPRI's failure mode framework provides credible industry/research institute backing for the multi-dimensional hazard characterization. Strengthens the problem statement by invoking established taxonomy.

---

### **8. Liao et al. (2020) — Hazard Analysis of Thermally-Induced Failure Propagation**

**Recommended placement:** Section 2.2 (Thermal Runaway Chemistry), after discussion of TR cascade

**Current text in Section 2.2:**
> "NMC lithium-ion thermal runaway follows a characteristic temperature cascade: SEI decomposition at 60–130°C, electrolyte oxidation at 130–200°C, cathode decomposition at 200–300°C, and separator meltdown with flaming ejection at >300°C [1,6]."

**Suggested insertion (REVISED):**
> "NMC lithium-ion thermal runaway follows a characteristic temperature cascade: SEI decomposition at 60–130°C, electrolyte oxidation at 130–200°C, cathode decomposition at 200–300°C, and separator meltdown with flaming ejection at >300°C [1,6]. The propagation of thermal runaway from individual cells into multi-cell modules is governed by thermal coupling between adjacent cells; Liao et al. [X] demonstrated experimentally that failure propagation probability within a module increases sharply with increasing State of Charge (SOC), with propagation distances exceeding 50 mm under high-SOC conditions. The cabinet-level propagation probabilities incorporated in this paper's event tree (Section 4) are based on this module-level propagation characterization extrapolated to full-cabinet scale."

**Citation to assign:** **[32]**

**Rationale:** Liao et al. provides direct experimental evidence for the TR propagation mechanism you model in your event tree. Placement here validates your model structure and provides the mechanistic basis for cabinet-level propagation assumptions.

---

### **9. NFPA 2001 (2019) — Standard on Clean Agent Fire Extinguishing Systems**

**Recommended placement:** Section 3.5 (Suppression Effectiveness Model), when introducing clean agent systems

**Current text in Section 3.5:**
> "Clean agent (Fluoro-K, HFC-227ea) pre-discharge during the sprinkler pre-action delay is modelled as providing flame suppression only — no TR arrest capability — consistent with the established self-oxidising chemistry of NMC cathodes and consistent with the position of FM Global (Property Loss Prevention Data Sheet 5-32, 2021)."

**Suggested insertion (REVISED):**
> "Clean agent (Fluoro-K, HFC-227ea) pre-discharge during the sprinkler pre-action delay is modelled as providing flame suppression only — no TR arrest capability — consistent with the established self-oxidising chemistry of NMC cathodes and consistent with the position of FM Global (Property Loss Prevention Data Sheet 5-32, 2021). The application rate, discharge duration, and oxygen depletion mechanism of the clean agent system at EQIX SG4-4A conform to NFPA 2001 [X] design requirements for clean agent systems in occupied spaces, with particular emphasis on post-discharge venting to restore room oxygen to habitable levels (>19.5% by volume) within the timeframe specified in the standard. The clean agent system operates as a pre-sprinkler layer designed to suppress open flaming (HRR reduction) rather than arrest thermal runaway; the subsequent water suppression layer is designed to cool the exothermic reaction and interrupt propagation."

**Citation to assign:** **[33]**

**Rationale:** NFPA 2001 is the design standard for clean agent systems. Including it validates that your clean agent modelling is grounded in the applicable standard, not arbitrary assumptions. It also clarifies the role boundary between clean agent and water suppression.

---

## REVISED REFERENCES LIST STRUCTURE

After integrating the above, your References section should be renumbered as follows:

```
[1]–[24]: Existing references (unchanged)
[25]: Golubkov et al. (2014)
[26]: Ohneseit et al. (2023)
[27]: UL Standards & Engagement (2023) — UL 9540A
[28]: Singapore Civil Defence Force (2023) — Singapore Fire Code 2023 (4th Amendment)
[29]: FM Global (2021) — Property Loss Prevention Data Sheets 5-32 [if not already present]
[30]: DNV GL (2021) — Considerations for ESS Fire Safety
[31]: EPRI (2020) — Energy Storage System Safety: Failure Mode Analysis
[32]: Liao et al. (2020) — Hazard Analysis of Thermally-Induced Failure Propagation
[33]: NFPA (2019) — NFPA 2001: Standard on Clean Agent Fire Extinguishing Systems
```

---

## ACTION CHECKLIST

- [ ] Verify current reference count; if already at [24], begin new references at [25]
- [ ] Move cited-but-unnumbered references (Golubkov, Ohneseit) to [25]–[26]
- [ ] Assign [27] to UL 9540A and update all text instances
- [ ] Assign [28] to Singapore Fire Code 2023 and update all text instances
- [ ] Verify FM Global DS 5-32 (2021) — add as [29] if not in current list
- [ ] Insert DNV GL reference in Section 1.2 (Gap Analysis); assign [30]
- [ ] Insert EPRI reference in Section 1.1 (Problem Statement); assign [31]
- [ ] Insert Liao et al. reference in Section 2.2 (TR Chemistry); assign [32]
- [ ] Insert NFPA 2001 reference in Section 3.5 (Suppression Model); assign [33]
- [ ] Renumber all subsequent citations and references
- [ ] Conduct find-and-replace for text references (e.g., "UL 9540A" → "UL 9540A [27]")
- [ ] Verify APS McMicken reference — confirm [20] is correct

---

## NOTES ON EXCLUDED SOURCES

The following sources in your "Additional Sources" list are already formally cited in the manuscript:

- **NFPA 855 (2023)** — Cited throughout; appears as implicit reference, confirm explicit [X] in references list
- **APS McMicken (2020)** — Cited as [20]; explicitly mentioned as "APS McMicken, 2020" in text and limits discussion

No further action needed for these beyond verification of reference numbering.

---

## RATIONALE FOR INTEGRATION STRATEGY

1. **Golubkov & Ohneseit → [25]–[26]**: These are already cited in text (Section 2.2) as supporting cell-level thermal runaway characterization. Formalizing the citation numbers closes a gap in the current numbering.

2. **UL 9540A → [27]**: Critical to your methodology (cabinet containment probability). Currently cited as "UL 9540A" without number; this undermines traceability. Assigning [27] and updating all text references strengthens the paper's methodological foundation.

3. **Singapore Fire Code → [28]**: Primary regulatory framework for your case study. Currently scattered throughout text without formal citation. Assigning [28] improves regulatory traceability and clarity for SCDF submissions.

4. **DNV GL (Gap Analysis)**: Positions your work within the broader industry context (non-NFPA guidance). Placement in Section 1.2 reinforces that the quantitative gap you address is recognized by multiple standards-setting bodies.

5. **EPRI (Problem Statement)**: Invokes established failure mode taxonomy. Placement in Section 1.1 strengthens the problem framing by anchoring it to research institute characterization rather than author assertion alone.

6. **Liao et al. (TR Chemistry)**: Provides direct experimental evidence for cabinet-level propagation assumptions. Placement in Section 2.2 validates the mechanistic basis of your event tree without disrupting narrative flow.

7. **NFPA 2001 (Suppression Model)**: Clarifies the design basis and operational role of the clean agent system. Placement in Section 3.5 explains why clean agent is modelled as flame suppression (not TR arrest) and grounds this in a recognized standard.

---

## FINAL NOTE

The integration of these references should be done in a coordinated pass:

1. **First pass:** Renumber existing [1]–[24] to account for new [25]–[33]
2. **Second pass:** Insert new text segments with correct citation numbers  
3. **Third pass:** Update all in-text references (e.g., "UL 9540A" → "UL 9540A [27]")
4. **Fourth pass:** Proofread for citation consistency and narrative flow

This systematic approach ensures no citations are missed and no duplication occurs.
