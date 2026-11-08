#!/usr/bin/env python3
"""Compile all Warband data with Python 3 and apply inherited localization."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
build=root/'build'
(build/'compiled').mkdir(exist_ok=True)
for line in (build/'build_module.bat').read_text().splitlines():
 line=line.strip()
 if not line.startswith('python process_'):continue
 command=line.split()[1]
 if command=='process_global_variables_unused.py':continue
 print(command,flush=True)
 subprocess.run([sys.executable,command],cwd=build,check=True)
subprocess.run([sys.executable,str(root/'scripts/finalize_fb_v74.py')],cwd=root,check=True)
print('Completed v7.4 release build and localization.',flush=True)
