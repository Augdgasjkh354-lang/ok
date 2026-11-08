#!/usr/bin/env python3
"""Produce deterministic v0.7 incremental, cumulative and source distributions."""
from pathlib import Path
import hashlib, zipfile
root=Path(__file__).resolve().parent
output=root.parent
new=root/'game-data'
base06=root/'baseline/v06/compiled'
base75=root/'baseline/v75/compiled'
assert len(list(new.glob('*.txt')))==len(list(base06.glob('*.txt')))==len(list(base75.glob('*.txt')))==32

def delta(base):
    return sorted(p.name for p in new.glob('*.txt') if p.read_bytes()!=(base/p.name).read_bytes())
d06=delta(base06);d75=delta(base75)
assert d06==['menus.txt','quick_strings.txt','scripts.txt','variable_uses.txt'],d06
assert d75==['menus.txt','party_templates.txt','quick_strings.txt','scripts.txt','simple_triggers.txt','troops.txt','variable_uses.txt','variables.txt'],d75

def pack(name, files):
    target=output/name
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for archive_name,path in sorted(files):
            meta=zipfile.ZipInfo(archive_name,date_time=(2026,11,8,4,30,0))
            meta.compress_type=zipfile.ZIP_DEFLATED
            meta.external_attr=0o644<<16
            z.writestr(meta,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=1)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist()))
    sha=hashlib.sha256(target.read_bytes()).hexdigest()
    print(f'{target.name}: {target.stat().st_size} bytes sha256={sha}',flush=True)
    return target

def install(names):
    return [('FewerBandits/'+name,new/name) for name in names]+[('版本说明.md',root/'README_ASHFALL_V07.md')]
pack('烽烟与暗流-v0.7-游戏增量包.zip',install(d06))
cumulative=pack('烽烟与暗流-v0.7-累计安装包.zip',install(d75))
with zipfile.ZipFile(cumulative) as z:
    for data in new.glob('*.txt'):
        source=z.read('FewerBandits/'+data.name) if data.name in d75 else (base75/data.name).read_bytes()
        assert source==data.read_bytes(),data.name
print('PASS: cumulative ZIP + v7.5 baseline reconstruct all 32 data files')
files=[]
for p in root.rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(root)
    if '__pycache__' in rel.parts or p.is_relative_to(root/'build/compiled'):continue
    files.append(('Ashfall-v0.7/'+rel.as_posix(),p))
pack('烽烟与暗流-v0.7-完整源码.zip',files)
print('source files:',len(files),'v0.6 delta:',len(d06),'v7.5 cumulative delta:',len(d75))
