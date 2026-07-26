"""
BESS Fire Safety Probabilistic Risk Assessment — Monte Carlo Simulation
Comparing 1-compartment vs 2-compartment designs for EQIX SG4-4A installation
"""

import os
import sys

# The console summary below contains non-ASCII characters. A Windows console
# defaulting to cp1252 would abort with UnicodeEncodeError, so make stdout
# capable of encoding them wherever the interpreter allows it.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
import numpy as np
import json

np.random.seed(42)
N = 10_000  # Monte Carlo iterations

# ─────────────────────────────────────────────
# INSTALLATION PARAMETERS (EQIX SG4-4A)
# ─────────────────────────────────────────────
total_kWh   = 485.52
cabinet_kWh = 34.68
n_cabinets  = 14
n_compartments = 2

comp1_kWh = total_kWh / n_compartments          # 242.76 kWh per compartment
comp2_kWh = comp1_kWh                            # same for 2-compartment design
single_comp_kWh = total_kWh                       # 485.52 kWh if un-compartmented

compartment_volume_m3  = 116.0                   # from HMA
ceiling_height_m       = 3.0
floor_area_m2          = compartment_volume_m3 / ceiling_height_m  # ~38.7 m²
ventilation_rate_ach   = 9.0                    # Stage 1 purging: 9 ACH
room_length_m          = np.sqrt(floor_area_m2) # ~6.22 m (assumed square)
room_width_m           = room_length_m

# ─────────────────────────────────────────────
# PROBABILITY DISTRIBUTIONS
# ─────────────────────────────────────────────

# State of Charge (%) — uniform between 90 and 100 for operational BESS
SOC = np.random.uniform(90, 100, N)

# HF yield (g/kWh) — triangular distribution from literature: 0.3–0.8 g/kWh, mode 0.5
HF_YIELD = np.random.triangular(0.3, 0.5, 0.8, N)

# Ventilation activation time (seconds) — lognormal: median 90s, 95th %ile ~300s
# Log-normal: mean=ln(90), std=0.8
VENT_DELAY_S = np.random.lognormal(mean=np.log(90), sigma=0.8, size=N)

# BMS failure probability (per thermal runaway initiating event)
# NFPA 855 Annex C cell-level TR with BMS: ~1×10⁻⁴ per cell-year
# For 7 cabinets × 96 cells = 672 cells, per-year ≈ 0.067
# Over 1-year analysis period, P(BMS fails | TR initiates) ≈ 0.15 (expert elicitation)
BMS_FAILURE_PROB = 0.15

# UL 9540A containment: Schneider Electric Galaxy LBF — pass rate ~0.92 (industry avg for open rack)
# This means P(cabinet-to-cabinet | TR in one cabinet) = 1 - 0.92 = 0.08
UL9540A_CONTAINMENT = 0.92

# Suppression effectiveness: water applied to NMC TR
# Literature: P(arrest TR | water applied within 3 min) ≈ 0.78
# P(arrest TR | water applied 3–10 min) ≈ 0.45
# P(arrest TR | water applied > 10 min) ≈ 0.20
SUPPRESSION_BASE = 0.78

# Suppression delay (minutes) — includes detection + response + system activation
# Pre-action sprinkler with fire department response
SUPPRESSION_DELAY_MIN = np.random.lognormal(mean=np.log(8), sigma=0.6, size=N)
SUPPRESSION_DELAY_MIN = np.clip(SUPPRESSION_DELAY_MIN, 1, 45)

def suppression_effectiveness(delay_min):
    """Piecewise effectiveness based on delay"""
    eff = np.where(delay_min <= 3, 0.78,
           np.where(delay_min <= 10, 0.45,
                    0.20))
    # Add ±10% random variation
    eff = eff * np.random.uniform(0.90, 1.10, len(eff))
    return np.clip(eff, 0.0, 1.0)

# ─────────────────────────────────────────────
# SIMULATION 1: HF GAS DOSE TO OCCUPANT
# ─────────────────────────────────────────────

# Occupant at room centre, 1.5m height (breathing zone)
# Simple well-mixed box model:
#   C_HF(t) = (q_HF × t) / (V × ACH × t/3600)  [simplified, ignores decay]
# More accurate: C_HF = m_HF_gen / (V_air + Q × t)
# HF toxicity: NIOSH IDLH = 25 mg/m³ (≈ 30 ppm by vol at 25°C)

