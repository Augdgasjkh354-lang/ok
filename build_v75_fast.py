#!/usr/bin/env python3
"""Deterministic fast v7.5 Warband compiler from bundled raw v7.4 output.
This build is for the v7.5 changes only. Use build_v75_full.py if you edit
unrelated native modules whose compiled data must also be regenerated.
"""
from pathlib import Path
import shutil
import subprocess
import sys
root=Path(__file__).resolve().parent
build=root/'build'
compiled=build/'compiled'
base=root/'baseline/v74/compiled'
if not (base/'quick_strings.txt').exists():
    raise RuntimeError('Missing v7.4 compiler baseline: baseline/v74/compiled')
if compiled.exists():
    shutil.rmtree(compiled)
shutil.copytree(base,compiled)
# Original v7.4 variable numbers are fixed. New globals are append-only.
(compiled/'variables.txt').write_bytes((root/'baseline/v74/variables.txt').read_bytes())
# None of the earlier exporter source files changed. Recompile everything
# that references v7.5 variables/new scripts or contributes new quick strings.
for step in (
    'process_global_variables.py',
    'process_scripts.py',
    'process_mission_tmps.py',
    'process_game_menus.py',
    'process_simple_triggers.py',
    'process_dialogs.py',
):
    print('Compiling',step,flush=True)
    subprocess.run([sys.executable,step], cwd=build,check=True)
subprocess.run([sys.executable,str(root/'scripts/finalize_fb_v75.py')],cwd=root,check=True)
print('Completed deterministic v7.5 incremental build.',flush=True)
