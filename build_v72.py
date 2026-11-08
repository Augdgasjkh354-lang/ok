#!/usr/bin/env python3
"""Build game-data/ with the bundled Python 3 compatible Warband Module System."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
b=root/'build'
(b/'compiled').mkdir(exist_ok=True)
# The build folder ships with the complete v7.1 variables.txt index to keep old IDs stable.
for line in (b/'build_module.bat').read_text().splitlines():
 line=line.strip()
 if line.startswith('python process_'):
  command=line.split()[1]
  if command=='process_global_variables_unused.py':
   continue # diagnostic-only metadata generator; not required by Warband
  print(command,flush=True)
  subprocess.run([sys.executable,command],cwd=b,check=True)
subprocess.run([sys.executable,str(root/'scripts/finalize_fb_v72.py')],cwd=root,check=True)
print('Finished game-data/',flush=True)
