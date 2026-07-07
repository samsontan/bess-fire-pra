"""
A2 + A3 production analyses for fire-4382023 v14 (run 2026-07-07).

Chain replicates suppression_erl_model.py exactly:
  P_multi = P_TR * P_BMS * P_UL                      (point: 0.01*0.15*0.08 = 1.2e-4)
  eff(delay) piecewise .78/.45/.20 (+-10% uniform), delay ~ lognormal(ln 8, 0.6)
  F_A = 0.80 + F_CO + F_smoke = 0.80 + 0.001 + 0.015 = 0.816   (water-only)
  F_B = 0.80 + 0.2*F_CO + 0.2*F_smoke = 0.8032                  (gas+water)
  ERL_w  = 2 * P_multi * P_wfail * F_A
  ERL_gw = 2 * P_multi * P_wfail * 0.20 * F_B
Point check: ERL_w = 1.22e-4, ERL_gw = 2.40e-5, reduction 80.3% (structural).

A2: distributions P_TR ~ lognormal(ln .01, .35); P_BMS ~ Beta(2.55,14.45) mean .15;
    P_UL ~ Beta(1.84,21.16) mean .08; N = 100,000, seed 42.
A3: OAT tornado on the production chain; delay-median swings evaluated analytically.
"""
import json, math
import numpy as np
from scipy.stats import norm

OUT_JSON = r"C:\temp_bess_v14\analysis\production_uncertainty.json"

F_CO, F_SMOKE, F_HF = 0.001, 0.015, 0.80
F_A = F_HF + F_CO + F_SMOKE
F_B = F_HF + 0.2 * F_CO + 0.2 * F_SMOKE
GAS_FAIL = 0.20

def wfail_from_median(m):
    """Analytic mean water-failure prob for lognormal(ln m, 0.6) delay, piecewise eff."""
    z3 = (math.log(3) - math.log(m)) / 0.6
    z10 = (math.log(10) - math.log(m)) / 0.6
    p1 = norm.cdf(z3)
    p2 = norm.cdf(z10) - p1
    p3 = 1 - norm.cdf(z10)
    return 1 - (p1 * 0.78 + p2 * 0.45 + p3 * 0.20)

# ---------- point check ----------
P_MULTI_PT = 0.01 * 0.15 * 0.08
WFAIL_PT = wfail_from_median(8.0)
ERL_W_PT = 2 * P_MULTI_PT * WFAIL_PT * F_A
ERL_GW_PT = 2 * P_MULTI_PT * WFAIL_PT * GAS_FAIL * F_B
RED_PT = 1 - ERL_GW_PT / ERL_W_PT
print(f"point: P_multi={P_MULTI_PT:.4g} wfail={WFAIL_PT:.4f} "
      f"ERL_w={ERL_W_PT:.4g} ERL_gw={ERL_GW_PT:.4g} reduction={RED_PT:.4f}")

# ---------- A2: distribution propagation ----------
rng = np.random.default_rng(42)
N = 100_000
P_TR = rng.lognormal(math.log(0.01), 0.35, N)
P_BMS = rng.beta(2.55, 14.45, N)
P_UL = rng.beta(1.84, 21.16, N)
P_multi = P_TR * P_BMS * P_UL
delay = rng.lognormal(math.log(8), 0.6, N)
eff = np.where(delay <= 3, 0.78, np.where(delay <= 10, 0.45, 0.20)) * rng.uniform(0.9, 1.1, N)
wfail = 1 - eff
ERL_w = 2 * P_multi * wfail * F_A
ERL_gw = 2 * P_multi * wfail * GAS_FAIL * F_B
red = 1 - ERL_gw / ERL_w  # exactly constant: 1 - 0.2*F_B/F_A

def stats(x):
    return dict(mean=float(np.mean(x)), median=float(np.median(x)),
                p5=float(np.percentile(x, 5)), p95=float(np.percentile(x, 95)))

a2 = dict(P_multi=stats(P_multi), ERL_w=stats(ERL_w), ERL_gw=stats(ERL_gw),
          reduction=float(red[0]),
          ERL_w_CI_ratio=float(np.percentile(ERL_w, 95) / np.percentile(ERL_w, 5)))
print("A2:", json.dumps(a2, indent=1))

# ---------- A3: OAT tornado (production chain) ----------
# hf_yield base = triangular-distribution mean (0.3+0.5+0.8)/3, matching the
# published MC means (dose 580 mg/m3, clearance 301 min for the 2-comp case)
base = dict(P_TR=0.01, P_BMS=0.15, P_UL=0.08, delay_med=8.0, P_occ=0.15,
            hf_yield=0.5333, ach=9.0)

def erl_oat(p):
    f_a = F_HF + F_CO * (p["P_occ"] / 0.15) + 0.10 * p["P_occ"]
    return 2 * p["P_TR"] * p["P_BMS"] * p["P_UL"] * wfail_from_median(p["delay_med"]) * f_a

def dose_oat(p):
    # 10-min time-averaged concentration x window, 2-comp: proportional to yield; ACH negligible early
    m = 242.76 * p["hf_yield"]; V = 116.0; k = p["ach"] / 3600.0
    C0 = m / V * 1000.0
    return C0 * (1 - math.exp(-k * 600)) / (k * 600)

def clear_oat(p):
    # mass-purge bound used by pra_simulation.py: t = m_HF / (Q * C_IDLH) + vent delay
    m_mg = 242.76 * p["hf_yield"] * 1000.0
    Q = 116.0 * p["ach"] / 3600.0  # m3/s
    return (m_mg / (Q * 25.0)) / 60.0 + 1.5  # minutes

swings = dict(P_TR=(0.005, 0.02), P_BMS=(0.10, 0.40), P_UL=(0.05, 0.15),
              delay_med=(4.0, 16.0), P_occ=(0.05, 0.30), hf_yield=(0.3, 0.8), ach=(6.0, 12.0))
tornado = {}
for k2, (lo, hi) in swings.items():
    row = {}
    for out_name, fn in [("ERL", erl_oat), ("dose", dose_oat), ("clearance", clear_oat)]:
        plo, phi = dict(base), dict(base)
        plo[k2], phi[k2] = lo, hi
        b, vlo, vhi = fn(base), fn(plo), fn(phi)
        row[out_name] = dict(lo=vlo, hi=vhi, base=b,
                             rel_swing=abs(vhi - vlo) / b if b else 0)
    tornado[k2] = row
print("\nERL tornado ranking (rel swing):")
for k2, row in sorted(tornado.items(), key=lambda kv: -kv[1]["ERL"]["rel_swing"]):
    print(f"  {k2:10s} ERL rel swing {row['ERL']['rel_swing']:.3f}  "
          f"dose {row['dose']['rel_swing']:.3f}  clear {row['clearance']['rel_swing']:.3f}")

json.dump(dict(point=dict(P_multi=P_MULTI_PT, wfail=WFAIL_PT, ERL_w=ERL_W_PT,
                          ERL_gw=ERL_GW_PT, reduction=RED_PT),
               a2=a2, tornado=tornado, base=base, swings=swings),
          open(OUT_JSON, "w"), indent=1)
print("\nsaved:", OUT_JSON)
