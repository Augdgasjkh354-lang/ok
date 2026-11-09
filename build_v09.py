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
# v1.0 NPC对白 B-0: append-only. New dialogue rows may only be appended at the
# end of module_dialogs.py; old rows keep their IDs in order. A text-only
# change keeps the old line ONLY when the fresh token is ASCII (English source
# vs localized compiled text); a fresh non-ASCII token is an intentional
# Chinese edit and is taken (e.g. A-14 elder donation line).
def merge_dialogs():
    fresh=(compiled/'conversation.txt').read_text('utf-8').split('\n')
    old=(base/'conversation.txt').read_text('utf-8').split('\n')
    if fresh and fresh[-1]=='': fresh=fresh[:-1]
    if old and old[-1]=='': old=old[:-1]
    assert len(fresh)>=len(old), 'dialogue lines removed: append-only rule'
    out=[];changed=0
    # v1.0 NPC对白 B-3 修正: 第 0 行是文件头 ("dialogsfile version 2"), 第 1 行是对话总数,
    # 都不是对话 ID; 文件头照原样, 总数直接取新数 (追加行使总数 +1)。
    out.append(fresh[0]); out.append(fresh[1]); changed+=(fresh[1]!=old[1])
    for f,o in zip(fresh[2:],old[2:]):
        ft,ot=f.split(' '),o.split(' ')
        diff=[i for i,(x,y) in enumerate(zip(ft,ot)) if x!=y] if len(ft)==len(ot) else None
        if f==o or (diff is not None and len(diff)==1 and not ot[diff[0]].isascii() and ft[diff[0]].isascii()):
            out.append(o)
        else:
            assert ft[0]==ot[0], ('dialogue order changed',ft[0],ot[0])
            out.append(f);changed+=1
    out.extend(fresh[len(old):])  # appended new rows, taken as compiled
    (output/'conversation.txt').write_text('\n'.join(out)+'\n','utf-8')
    print('dialogue lines taken from source:',changed)
merge_dialogs()
print('v0.9 build succeeded',len(list(output.glob('*.txt'))),'data files')
