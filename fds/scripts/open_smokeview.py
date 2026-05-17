"""Launch Smokeview for the eqix_preview run."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import subprocess, os

SMV_EXE = r"C:\FDS_extract\firemodels\SMV6\smokeview.exe"
SMV_FILE = r"C:\FDS_runs\eqix_preview\eqix_preview.smv"
RUN_DIR  = r"C:\FDS_runs\eqix_preview"

if not os.path.exists(SMV_EXE):
    print(f"ERROR: Smokeview not found at {SMV_EXE}")
    sys.exit(1)
if not os.path.exists(SMV_FILE):
    print(f"ERROR: SMV file not found: {SMV_FILE}")
    sys.exit(1)

print(f"Opening Smokeview...")
print(f"  SMV file : {SMV_FILE}")
print(f"  Exe      : {SMV_EXE}")
print(f"")
print("Smokeview tips for this run:")
print("  Load slices: Load Data > Slice Files > HYDROGEN FLUORIDE (MASS FRACTION)")
print("  For Fig 14: choose PBZ=1.50 (breathing zone plan view)")
print("  For Fig 12: choose PBY=2.50 (room centreline section)")
print("  Use the time bar to step through frames -- new frames appear as FDS runs")
print("  Fire starts at t=60s, HF visible at t=90s, peak at t=360s")
print("")

proc = subprocess.Popen(
    [SMV_EXE, "eqix_preview.smv"],
    cwd=RUN_DIR,
    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
)
print(f"Smokeview launched: PID {proc.pid}")
