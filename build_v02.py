#!/usr/bin/env python3
"""Build Ashfall v0.2 from v0.1 localized, deterministic compiled baseline."""
from pathlib import Path
import shutil, subprocess, sys
root=Path(__file__).resolve().parent
build=root/'build'
compiled=build/'compiled'
base=root/'baseline/v01/compiled'
assert base.is_dir(), 'Missing bundled v0.1 baseline'
if compiled.exists():shutil.rmtree(compiled)
shutil.copytree(base,compiled)
for step in (
  'process_party_tmps.py',
  'process_global_variables.py',
  'process_scripts.py',
  'process_mission_tmps.py',
  'process_game_menus.py',
  'process_simple_triggers.py',
  'process_dialogs.py',
):
    print('Compiling',step,flush=True)
    subprocess.run([sys.executable,step],cwd=build,check=True)
out=root/'game-data'
out.mkdir(exist_ok=True)
for p in compiled.glob('*.txt'): shutil.copy2(p,out/p.name)
# Localization artifact: unchanged political dialogue must stay byte-for-byte identical
shutil.copy2(base/'conversation.txt',out/'conversation.txt')
assert (out/'conversation.txt').read_bytes()==(base/'conversation.txt').read_bytes()
print('Ashfall v0.2 compile succeeded')
