#!/usr/bin/env python3
"""Bundle entire buildable v0.9 sources with v0.8 compiled compatibility baseline."""
from pathlib import Path
import zipfile
root=Path(__file__).resolve().parent
out=Path('/mnt/data/烽烟与暗流-v0.9-完整源码.zip')
files=[]
for p in root.rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(root)
    if any(x in rel.parts for x in ('__pycache__','.git','.pytest_cache')):continue
    if p.name.endswith(('.pyc','.log','.tmp')):continue
    files.append(p)
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
    for p in sorted(files): z.write(p,'Ashfall-v0.9/'+str(p.relative_to(root)))
with zipfile.ZipFile(out) as z:
    assert not z.testzip()
    assert 'Ashfall-v0.9/build_v09.py' in z.namelist()
    assert 'Ashfall-v0.9/build/module_scripts.py' in z.namelist()
    assert 'Ashfall-v0.9/localization/cns/game_menus.csv' in z.namelist()
print(out.name,out.stat().st_size,'bytes',len(files),'files')
