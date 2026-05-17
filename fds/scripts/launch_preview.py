"""Launch FDS preview run in background -- detached subprocess."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import subprocess, os

FDS_BIN = r"C:\FDS_extract\firemodels\FDS6\bin"
MPI_BIN = r"C:\FDS_extract\firemodels\FDS6\bin\mpi"
RUN_DIR = r"C:\FDS_runs\eqix_preview"
FDS_EXE = os.path.join(FDS_BIN, "fds.exe")
MPI_EXE = os.path.join(MPI_BIN, "mpiexec.exe")

env = os.environ.copy()
env["PATH"] = FDS_BIN + ";" + MPI_BIN + ";" + env.get("PATH", "")

log_file = open(os.path.join(RUN_DIR, "preview_run.log"), "w")

proc = subprocess.Popen(
    [MPI_EXE, "-n", "2", FDS_EXE, "eqix_preview.fds"],
    cwd=RUN_DIR,
    env=env,
    stdout=log_file,
    stderr=log_file,
    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
)

print(f"FDS preview launched: PID {proc.pid}")
print(f"Log: {RUN_DIR}\\preview_run.log")
print(f"Output: {RUN_DIR}\\eqix_preview.out")
print("Run will take ~1-2 hours for 600s at 0.15m resolution.")
log_file.close()
