#!/usr/bin/env python3
"""Apply four source-file edits to a clean v7.1 Module System directory."""
import hashlib,json,shutil,sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
if len(sys.argv)!=2:raise SystemExit('Usage: python apply_fb72.py PATH_TO_V71_BUILD')
target=Path(sys.argv[1]).resolve()
checks=json.loads((root/'scripts/baseline_sha256.json').read_text())
for n,digest in checks.items():
 p=target/n
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
  raise SystemExit('Refusing to overwrite: expected pristine v7.1 file '+str(p))
for n in checks:
 p=target/n
 shutil.copy2(p,p.with_name(n+'.pre_v72'))
 shutil.copy2(root/'sources'/n,p)
print('Applied four v7.2 source changes with backup copies')