IDLH_HF_mg_m3 = 25.0  # mg/m³ (NIOSH IDLH ≈ 25 mg/m³)
IDLH_HF_ppm   = 30.0  # ppmv at 25°C, 1 atm (for reference)

# Generate per-compartment HF mass (g)
m_HF_1comp = single_comp_kWh * HF_YIELD          # 1-compartment: full 485 kWh
m_HF_2comp  = comp1_kWh * HF_YIELD                # 2-compartment: 242 kWh per comp

# Time to IDLH (s) for each scenario — ventilation ON (9 ACH)
# Using: C(t) = m / (V × (1 - exp(-Q*t/V)) )
# For large t: C ≈ q / Q where q = m/t_gen  (pseudo-steady state)
# Here we compute: time to reach IDLH concentration in breathing zone
# Simplified: m_HF / (V * IDLH_conc) * 1000 mg/g / (1 g/mg) 

air_volume_m3   = compartment_volume_m3
Q_m3_s_9ach     = (9.0 / 3600) * air_volume_m3   # m³/s at 9 ACH

# Time to reach IDLH if HF is released instantaneously (worst case)
t_to_IDLH_1comp_s = (m_HF_1comp * 1000) / (Q_m3_s_9ach * IDLH_HF_mg_m3)
t_to_IDLH_2comp_s = (m_HF_2comp * 1000) / (Q_m3_s_9ach * IDLH_HF_mg_m3)

# Time to IDLH if ventilation is delayed (VENT_DELAY_S)
# HF accumulates during delay, then dilution begins
m_HF_accumulated_1comp = m_HF_1comp * (VENT_DELAY_S / 600)  # fraction released in delay period
m_HF_accumulated_2comp = m_HF_2comp * (VENT_DELAY_S / 600)

# Effective IDLH time including delay
t_IDLH_effective_1comp = t_to_IDLH_1comp_s + VENT_DELAY_S
t_IDLH_effective_2comp = t_to_IDLH_2comp_s + VENT_DELAY_S

print("=" * 60)
print("SIMULATION 1: TIME TO HF IDLH CONCENTRATION")
print("=" * 60)
print(f"\n1-Compartment Design (485.52 kWh):")
print(f"  Mean time to IDLH: {np.mean(t_IDLH_effective_1comp):.1f} s ({np.mean(t_IDLH_effective_1comp)/60:.2f} min)")
print(f"  5th percentile:   {np.percentile(t_IDLH_effective_1comp, 5):.1f} s ({np.percentile(t_IDLH_effective_1comp, 5)/60:.2f} min)")
print(f"  50th percentile:  {np.percentile(t_IDLH_effective_1comp, 50):.1f} s ({np.percentile(t_IDLH_effective_1comp, 50)/60:.2f} min)")
print(f"  95th percentile: {np.percentile(t_IDLH_effective_1comp, 95):.1f} s ({np.percentile(t_IDLH_effective_1comp, 95)/60:.2f} min)")
print(f"  P(IDLH exceeded within 5 min): {np.mean(t_IDLH_effective_1comp < 300)*100:.1f}%")

print(f"\n2-Compartment Design (242.76 kWh per compartment):")
print(f"  Mean time to IDLH: {np.mean(t_IDLH_effective_2comp):.1f} s ({np.mean(t_IDLH_effective_2comp)/60:.2f} min)")
print(f"  5th percentile:   {np.percentile(t_IDLH_effective_2comp, 5):.1f} s ({np.percentile(t_IDLH_effective_2comp, 5)/60:.2f} min)")
print(f"  50th percentile:  {np.percentile(t_IDLH_effective_2comp, 50):.1f} s ({np.percentile(t_IDLH_effective_2comp, 50)/60:.2f} min)")
print(f"  95th percentile: {np.percentile(t_IDLH_effective_2comp, 95):.1f} s ({np.percentile(t_IDLH_effective_2comp, 95)/60:.2f} min)")
print(f"  P(IDLH exceeded within 5 min): {np.mean(t_IDLH_effective_2comp < 300)*100:.1f}%")

print(f"\n2-compartment improvement:")
print(f"  Mean IDLH time extended by: {np.mean(t_IDLH_effective_1comp) - np.mean(t_IDLH_effective_2comp):.1f} s ({(np.mean(t_IDLH_effective_1comp) - np.mean(t_IDLH_effective_2comp))/60:.2f} min)")
print(f"  Risk reduction: {(1 - np.mean(t_IDLH_effective_2comp)/np.mean(t_IDLH_effective_1comp))*100:.1f}%")

