#!/usr/bin/env python3
"""Reproducible Ashfall v0.6 incremental compile over bundled v0.5 outputs."""
from pathlib import Path
import shutil, subprocess, sys
root=Path(__file__).resolve().parent
build=root/'build'; compiled=build/'compiled'; base=root/'baseline/v05/compiled'
assert base.is_dir(), 'Bundled v0.5 compiled baseline missing'
if compiled.exists(): shutil.rmtree(compiled)
shutil.copytree(base,compiled)
for step in ('process_troops.py','process_party_tmps.py','process_global_variables.py',
             'process_scripts.py','process_mission_tmps.py','process_game_menus.py',
             'process_simple_triggers.py','process_dialogs.py'):
 print('Compiling',step,flush=True)
 subprocess.run([sys.executable,step],cwd=build,check=True)
out=root/'game-data';out.mkdir(exist_ok=True)
for p in compiled.glob('*.txt'):shutil.copy2(p,out/p.name)
shutil.copy2(base/'conversation.txt',out/'conversation.txt')
assert (out/'conversation.txt').read_bytes()==(base/'conversation.txt').read_bytes()
print('Ashfall v0.6 compile succeeded')
