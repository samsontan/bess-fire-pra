"""Figure 1 (v14): BESS thermal runaway event tree, corrected probability chain (B1).
v2 layout: wrapped outcome text, wide column gutters, labels clear of lines,
A/B design sub-nodes, severity colors matched to outcome class. 600 dpi.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

NAVY, GREEN, RED, ORANGE, GREY = "#16324f", "#1a7a4a", "#b03a2e", "#b9770e", "#5d6d7e"

fig, ax = plt.subplots(figsize=(16.4, 7.6))
ax.set_xlim(0, 24.4)
ax.set_ylim(0, 12.0)
ax.axis("off")

# ---------------- header band ----------------
headers = [
    (0.15, 2.60, "Initiating\nevent", 10.5),
    (3.00, 2.15, "BMS isolates\n$P_{fail}$ = 0.15", 9.4),
    (5.40, 2.15, "UL 9540A\n$P_{fail}$ = 0.08", 9.4),
    (7.80, 3.30, "Suppression\nA: water  B: gas+water", 9.0),
    (11.45, 6.30, "Outcome", 11.0),
    (17.95, 1.05, "Sc.", 10.5),
    (19.15, 2.20, "Frequency\n[/comp-yr]", 9.8),
    (21.55, 2.70, "Severity", 10.5),
]
for x, w, label, fs in headers:
    ax.add_patch(FancyBboxPatch((x, 10.70), w, 1.12, boxstyle="round,pad=0.02",
                                fc=NAVY, ec="none"))
    ax.text(x + w / 2, 11.26, label, color="white", ha="center", va="center",
            fontsize=fs, fontweight="bold")

# ---------------- outcome rows ----------------
rows = [
    ("No propagation: BMS isolates, thermal runaway\nlimited to the initiating cabinet",
     "1", r"$8.5\times10^{-3}$", "Negligible", GREEN, "#eaf3ef"),
    ("Limited propagation: UL 9540A containment\nconfines spread to adjacent cabinets",
     "2", r"$1.4\times10^{-3}$", "Minor", GREEN, "#eaf3ef"),
    ("Multi-cabinet TR: flaming controlled once\nwater suppression activates",
     "3A", r"$4.5\times10^{-5}$", "Major", ORANGE, "#fdf3e3"),
    ("Unsuppressed full-compartment fire with\nHF release (water suppression fails)",
     "4A", r"$7.5\times10^{-5}$", "Catastrophic", RED, "#fbe9e7"),
    ("Multi-cabinet TR: gas controls flaming at\n0.5 min, water then cools the TR source",
     "3B", r"$1.1\times10^{-4}$", "Major", ORANGE, "#fdf3e3"),
    ("Residual uncontrolled fire: both gas and\nwater suppression layers fail",
     "4B", r"$1.5\times10^{-5}$", "Catastrophic", RED, "#fbe9e7"),
]
ys = [9.85, 8.55, 7.25, 5.95, 4.65, 3.35]
X_TEXT, X_SC, X_FREQ, X_SEV = 11.65, 18.45, 20.25, 22.90
for (label, sc, freq, sev, sevc, bg), y in zip(rows, ys):
    ax.add_patch(FancyBboxPatch((11.45, y - 0.52), 12.80, 1.04,
                                boxstyle="round,pad=0.02", fc=bg, ec="none"))
    ax.text(X_TEXT, y, label, fontsize=9.4, va="center", color="#1c2833",
            linespacing=1.25)
    ax.text(X_SC, y, sc, fontsize=10.5, va="center", ha="center",
            fontweight="bold", color=NAVY)
    ax.text(X_FREQ, y, freq, fontsize=10.0, va="center", ha="center", color="#1c2833")
    ax.text(X_SEV, y, sev, fontsize=9.8, va="center", ha="center",
            color=sevc, fontweight="bold")

# ---------------- tree ----------------
LW = 1.9
def hline(x0, x1, y):
    ax.plot([x0, x1], [y, y], color=NAVY, lw=LW, solid_capstyle="round", zorder=2)
def vline(x, y0, y1):
    ax.plot([x, x], [y0, y1], color=NAVY, lw=LW, solid_capstyle="round", zorder=2)
def node(x, y, tag=None):
    ax.plot([x], [y], marker="o", ms=5.5, color=NAVY, zorder=4)
    if tag:
        ax.text(x - 0.12, y + 0.20, tag, fontsize=9.5, fontweight="bold", color=NAVY,
                ha="right", va="bottom", zorder=5)

# initiating event box
ax.add_patch(FancyBboxPatch((0.15, 6.10), 2.60, 1.70, boxstyle="round,pad=0.06",
                            fc="#fff7dd", ec=NAVY, lw=1.4))
ax.text(1.45, 7.36, "TR initiating event", fontsize=10.2, ha="center",
        fontweight="bold", color=NAVY)
ax.text(1.45, 6.88, r"$P(TR) = 0.01$", fontsize=10.0, ha="center", color="#1c2833")
ax.text(1.45, 6.42, "per compartment-year", fontsize=8.6, ha="center", color=GREY)

Y0 = 6.95
XB, XU, XH, XS = 4.10, 6.60, 8.55, 9.50
hline(2.75, XB, Y0); node(XB, Y0)

# BMS isolates -> row 1
vline(XB, Y0, ys[0]); hline(XB, 11.45, ys[0])
ax.text(XB + 0.35, ys[0] + 0.18, "isolates  0.85", fontsize=9.6, color=GREEN,
        fontweight="bold", va="bottom")
# BMS fails -> UL node
vline(XB, Y0, 5.75); hline(XB, XU, 5.75); node(XU, 5.75)
ax.text(XB + 0.35, 5.75 - 0.20, "fails  0.15", fontsize=9.6, color=RED,
        fontweight="bold", va="top")
# UL contains -> row 2
vline(XU, 5.75, ys[1]); hline(XU, 11.45, ys[1])
ax.text(XU + 0.35, ys[1] + 0.18, "contains  0.92", fontsize=9.6, color=GREEN,
        fontweight="bold", va="bottom")
# UL fails -> hub
vline(XU, 5.75, 4.85); hline(XU, XH, 4.85); node(XH, 4.85)
ax.text(XU + 0.35, 4.85 - 0.20, "fails  0.08", fontsize=9.6, color=RED,
        fontweight="bold", va="top")
ax.text(4.70, 4.12, r"multi-cabinet TR:  $1.2\times10^{-4}$ /comp-yr",
        fontsize=9.0, color=NAVY, style="italic", ha="left", va="top")

# hub -> design sub-nodes A (up) and B (down)
vline(XH, 4.85, 6.60); hline(XH, XS, 6.60); node(XS, 6.60, "A")
vline(XH, 4.85, 4.00); hline(XH, XS, 4.00); node(XS, 4.00, "B")

# A: success -> 3A, fail -> 4A
vline(XS, 6.60, ys[2]); hline(XS, 11.45, ys[2])
ax.text(11.30, ys[2] + 0.16, "water works  0.378", fontsize=8.9, color=GREEN,
        fontweight="bold", va="bottom", ha="right")
vline(XS, 6.60, ys[3]); hline(XS, 11.45, ys[3])
ax.text(11.30, ys[3] + 0.16, "water fails  0.622", fontsize=8.9, color=RED,
        fontweight="bold", va="bottom", ha="right")
# B: success -> 3B, fail -> 4B
vline(XS, 4.00, ys[4]); hline(XS, 11.45, ys[4])
ax.text(11.30, ys[4] + 0.16, "gas controls  0.876", fontsize=8.9, color=GREEN,
        fontweight="bold", va="bottom", ha="right")
vline(XS, 4.00, ys[5]); hline(XS, 11.45, ys[5])
ax.text(11.30, ys[5] + 0.16, "both fail  0.124", fontsize=8.9, color=RED,
        fontweight="bold", va="bottom", ha="right")

# ---------------- summary table ----------------
ty = 2.45
ax.add_patch(FancyBboxPatch((0.15, 0.10), 24.05, ty + 0.05,
                            boxstyle="round,pad=0.03", fc="#f2f4f8", ec=NAVY, lw=1.1))
cols = [0.60, 9.10, 12.60, 16.20, 20.40]
head = ["Design branch (installation, 2 compartments)", "P(suppression fails)",
        "ERL [fatalities/yr]", "Individual risk", "HSE classification"]
for x, h in zip(cols, head):
    ax.text(x, ty - 0.16, h, fontsize=9.9, fontweight="bold", color=NAVY, va="top")
rowsA = ["A   Water-only suppression", "62.2%", r"$1.22\times10^{-4}$",
         "1 in 16,424 per year", "Tolerable if ALARP"]
rowsB = ["B   Gas + water dual suppression", "12.4%", r"$2.40\times10^{-5}$",
         "1 in 83,433 per year", "Broadly acceptable"]
for x, v in zip(cols, rowsA):
    ax.text(x, ty - 0.78, v, fontsize=9.9, color=ORANGE if x > 1 else "#1c2833", va="top")
for x, v in zip(cols, rowsB):
    ax.text(x, ty - 1.36, v, fontsize=9.9, color=GREEN if x > 1 else "#1c2833", va="top")
ax.text(0.60, ty - 1.90,
        "Adding gas suppression reduces installation ERL by 80.3%  "
        r"($1.22\times10^{-4} \to 2.40\times10^{-5}$ fatalities/yr)",
        fontsize=9.9, color=RED, fontweight="bold", va="top")

fig.savefig(r"C:\temp_bess_v14\figures\Fig1_EventTree_v14.png", dpi=600,
            bbox_inches="tight", facecolor="white")
print("saved Fig1_EventTree_v14.png (v2 layout)")
