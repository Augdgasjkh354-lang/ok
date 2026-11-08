#!/usr/bin/env python3
"""Build a ready-to-copy trial package for the player's install.

Usage:
  python tools/package_trial.py PLAYER_CNS_DIR OUTPUT.zip [--note NOTE.txt]

PLAYER_CNS_DIR is a copy of the player's own TestMod/languages/cns/ (his is a
full copy of Native's cns plus the v7.4 troops.csv). It is NOT in the repo:
ask the player to upload it. The directory is copied, never modified.

The zip contains one TestMod/ folder mirroring the player's module:
  - every game-data/*.txt that differs from baseline/v74/compiled;
  - languages/cns/*.csv: only the files the mod touches (names in
    localization/cns), = the player's file merged by merge_localization.py;
  - 试玩说明.txt (from --note, or a minimal default) with the expected
    scripts.txt size so the player can check the copy worked.
Run build_v09.py and generate_localization.py first.
"""
import argparse, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

root = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument('cns_dir')
ap.add_argument('out')
ap.add_argument('--note', help='UTF-8 text file with the trial notes (what is new, where to try it)')
args = ap.parse_args()

src = Path(args.cns_dir)
if not any(src.glob('*.csv')):
    sys.exit(f'{src} has no CSV files: pass the player\'s languages/cns folder')

base = root / 'baseline' / 'v74' / 'compiled'
txt = sorted(p for p in (root / 'game-data').glob('*.txt')
             if p.read_bytes() != (base / p.name).read_bytes())
size = (root / 'game-data' / 'scripts.txt').stat().st_size

with tempfile.TemporaryDirectory() as tmp:
    mod = Path(tmp) / 'TestMod'
    cns = mod / 'languages' / 'cns'
    cns.mkdir(parents=True)
    (mod / 'module.ini').write_text('')
    for f in src.glob('*.csv'):
        shutil.copy2(f, cns / f.name)
    subprocess.run([sys.executable, str(root / 'merge_localization.py'), str(mod), 'cns'], check=True)
    for f in cns.glob('*.bak'):
        f.unlink()
    for f in cns.glob('*.csv'):
        assert f.read_bytes().startswith(b'\xef\xbb\xbf\r\n'), f'{f.name}: header line lost'

    note = Path(args.note).read_text('utf-8') if args.note else '烽烟与暗流 试玩包\n'
    note += f'''
安装：先备份 Modules\\TestMod 和存档。把本包里的 TestMod 文件夹整个复制到 Modules\\ 里，选"替换"。
核对：TestMod\\scripts.txt 应为 {size:,} 字节。汉化已经合并好，直接替换即可。
'''
    out = Path(args.out)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('试玩说明.txt', note.replace('\n', '\r\n').encode('utf-8-sig'))
        for p in txt:
            z.write(p, 'TestMod/' + p.name)
        # Only the files the mod touches; the player's other language files stay as they are.
        touched = {f.name for f in (root / 'localization' / 'cns').glob('*.csv')}
        for p in sorted(cns.glob('*.csv')):
            if p.name in touched:
                z.write(p, 'TestMod/languages/cns/' + p.name)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        for p in txt:
            assert z.read('TestMod/' + p.name) == p.read_bytes()
print(out, f'{len(txt)} txt files, scripts.txt = {size:,} bytes')
