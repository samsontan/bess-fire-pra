---
tags: [domain-knowledge, BESS, fire-safety, battery, thermal-runaway, HF, NMC, LFP]
date: 2026-05-17
---

# BESS Fire Safety -- Domain Knowledge

## Battery Chemistry

| Parameter | NMC | LFP |
|-----------|-----|-----|
| TR onset temperature | 130-150 C | >270 C |
| HF yield | 0.020 kg/kg (Golubkov 2014) | Lower (phosphate, not fluoride) |
| Energy density | Higher | Lower |
| Market status | Legacy fleet (pre-2022) | Preferred for new builds (>85% utility-scale 2024) |
| Data centre UPS | Schneider Galaxy LBF, Eaton 9PX, Vertiv Liebert EXL -- all NMC | CATL TENER Stack (9 MWh/unit) |

Equinix does NOT publicly disclose battery chemistry per facility.
NMC legacy fleet remains in service until ~2033-2036 (10-15 yr replacement cycles).

## Thermal Runaway (TR) Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| HF yield (NMC, per kg battery) | 0.020 kg/kg | Golubkov et al. (2014) |
| H2 yield | 0.010 kg/kg | Literature average |
| TR initiating event frequency | See NFPA 855 Annex C | NFPA 855 (2023) |
| IDLH (HF) | 30 ppm = 2.46 x 10^-5 mass fraction | NIOSH |
| STEL (HF) | 3 ppm (ACGIH ceiling) | |
| LFL (H2) | 4% v/v = 2.88 x 10^-3 mass fraction | |
| HF mass fraction at IDLH | 30e-6 * 20.01/28.97 = 2.07 x 10^-5 | Calculated |

## Regulatory Framework (Singapore)

| Requirement | Regulation |
|-------------|-----------|
| BESS Level 5 (>480 kWh in URA category) | SCDF Fire Code + NFPA 855 |
| Prior approval pathway | NFPA 855 Exception (1) |
| HMA report required | Yes |
| SCDF informal preference | LFP chemistry (higher TR onset) |
| FM Global prescription | DS 5-33: water suppression only |

## FM Global DS 5-33 vs DS 5-32

**IMPORTANT**: The relevant FM Global data sheet for BESS is:
- **DS 5-33**: Electrical Energy Storage Systems -- prescribes water as primary suppression medium
- DS 5-32: Pumping Equipment -- NOT relevant to BESS

Always cite DS 5-33, not DS 5-32.

## Suppression Effectiveness

| System | Effectiveness (NMC) | Notes |
|--------|--------------------|----|
| Water mist | 37.9% mean (Monte Carlo) | Per FM Global DS 5-33 range |
| Clean agent (HFC-227ea) | 25-35% (gas phase only) | Does not penetrate cell, only controls surface fire |
| Gas + Water (two-stage) | Cumulative reduction 80.3% ERL | This paper's result |

Key finding: Clean agent alone is insufficient for NMC. Water is necessary.
Two-stage (gas+water) is justified when: gas suppresses surface ignition, water prevents propagation.

## ALARP Framework (UK HSE R2P2 2001)

| Band | Annual ERL | Action |
|------|-----------|--------|
| Intolerable | > 1e-4 | Must reduce regardless of cost |
| ALARP tolerable | 1e-4 to 1e-6 | Reduce until SFAIRP |
| Broadly acceptable | < 1e-6 | No further action required |

EQIX SG4-4A results:
- Water-only (Design B): ERL = 1.22 x 10^-4 (ALARP tolerable boundary)
- Gas+Water (Design A): ERL = 2.40 x 10^-5 (broadly acceptable)

## FDS CFD Key Parameters (BESS Room)

| Parameter | Value |
|-----------|-------|
| Room | 7.50 x 5.00 x 3.00 m |
| Cabinet row | Y=2.00-2.90 m (7 cabinets) |
| Fire source | CAB-4 south face, X=2.90-3.70 m |
| HRR ramp | 0->300 kW over 60->300 s |
| HF at IDLH | t~120 s from TR onset (FDS result) |
| Ventilation | 3 ACH mechanical extract |
