"""New sensitivity figure (v14): tornado panels from production_uncertainty.json.
Panel (a): ERL swings; panel (b): HF dose and IDLH clearance swings. 600 dpi."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = json.load(open(r"C:\temp_bess_v14\analysis\production_uncertainty.json"))
T = D["tornado"]
NICE = {"P_TR": "TR initiating frequency\n(0.005 - 0.02 /comp-yr)",
        "P_BMS": "BMS failure probability\n(0.10 - 0.40)",
        "P_UL": "UL 9540A containment failure\n(0.05 - 0.15)",
        "delay_med": "Suppression delay median\n(4 - 16 min)",
        "P_occ": "Occupancy probability\n(0.05 - 0.30)",
        "hf_yield": "HF yield\n(0.3 - 0.8 g/kWh)",
        "ach": "Ventilation rate\n(6 - 12 ACH)"}
NAVY, BLUE, ORANGE = "#16324f", "#2874a6", "#e67e22"

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 5.6))

erl_keys = ["P_BMS", "P_TR", "P_UL", "delay_med", "P_occ"]
base_erl = T["P_BMS"]["ERL"]["base"]
for i, k in enumerate(erl_keys):
    lo, hi = T[k]["ERL"]["lo"], T[k]["ERL"]["hi"]
    y = len(erl_keys) - 1 - i
    width = hi - lo
    ax1.barh(y, width, left=lo, height=0.55, color=BLUE, alpha=0.85, zorder=3)
    note = f"{min(lo,hi):.1e} - {max(lo,hi):.1e}"
    if abs(width) / base_erl < 0.05:
        note += "  (negligible swing)"
    ax1.text(max(lo, hi) * 1.06, y, note, va="center", fontsize=9.5,
             color="#1c2833")
ax1.axvline(base_erl, color=NAVY, lw=2.0, ls="--", zorder=4)
ax1.text(base_erl * 0.93, 0.05, f"base ERL {base_erl:.2e}", fontsize=9.5,
         color=NAVY, rotation=90, va="bottom", ha="right")
ax1.set_yticks(range(len(erl_keys)))
ax1.set_yticklabels([NICE[k] for k in reversed(erl_keys)], fontsize=10)
ax1.set_xscale("log")
ax1.set_xlabel("ERL, water-only installation [fatalities/yr]", fontsize=11.5)
ax1.set_title("(a) ERL sensitivity (one-at-a-time swings)", fontsize=12, fontweight="bold")
ax1.grid(True, axis="x", which="both", color="#d5d8dc", lw=0.5, zorder=0)
ax1.tick_params(axis="x", labelsize=10)

pairs = [("hf_yield", "dose", "10-min mean HF dose [mg/m$^3$]", ORANGE),
         ("ach", "dose", None, ORANGE),
         ("hf_yield", "clearance", "IDLH clearance time [min]", BLUE),
         ("ach", "clearance", None, BLUE)]
labels, y = [], 0
for k, out, _, c in reversed(pairs):
    lo, hi = T[k][out]["lo"], T[k][out]["hi"]
    b = T[k][out]["base"]
    ax2.barh(y, (hi - lo) / b, left=min(lo, hi) / b, height=0.55, color=c,
             alpha=0.85, zorder=3)
    unit = "mg/m$^3$" if out == "dose" else "min"
    ax2.text(max(lo, hi) / b + 0.04, y,
             f"{min(lo,hi):.0f} - {max(lo,hi):.0f} {unit}",
             va="center", fontsize=9.5)
    labels.append(f"{NICE[k].splitlines()[0]}\n→ {out}")
    y += 1
ax2.axvline(1.0, color=NAVY, lw=2.0, ls="--", zorder=4)
ax2.set_yticks(range(len(pairs)))
ax2.set_yticklabels(labels, fontsize=10)
ax2.set_xlabel("Output relative to base case", fontsize=11.5)
ax2.set_title("(b) Dose and clearance-time sensitivity", fontsize=12, fontweight="bold")
ax2.grid(True, axis="x", color="#d5d8dc", lw=0.5, zorder=0)
ax2.tick_params(axis="x", labelsize=10)

fig.tight_layout()
fig.savefig(r"C:\temp_bess_v14\figures\Fig_Tornado_v14.png", dpi=600,
            bbox_inches="tight", facecolor="white")
print("saved Fig_Tornado_v14.png")
