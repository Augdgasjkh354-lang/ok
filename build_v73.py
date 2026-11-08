#!/usr/bin/env python3
"""Run the bundled Python 3 compatible Warband Module System into game-data/."""
from pathlib import Path
import subprocess,sys
r=Path(__file__).resolve().parent
b=r/'build'
(b/'compiled').mkdir(exist_ok=True)
for line in (b/'build_module.bat').read_text().splitlines():
 line=line.strip()
 if not line.startswith('python process_'):continue
 program=line.split()[1]
 if program=='process_global_variables_unused.py':continue
 print(program,flush=True)
 subprocess.run([sys.executable,program],cwd=b,check=True)
subprocess.run([sys.executable,str(r/'scripts/finalize_fb_v73.py')],cwd=r,check=True)
print('Compiled and localized game-data/',flush=True)
