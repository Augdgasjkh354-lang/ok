#!/usr/bin/env python3
"""v0.9 reproducible Module System compile over bundled v0.8 baseline."""
from pathlib import Path
import shutil,subprocess,sys
root=Path(__file__).resolve().parent
base=root/'baseline/v08/compiled'
build=root/'build';compiled=build/'compiled'
assert base.exists(), 'v0.8 base missing'
if compiled.exists():shutil.rmtree(compiled)
shutil.copytree(base,compiled)
steps=('process_troops.py','process_party_tmps.py','process_global_variables.py',
       'process_scripts.py','process_mission_tmps.py','process_game_menus.py',
       'process_simple_triggers.py','process_dialogs.py')
for step in steps:
    print('Compiling',step,flush=True)
    subprocess.run([sys.executable,step],cwd=build,check=True)
# Keep historical quick-string IDs (script opcodes are positional) while repairing
# three legacy UTF-8 -> cp1254 mojibake display payloads.
qpath=compiled/'quick_strings.txt'
lines=qpath.read_text('utf-8').splitlines()
fixed=0
for i,line in enumerate(lines):
    if line.startswith('qstr_æ'):
        key=line.split(' ',1)[0]
        value='无有效线索' if 'æœ' in key else '暂无'
        lines[i]=key+' '+value
        fixed+=1
assert fixed==3, f'Unexpected corrupt quick strings: {fixed}'
qpath.write_text('\n'.join(lines)+'\n','utf-8')
output=root/'game-data';output.mkdir(exist_ok=True)
for f in compiled.glob('*.txt'):shutil.copy2(f,output/f.name)
shutil.copy2(base/'conversation.txt',output/'conversation.txt')
print('v0.9 build succeeded',len(list(output.glob('*.txt'))),'data files')
