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
       'process_simple_triggers.py','process_dialogs.py','process_presentations.py')
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
# Dialogues: FewerBandits v7.x English dialogue text was localized into the
# compiled file (not the source), so a plain recompile would lose that Chinese.
# Keep each baseline line whose compiled form differs only in its text token;
# lines whose logic changed in source come from the fresh compile.
def merge_dialogs():
    fresh=(compiled/'conversation.txt').read_text('utf-8').split('\n')
    old=(base/'conversation.txt').read_text('utf-8').split('\n')
    assert len(fresh)==len(old), 'dialogue count changed: append-only rule needs review'
    out=[];changed=0
    for f,o in zip(fresh,old):
        ft,ot=f.split(' '),o.split(' ')
        diff=[i for i,(x,y) in enumerate(zip(ft,ot)) if x!=y] if len(ft)==len(ot) else None
        if f==o or (diff is not None and len(diff)==1 and not ot[diff[0]].isascii()):
            out.append(o)
        else:
            assert ft[0]==ot[0], ('dialogue order changed',ft[0],ot[0])
            out.append(f);changed+=1
    (output/'conversation.txt').write_text('\n'.join(out),'utf-8')
    print('dialogue lines taken from source:',changed)
merge_dialogs()
print('v0.9 build succeeded',len(list(output.glob('*.txt'))),'data files')
