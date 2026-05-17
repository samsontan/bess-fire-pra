#!/usr/bin/env python3
"""
EQIX SG4-4A BESS Fire Safety PRA Manuscript
Figure 7 Generator: Event Tree Analysis - BESS Thermal Runaway Propagation Sequence
Industry-standard staircase format (Option A reference).

Prepared by:  Samson Tan PhD | BOA Reg. No. 1324 | STAARCH Pte Ltd
Target:       Fire and Materials (peer-reviewed journal submission)
Source data:  BESS_Event_Tree.xlsx (EQIX SG4-4A HMA Monte Carlo PRA, N=10,000)

Usage:
    python generate_figure7.py

Output:
    EQIX-SG4-4A_Figure7_EventTree.png   (high-resolution, 2x scale)

Requirements:
    pip install cairosvg

The SVG source file (EQIX-SG4-4A_Figure7_EventTree.svg) must be in the same
folder as this script.
"""

import os
import sys
import subprocess

# Dependency check
try:
    import cairosvg
except ImportError:
    print("cairosvg not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cairosvg"])
    import cairosvg

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SVG_PATH = os.path.join(SCRIPT_DIR, "EQIX-SG4-4A_Figure7_EventTree.svg")
PNG_PATH = os.path.join(SCRIPT_DIR, "EQIX-SG4-4A_Figure7_EventTree.png")

if not os.path.exists(SVG_PATH):
    print(f"ERROR: Source SVG not found at {SVG_PATH}")
    sys.exit(1)

print(f"Rendering: {SVG_PATH}")
cairosvg.svg2png(
    url=SVG_PATH,
    write_to=PNG_PATH,
    output_width=2800,   # 2x scale, ~300 dpi equivalent for print at A4 landscape
)

size_kb = os.path.getsize(PNG_PATH) // 1024
print(f"Output:    {PNG_PATH} ({size_kb} KB)")
print("Done.")
