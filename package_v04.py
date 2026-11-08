#!/usr/bin/env python3
"""Package independent v0.4 source, cumulative-over-v7.5 and delta-over-v0.3 game datasets."""
from pathlib import Path
import zipfile, hashlib
root=Path(__file__).resolve().parent
out=root.parent
game=root/'game-data'
old_v03=root/'baseline/v03/compiled'
old_v75=root/'baseline/v75/compiled'
assert len(list(game.glob('*.txt')))==len(list(old_v03.glob('*.txt')))==len(list(old_v75.glob('*.txt')))==32

def diff(old):
 return [p.name for p in sorted(game.glob('*.txt')) if (old/p.name).read_bytes()!=p.read_bytes()]
delta03=diff(old_v03)
delta75=diff(old_v75)
assert delta03==['menus.txt','party_templates.txt','quick_strings.txt','scripts.txt','simple_triggers.txt','troops.txt','variable_uses.txt'],delta03
assert delta75==['menus.txt','party_templates.txt','quick_strings.txt','scripts.txt','simple_triggers.txt','troops.txt','variable_uses.txt','variables.txt'],delta75

def pack(path,records):
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
  for name,p in sorted(records):
   info=zipfile.ZipInfo(name,date_time=(2026,11,8,0,0,0))
   info.compress_type=zipfile.ZIP_DEFLATED
   info.external_attr=0o644<<16
   z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=1)
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(set(z.namelist()))
 print(f'{path.name} size={path.stat().st_size} SHA256={hashlib.sha256(path.read_bytes()).hexdigest()}',flush=True)

def files_for_version(names):
 return [('FewerBandits/'+n,game/n) for n in names]+[('版本说明.md',root/'README_ASHFALL_V04.md')]
pack(out/'烽烟与暗流-v0.4-游戏增量包.zip',files_for_version(delta03))
pack(out/'烽烟与暗流-v0.4-累计安装包.zip',files_for_version(delta75))
# Verify cumulative installer over v7.5 reconstructs the exact compiled output.
with zipfile.ZipFile(out/'烽烟与暗流-v0.4-累计安装包.zip') as z:
 for p in game.glob('*.txt'):
  found=z.read('FewerBandits/'+p.name) if p.name in delta75 else (old_v75/p.name).read_bytes()
  assert found==p.read_bytes(),p.name
print('PASS: v7.5 baseline + v0.4 cumulative installer equals all 32 v0.4 game data files.')
files=[]
for p in root.rglob('*'):
 if not p.is_file():continue
 if '__pycache__' in p.relative_to(root).parts:continue
 if p.is_relative_to(root/'build/compiled'):continue
 files.append(('Ashfall-v0.4/'+p.relative_to(root).as_posix(),p))
pack(out/'烽烟与暗流-v0.4-完整源码.zip',files)
print('source files:',len(files),'v0.3 delta files:',len(delta03),'v7.5 cumulative delta files:',len(delta75))
