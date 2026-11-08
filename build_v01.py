#!/usr/bin/env python3
"""Reproducible Ashfall v0.1 incremental build, inheriting localized v7.5."""
from pathlib import Path
import shutil, subprocess, sys
root=Path(__file__).resolve().parent
build=root/'build'
compiled=build/'compiled'
# The release v7.5 game-data is the strict compiler baseline.
base=root/'baseline/v75/compiled'
assert (base/'variables.txt').is_file(), 'Missing clean v7.5 baseline.'
if compiled.exists(): shutil.rmtree(compiled)
shutil.copytree(base,compiled)
for step in (
    'process_global_variables.py',
    'process_scripts.py',
    'process_mission_tmps.py',
    'process_game_menus.py',
    'process_simple_triggers.py',
    'process_dialogs.py',
):
    print('Compiling',step,flush=True)
    subprocess.run([sys.executable,step],cwd=build,check=True)
# The input baseline is ALREADY localized v7.5. Replaying old localization
# scripts would double-translate (and fail). Keep the unchanged v7.5 dialogue
# output byte-exact; the new feature does not edit module_dialogs.py.
out=root/'game-data'
out.mkdir(exist_ok=True)
for file in compiled.glob('*.txt'):
    shutil.copy2(file,out/file.name)
shutil.copy2(base/'conversation.txt',out/'conversation.txt')
assert (out/'conversation.txt').read_bytes()==(base/'conversation.txt').read_bytes()

print('Ashfall v0.1 build complete.', flush=True)
