"""
save_as_v11.py
Copy the ground-truth draft (already corrected by Sam) to v11 in the main paper
folder, then export to PDF via Word COM.
"""

import sys, os, shutil
sys.stdout.reconfigure(encoding='utf-8')

BASE  = r'G:\My Drive\SAI\Projects\EQIX_SG4-4A_NFPA855_HMA_Waiver_Report\__Mickey7_BESS_Fire_Safety_Paper'
SRC   = os.path.join(BASE, r'Manuscript Draft to Khalid and Paul - 2026-05-17\BESS_Fire_Safety_Paper_Draft_260517.docx')
DEST_DOCX = os.path.join(BASE, 'BESS_Fire_Safety_Paper_Q1_revised_v11.docx')
DEST_PDF  = os.path.join(BASE, 'BESS_Fire_Safety_Paper_Q1_revised_v11.pdf')

# ── 1. Copy ────────────────────────────────────────────────────────────────────
print(f'Source : {SRC}')
print(f'  size : {os.path.getsize(SRC):,} bytes')
shutil.copy2(SRC, DEST_DOCX)
print(f'Copied → {DEST_DOCX}')
print(f'  size : {os.path.getsize(DEST_DOCX):,} bytes')

# ── 2. Kill any stale Word instances ──────────────────────────────────────────
import subprocess
subprocess.run(['taskkill', '/F', '/IM', 'WINWORD.EXE'],
               capture_output=True)

# ── 3. Export PDF via Word COM ─────────────────────────────────────────────────
print('\nConverting to PDF ...')
import win32com.client

word = win32com.client.Dispatch('Word.Application')
word.Visible = False
try:
    wdoc = word.Documents.Open(os.path.abspath(DEST_DOCX))
    wdoc.SaveAs(os.path.abspath(DEST_PDF), FileFormat=17)
    wdoc.Close(False)
    print(f'PDF → {DEST_PDF}')
    print(f'  size : {os.path.getsize(DEST_PDF):,} bytes')
finally:
    try:
        word.Quit()
    except Exception:
        pass

# ── 4. Summary ─────────────────────────────────────────────────────────────────
print('\nFiles in main paper folder (v* only):')
for f in sorted(os.listdir(BASE)):
    if f.startswith('BESS_Fire_Safety_Paper_Q1'):
        sz = os.path.getsize(os.path.join(BASE, f))
        print(f'  {f:<55s}  {sz:>12,} bytes')
print('\nDone.')
