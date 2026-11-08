#!/usr/bin/env python3
"""Reproducible v0.2 archives. Install incremental files over v0.1."""
from pathlib import Path
import hashlib,zipfile
root=Path(__file__).resolve().parent
out=root.parent
base=root/'baseline/v01/compiled'
game=root/'game-data'
changed=sorted(p.name for p in game.glob('*.txt') if (base/p.name).read_bytes()!=p.read_bytes())
expected=['menus.txt','party_templates.txt','quick_strings.txt','scripts.txt','simple_triggers.txt','variable_uses.txt']
assert changed==expected,(changed,expected)

def pack(path, entries):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for name,p in sorted(entries,key=lambda x:x[0]):
            info=zipfile.ZipInfo(name,date_time=(2026,11,8,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=8)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist()))
    print(path.name, path.stat().st_size, hashlib.sha256(path.read_bytes()).hexdigest())

pack(out/'烽烟与暗流-v0.2-游戏增量包.zip',
 [(f'FewerBandits/{file}',game/file) for file in changed]+
 [('版本说明.md',root/'README_ASHFALL_V02.md')])

exclude={'__pycache__','.DS_Store'}
entries=[]
for p in root.rglob('*'):
    if not p.is_file() or any(x in exclude for x in p.relative_to(root).parts):continue
    if p.is_relative_to(root/'build/compiled'):continue
    entries.append(('Ashfall-v0.2/'+p.relative_to(root).as_posix(),p))
pack(out/'烽烟与暗流-v0.2-完整源码.zip',entries)
print('Delta:',', '.join(changed),'source files:',len(entries))
