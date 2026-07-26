#!/usr/bin/env python3
'''Root-level entry point for the Monte Carlo PRA.

The published paper (Fire, fire-4382023, Appendix A.2) instructs readers to run
python pra_simulation.py from the repository root. The implementation lives in
pra/pra_simulation.py; this shim runs it so the printed instruction works as written.
'''
import runpy, sys, pathlib

target = pathlib.Path(__file__).parent / 'pra' / 'pra_simulation.py'
sys.path.insert(0, str(target.parent))
runpy.run_path(str(target), run_name='__main__')