# ─────────────────────────────────────────────
# SIMULATION 2: PROBABILITY OF CABINET-TO-CABINET PROPAGATION
# ─────────────────────────────────────────────

# Event tree:
# TR initiates in Cabinet A
#   -> BMS detects + isolates: P(suppress) = 0.85
#   -> BMS fails: TR propagates within cabinet
#       -> UL 9540A containment (cabinet A -> B): P(contained) = 0.92
#           -> Fire develops in 2 cabinets: P(develops | TR+no BMS+no UL) = 0.08

P_TR_initiates = 0.01    # Annual probability of TR initiating in a cabinet (literature estimate)
P_BMS_works    = 1 - BMS_FAILURE_PROB  # 0.85
P_UL9540A_pass = UL9540A_CONTAINMENT    # 0.92

# P(multi-cabinet fire) = P(TR) × P(BMS fails) × P(UL 9540A fail)
P_multi_cabinet_1comp = P_TR_initiates * (1 - P_BMS_works) * (1 - P_UL9540A_pass)
P_multi_cabinet_2comp = P_multi_cabinet_1comp  # per compartment; 2-compartment has 2x independent cabinets

# Expected annual losses (qualitative risk index)
# Risk Index = P(event) × Consequence Severity (1-5 scale)
CONSEQUENCE_CATASTROPHIC = 5.0
CONSEQUENCE_MAJOR = 4.0
CONSEQUENCE_MODERATE = 3.0

risk_1comp = P_multi_cabinet_1comp * CONSEQUENCE_CATASTROPHIC
risk_2comp = P_multi_cabinet_2comp * CONSEQUENCE_MAJOR  # 2-compartment reduces max consequence

print("\n" + "=" * 60)
print("SIMULATION 2: CABINET-TO-CABINET PROPAGATION PROBABILITY")
print("=" * 60)
print(f"\nAssumptions:")
print(f"  P(TR initiating in a cabinet, per year): {P_TR_initiates}")
print(f"  P(BMS working | TR): {P_BMS_works:.2f}")
print(f"  P(UL 9540A containment | BMS fails): {P_UL9540A_pass:.2f}")
print(f"\n  P(multi-cabinet fire, per compartment-year):")
print(f"    1-compartment design: {P_multi_cabinet_1comp:.5f} ({P_multi_cabinet_1comp*1000:.3f} per 1000 cabinet-years)")
print(f"    2-compartment design: {P_multi_cabinet_2comp:.5f} (same per compartment)")
print(f"\n  Expected Risk Index (P × Consequence):")
print(f"    1-compartment: {risk_1comp:.4f} (assumes full 485 kWh consequence = C5)")
print(f"    2-compartment: {risk_2comp:.4f} (max 242 kWh per event = C4, consequence reduced)")

# ─────────────────────────────────────────────
# SIMULATION 3: SUPPRESSION EFFECTIVENESS
# ─────────────────────────────────────────────

suppression_eff = suppression_effectiveness(SUPPRESSION_DELAY_MIN)

# P(TR arrested before full compartment fire) = P(suppression effective | TR propagates)
P_arrest_given_TR = np.mean(suppression_eff)

# Combined: P(full compartment fire) = P(TR) × P(BMS fails) × P(UL fails) × P(suppression fails)
P_supp_fails = 1 - P_arrest_given_TR
P_full_comp_fire_1comp = P_TR_initiates * (1 - P_BMS_works) * (1 - P_UL9540A_pass) * P_supp_fails
P_full_comp_fire_2comp = P_full_comp_fire_1comp  # per compartment

print("\n" + "=" * 60)
print("SIMULATION 3: SUPPRESSION EFFECTIVENESS")
print("=" * 60)
print(f"\nSuppression effectiveness given TR propagates:")
print(f"  Mean effectiveness: {P_arrest_given_TR:.1%}")
print(f"  Median suppression delay: {np.median(SUPPRESSION_DELAY_MIN):.1f} min")
print(f"  5th percentile delay: {np.percentile(SUPPRESSION_DELAY_MIN, 5):.1f} min")
print(f"  95th percentile delay: {np.percentile(SUPPRESSION_DELAY_MIN, 95):.1f} min")
print(f"\n  P(full compartment fire, per compartment-year):")
print(f"    1-compartment: {P_full_comp_fire_1comp:.6f}")
print(f"    2-compartment: {P_full_comp_fire_2comp:.6f}")
print(f"  Risk Index (P × C4):")
print(f"    1-compartment: {P_full_comp_fire_1comp * CONSEQUENCE_MAJOR:.6f}")
print(f"    2-compartment: {P_full_comp_fire_2comp * CONSEQUENCE_MODERATE:.6f}")

