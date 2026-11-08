#!/usr/bin/env python3
"""Deterministic v0.6 incremental / cumulative / reproducible source delivery."""
from pathlib import Path
import zipfile,hashlib
root=Path(__file__).resolve().parent; out=root.parent
new=root/'game-data';base05=root/'baseline/v05/compiled';base75=root/'baseline/v75/compiled'
assert len(list(new.glob('*.txt')))==len(list(base05.glob('*.txt')))==len(list(base75.glob('*.txt')))==32
def changed(base):
 return sorted(p.name for p in new.glob('*.txt') if p.read_bytes()!=(base/p.name).read_bytes())
d05=changed(base05);d75=changed(base75)
assert d05==['menus.txt','quick_strings.txt','scripts.txt','simple_triggers.txt','variable_uses.txt'],d05
assert d75==['menus.txt','party_templates.txt','quick_strings.txt','scripts.txt','simple_triggers.txt','troops.txt','variable_uses.txt','variables.txt'],d75

def pack(name,items):
 path=out/name
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
  for loc,p in sorted(items):
   info=zipfile.ZipInfo(loc,date_time=(2026,11,8,3,0,0))
   info.compress_type=zipfile.ZIP_DEFLATED
   info.external_attr=0o644<<16
   z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=1)
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(set(z.namelist()))
 print(name,path.stat().st_size,hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)
 return path

def install(names):
 return [('FewerBandits/'+n,new/n) for n in names]+[('版本说明.md',root/'README_ASHFALL_V06.md')]
pack('烽烟与暗流-v0.6-游戏增量包.zip',install(d05))
cumul=pack('烽烟与暗流-v0.6-累计安装包.zip',install(d75))
with zipfile.ZipFile(cumul) as z:
 for f in new.glob('*.txt'):
  raw=z.read('FewerBandits/'+f.name) if f.name in d75 else (base75/f.name).read_bytes()
  assert raw==f.read_bytes(),f.name
print('PASS: v7.5 baseline + cumulative ZIP reconstructs all 32 data files')
files=[]
for p in root.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(root)
 if '__pycache__' in rel.parts or p.is_relative_to(root/'build/compiled'):continue
 files.append(('Ashfall-v0.6/'+rel.as_posix(),p))
pack('烽烟与暗流-v0.6-完整源码.zip',files)
print('source files',len(files),'incremental modified',len(d05),'cumulative modified',len(d75))
