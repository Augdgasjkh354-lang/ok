#!/usr/bin/env python3
"""Deterministic source, patch-over-v0.4 and cumulative-over-v7.5 ZIP releases."""
from pathlib import Path
import hashlib,zipfile
root=Path(__file__).resolve().parent; out=root.parent
pnew=root/'game-data'; pold=root/'baseline/v04/compiled'; pv75=root/'baseline/v75/compiled'
assert len(list(pnew.glob('*.txt')))==len(list(pold.glob('*.txt')))==len(list(pv75.glob('*.txt')))==32
def delta(old):return sorted(p.name for p in pnew.glob('*.txt') if p.read_bytes()!=(old/p.name).read_bytes())
d04=delta(pold); d75=delta(pv75)
assert d04==['menus.txt','quick_strings.txt','scripts.txt','simple_triggers.txt','variable_uses.txt'],d04
assert d75==['menus.txt','party_templates.txt','quick_strings.txt','scripts.txt','simple_triggers.txt','troops.txt','variable_uses.txt','variables.txt'],d75

def pack(name,items):
 file=out/name
 with zipfile.ZipFile(file,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
  for path,p in sorted(items):
   info=zipfile.ZipInfo(path,date_time=(2026,11,8,0,0,0))
   info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16
   z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=1)
 with zipfile.ZipFile(file) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(set(z.namelist()))
 print(name, file.stat().st_size, hashlib.sha256(file.read_bytes()).hexdigest(),flush=True)
 return file

def install(names):return [('FewerBandits/'+n,pnew/n) for n in names]+[('版本说明.md',root/'README_ASHFALL_V05.md')]
pack('烽烟与暗流-v0.5-游戏增量包.zip',install(d04))
cumulative=pack('烽烟与暗流-v0.5-累计安装包.zip',install(d75))
with zipfile.ZipFile(cumulative) as z:
 for p in pnew.glob('*.txt'):
  data=z.read('FewerBandits/'+p.name) if p.name in d75 else (pv75/p.name).read_bytes()
  assert data==p.read_bytes(),p.name
print('PASS: v7.5 baseline + cumulative installer reproduces all 32 files')
files=[]
for p in root.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(root)
 if '__pycache__' in rel.parts or p.is_relative_to(root/'build/compiled'):continue
 files.append(('Ashfall-v0.5/'+rel.as_posix(),p))
pack('烽烟与暗流-v0.5-完整源码.zip',files)
print('source files',len(files),'delta04',len(d04),'delta75',len(d75))