# ─────────────────────────────────────────────
# SIMULATION 4: HF DOSE TO OCCUPANT (per event)
# ─────────────────────────────────────────────

# Assumptions: firefighter enters after gas detection + ventilation fails
# Exposure duration = 10 minutes (typical fire response)
EXPOSURE_MIN = 10

# Dose (mg·s/m³) = integral of concentration over time
# Simplified: avg conc = m_HF / (V + Q×t), dose = avg_conc × t × 60
def HF_dose_mgsm3(m_HF_g, delay_s, exposure_min, Q_m3_s, V_m3):
    # Concentration at time t: C(t) = m / (V + Q*t)  [well-mixed box, continuous source]
    # Integrate from t=delay to t=delay+exposure
    t1 = delay_s
    t2 = delay_s + exposure_min * 60
    # Integral of m/(V+Qt) dt = (m/Q) * ln((V+Qt)/Q)
    if Q_m3_s < 1e-6:
        return 1e9  # essentially no ventilation
    integral = (m_HF_g * 1000 / Q_m3_s) * np.log((V_m3 + Q_m3_s * t2) / (V_m3 + Q_m3_s * t1))
    dose = integral / (exposure_min * 60)  # average mg/m³ over exposure
    return dose

dose_1comp = HF_dose_mgsm3(m_HF_1comp, VENT_DELAY_S, EXPOSURE_MIN, Q_m3_s_9ach, air_volume_m3)
dose_2comp = HF_dose_mgsm3(m_HF_2comp, VENT_DELAY_S, EXPOSURE_MIN, Q_m3_s_9ach, air_volume_m3)

print("\n" + "=" * 60)
print("SIMULATION 4: HF DOSE TO OCCUPANT (mg/m³, 10-min exposure)")
print("=" * 60)
print(f"\n1-Compartment Design (485.52 kWh):")
print(f"  Mean dose: {np.mean(dose_1comp):.2f} mg/m³")
print(f"  Median dose: {np.median(dose_1comp):.2f} mg/m³")
print(f"  P(dose > IDLH 25 mg/m³): {np.mean(dose_1comp > IDLH_HF_mg_m3)*100:.1f}%")
print(f"  P(dose > 5× IDLH): {np.mean(dose_1comp > 5*IDLH_HF_mg_m3)*100:.1f}%")
print(f"  P(dose > 10× IDLH): {np.mean(dose_1comp > 10*IDLH_HF_mg_m3)*100:.1f}%")

print(f"\n2-Compartment Design (242.76 kWh):")
print(f"  Mean dose: {np.mean(dose_2comp):.2f} mg/m³")
print(f"  Median dose: {np.median(dose_2comp):.2f} mg/m³")
print(f"  P(dose > IDLH 25 mg/m³): {np.mean(dose_2comp > IDLH_HF_mg_m3)*100:.1f}%")
print(f"  P(dose > 5× IDLH): {np.mean(dose_2comp > 5*IDLH_HF_mg_m3)*100:.1f}%")
print(f"  P(dose > 10× IDLH): {np.mean(dose_2comp > 10*IDLH_HF_mg_m3)*100:.1f}%")

dose_reduction = (np.mean(dose_1comp) - np.mean(dose_2comp)) / np.mean(dose_1comp) * 100
print(f"\n  HF dose reduction (2-comp vs 1-comp): {dose_reduction:.1f}%")

# ─────────────────────────────────────────────
# SIMULATION 5: ANNUAL RISK SUMMARIES
# ─────────────────────────────────────────────

annual_risk_1comp = P_full_comp_fire_1comp * CONSEQUENCE_MODERATE * 10   # scaled
annual_risk_2comp = P_full_comp_fire_2comp * CONSEQUENCE_MODERATE * 5     # scaled

