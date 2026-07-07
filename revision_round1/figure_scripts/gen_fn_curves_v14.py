"""Figure 3 (v14): F-N curves, societal risk, rebuilt from Table 7 values.
Step curves (N_max = 2), UK HSE criterion lines F = 1e-3/N and 1e-5/N, shaded bands,
heavy line weights and large fonts for single-column legibility. 600 dpi."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SCEN = [  # label, F(N>=1), F(N>=2), color, style
    ("1-comp, water-only",              2.5e-5, 1.8e-6, "#e67e22", "-"),
    ("2-comp, water-only",              2.1e-5, 1.5e-6, "#7d3c98", "--"),
    ("2-comp, gas + water",             4.3e-6, 3.1e-7, "#1f618d", "-"),
    ("2-comp, gas + water, BMS P=0.05", 1.4e-6, 1.0e-7, "#1a7a4a", "-"),
]

fig, ax = plt.subplots(figsize=(7.6, 6.2))
N = np.logspace(np.log10(0.8), np.log10(30), 200)

ax.fill_between(N, 1e-3 / N, 1e0, color="#fdecea", zorder=0)
ax.fill_between(N, 1e-5 / N, 1e-3 / N, color="#fef9e7", zorder=0)
ax.fill_between(N, 1e-9, 1e-5 / N, color="#eafaf1", zorder=0)
ax.plot(N, 1e-3 / N, "--", color="#922b21", lw=2.2)
ax.plot(N, 1e-5 / N, "--", color="#196f3d", lw=2.2)
ax.text(6.5, 6e-5, "Unacceptable\n$F = 10^{-3}/N$", fontsize=11, color="#922b21",
        fontweight="bold", ha="center")
ax.text(6.5, 4.5e-7, "Broadly acceptable\n$F = 10^{-5}/N$", fontsize=11,
        color="#196f3d", fontweight="bold", ha="center")
ax.text(1.9, 4.5e-5, "Tolerable if ALARP", fontsize=11, color="#7d6608",
        fontweight="bold", rotation=-32)

for label, f1, f2, c, ls in SCEN:
    ax.step([1, 2, 2.9], [f1, f2, f2 * 0.28], where="post", color=c, lw=3.0,
            ls=ls, label=label, zorder=4)
    ax.plot([1, 2], [f1, f2], "o", color=c, ms=8, zorder=5,
            markeredgecolor="white", markeredgewidth=1.2)

ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(0.9, 10); ax.set_ylim(3e-8, 3e-3)
ax.set_xticks([1, 2, 5, 10])
ax.set_xticklabels(["1", "2", "5", "10"], fontsize=12)
ax.tick_params(axis="y", labelsize=12)
ax.set_xlabel("Number of fatalities, N", fontsize=13)
ax.set_ylabel("Frequency of N or more fatalities, F [1/yr]", fontsize=13)
ax.grid(True, which="both", color="#d5d8dc", lw=0.5, zorder=1)
ax.legend(fontsize=10.5, loc="upper right", framealpha=0.95, edgecolor="#aab7b8")
fig.tight_layout()
fig.savefig(r"C:\temp_bess_v14\figures\Fig3_FN_Curves_v14.png", dpi=600,
            bbox_inches="tight", facecolor="white")
print("saved Fig3_FN_Curves_v14.png")
