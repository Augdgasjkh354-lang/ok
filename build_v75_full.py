#!/usr/bin/env python3
"""Compile all Warband data with Python 3 and apply inherited localization."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
build=root/'build'
(build/'compiled').mkdir(exist_ok=True)
# Preserve all original v7.4 global variable indices, including the five v7.4 globals.
# The compiler appends only v7.5 names after this historical prefix.
(build/'compiled'/'variables.txt').write_bytes((root/'baseline'/'v74'/'variables.txt').read_bytes())
for line in (build/'build_module.bat').read_text().splitlines():
 line=line.strip()
 if not line.startswith('python process_'):continue
 command=line.split()[1]
 if command=='process_global_variables_unused.py':continue
 print(command,flush=True)
 subprocess.run([sys.executable,command],cwd=build,check=True)
subprocess.run([sys.executable,str(root/'scripts/finalize_fb_v75.py')],cwd=root,check=True)
print('Completed v7.5 release build and localization.',flush=True)