print("\n" + "=" * 60)
print("SIMULATION 5: COMPARATIVE RISK SUMMARY")
print("=" * 60)
print(f"\n{'Metric':<45} {'1-Comp':>12} {'2-Comp':>12}")
print("-" * 70)
print(f"{'Annual P(full compartment fire)':<45} {P_full_comp_fire_1comp:>12.6f} {P_full_comp_fire_2comp:>12.6f}")
print(f"{'Mean HF dose (mg/m³, 10-min)':<45} {np.mean(dose_1comp):>12.2f} {np.mean(dose_2comp):>12.2f}")
print(f"{'P(HF dose > IDLH, per event)':<45} {np.mean(dose_1comp>IDLH_HF_mg_m3)*100:>11.1f}% {np.mean(dose_2comp>IDLH_HF_mg_m3)*100:>11.1f}%")
print(f"{'Mean time to IDLH (min)':<45} {np.mean(t_IDLH_effective_1comp)/60:>12.1f} {np.mean(t_IDLH_effective_2comp)/60:>12.1f}")
print(f"{'P(IDLH within 5 min, per event)':<45} {np.mean(t_IDLH_effective_1comp<300)*100:>11.1f}% {np.mean(t_IDLH_effective_2comp<300)*100:>11.1f}%")

# ALARP assessment (UK HSE framework)
print("\n  ALARP Assessment (UK HSE framework):")
print(f"  1-compartment residual risk: {P_full_comp_fire_1comp * CONSEQUENCE_MAJOR:.5f} → {'UNACCEPTABLE' if P_full_comp_fire_1comp*CONSEQUENCE_MAJOR > 0.001 else 'Tolerable if ALARP'}")
print(f"  2-compartment residual risk: {P_full_comp_fire_2comp * CONSEQUENCE_MODERATE:.5f} → {'UNACCEPTABLE' if P_full_comp_fire_2comp*CONSEQUENCE_MODERATE > 0.001 else 'Broadly Acceptable'}")

# Save numerical results for paper
results = {
    "N_simulations": N,
    "HF_dose_IDLH_mgm3": IDLH_HF_mg_m3,
    "one_compartment": {
        "capacity_kWh": float(single_comp_kWh),
        "mean_HF_dose_mgm3": float(np.mean(dose_1comp)),
        "median_HF_dose_mgm3": float(np.median(dose_1comp)),
        "pct_HF_exceeds_IDLH": float(np.mean(dose_1comp > IDLH_HF_mg_m3) * 100),
        "pct_HF_exceeds_5x_IDLH": float(np.mean(dose_1comp > 5*IDLH_HF_mg_m3) * 100),
        "mean_time_to_IDLH_min": float(np.mean(t_IDLH_effective_1comp) / 60),
        "p_IDLH_within_5min_pct": float(np.mean(t_IDLH_effective_1comp < 300) * 100),
        "P_full_comp_fire_annual": float(P_full_comp_fire_1comp),
        "risk_index": float(P_full_comp_fire_1comp * CONSEQUENCE_MAJOR),
    },
    "two_compartment": {
        "capacity_kWh_per_comp": float(comp1_kWh),
        "mean_HF_dose_mgm3": float(np.mean(dose_2comp)),
        "median_HF_dose_mgm3": float(np.median(dose_2comp)),
        "pct_HF_exceeds_IDLH": float(np.mean(dose_2comp > IDLH_HF_mg_m3) * 100),
        "pct_HF_exceeds_5x_IDLH": float(np.mean(dose_2comp > 5*IDLH_HF_mg_m3) * 100),
        "mean_time_to_IDLH_min": float(np.mean(t_IDLH_effective_2comp) / 60),
        "p_IDLH_within_5min_pct": float(np.mean(t_IDLH_effective_2comp < 300) * 100),
        "P_full_comp_fire_annual": float(P_full_comp_fire_2comp),
        "risk_index": float(P_full_comp_fire_2comp * CONSEQUENCE_MODERATE),
    },
    "improvement": {
        "HF_dose_reduction_pct": float(dose_reduction),
        "IDLH_time_extension_min": float((np.mean(t_IDLH_effective_1comp) - np.mean(t_IDLH_effective_2comp)) / 60),
    }
}

import os
_results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(_results_dir, exist_ok=True)
_results_path = os.path.join(_results_dir, "pra_results.json")
with open(_results_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n\nResults saved to {_results_path}")
