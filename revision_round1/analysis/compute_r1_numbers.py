"""
Round-1 response support numbers -- fire-4382023 (run 2026-07-07).

Produces r1_response_numbers.json with three blocks:
  A. box_vs_fds  -- well-mixed box model vs corrected FDS run (eqix_corrected, 2026-06-15,
                    peak 713.4 kW @ 385 s) at three spatial reference levels.
  B. event_tree_mc -- distribution-level propagation of the event-tree parameters
                    (PROTOTYPE: standalone chain; the manuscript-grade run must be
                    integrated with 02_PRA scripts / suppression_erl_model.py -- see
                    REVISION_PLAN A2. Prototype ERL absolute values are NOT quotable;
                    the P_multi credible interval and the invariance of the relative
                    dual-suppression benefit are the quotable findings.)
  C. tornado     -- OAT swings (PROTOTYPE ranking only; manuscript run via
                    sensitivity_analyses.py extension -- REVISION_PLAN A3).

Conversion basis: 25 degC; MW_HF 20.01; ppm = Y * (28.97/20.01) * 1e6; mg/m3 = ppm*20.01/24.45.
Box model (2-comp): m_HF = 242.76 kWh * 0.5 g/kWh; V = 116 m3; k = 9 ACH.
"""
import csv, json, math
import numpy as np

DEVC = r"C:/FDS_runs/eqix_corrected/eqix_corrected_devc.csv"
OUT = r"G:\My Drive\SAI\PEER_REVIEW_SUBMISSIONS\260601_SUBMITTED_MDPI-Fire_BESS_Fire_Safety_fire-4382023\260707_Round1_Revision\analysis\r1_response_numbers.json"

rows = list(csv.reader(open(DEVC)))
hdr = rows[1]
data = np.array([[float(x) for x in r] for r in rows[2:]])
cols = {h: i for i, h in enumerate(hdr)}
t = data[:, 0]
MW_HF, MW_AIR = 20.01, 28.97
Y2ppm = lambda Y: Y * (MW_AIR / MW_HF) * 1e6
ppm2mg = lambda p: p * MW_HF / 24.45
IDLH_PPM = 30.0

res = {}
for name in ["HF_NORTH_AISLE_BZ", "HF_DOOR_BZ", "HF_CEILING_CAB4"]:
    ppm = Y2ppm(data[:, cols[name]])
    mg = ppm2mg(ppm)
    ipk = int(np.argmax(mg))
    cross = t[ppm > IDLH_PPM]
    res[name] = dict(
        peak_mg=round(float(mg[ipk])), peak_ppm=round(float(ppm[ipk])),
        t_peak=float(t[ipk]), end_mg=round(float(mg[-1])),
        first_IDLH_s=float(cross[0]) if len(cross) else None,
        timeavg_mg_600s=round(float(np.trapezoid(mg, t) / (t[-1] - t[0]))),
    )
m_HF = 242.76 * 0.5
V, k = 116.0, 9 / 3600.0
C0 = m_HF / V * 1000.0
res["box_model_2comp_mode_yield"] = dict(
    C0_mg=round(C0), C_600s=round(C0 * math.exp(-k * 600)),
    timeavg_mg_600s=round(C0 * (1 - math.exp(-k * 600)) / (k * 600)),
)

rng = np.random.default_rng(42)
N = 100_000
P_TR = rng.lognormal(math.log(0.01), 0.35, N)
P_BMS = rng.beta(2.55, 14.45, N)      # mean 0.15
P_UL = rng.beta(1.84, 21.16, N)       # mean 0.08
P_multi = P_TR * P_BMS * P_UL
delay = rng.lognormal(math.log(8), 0.6, N)
eff = np.where(delay <= 3, 0.78, np.where(delay <= 10, 0.45, 0.20)) * rng.uniform(0.9, 1.1, N)
P_wfail = 1 - eff
red = 1 - (P_wfail * 0.20 * 0.82) / (P_wfail * 0.90)  # relative dual-suppression benefit
mc = dict(
    P_multi_central=float(np.median(P_multi)),
    P_multi_CI90=[float(np.percentile(P_multi, 5)), float(np.percentile(P_multi, 95))],
    dual_suppression_reduction=float(np.mean(red)),
)

base = dict(P_TR=0.01, P_BMS=0.15, P_UL=0.08, eff=0.379, F=0.90, P_occ=0.15)
def erl_pt(p):
    return p["P_TR"] * p["P_BMS"] * p["P_UL"] * (1 - p["eff"]) * p["F"] * p["P_occ"] * 2 * 2
swings = {"P_TR": (0.005, 0.02), "P_BMS": (0.10, 0.40), "P_UL": (0.05, 0.15),
          "eff": (0.20, 0.60), "F": (0.5, 0.95), "P_occ": (0.05, 0.30)}
torn = {}
for k2, (lo, hi) in swings.items():
    plo, phi = dict(base), dict(base)
    plo[k2], phi[k2] = lo, hi
    torn[k2] = [erl_pt(plo), erl_pt(phi)]

json.dump(dict(box_vs_fds=res, event_tree_mc=mc, tornado_prototype=torn),
          open(OUT, "w"), indent=1)
print("written:", OUT)
