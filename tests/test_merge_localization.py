#!/usr/bin/env python3
"""Static checks for the localization merge tools and the merge-only package layout.

Run: python tests/test_merge_localization.py
The PowerShell tool is only checked statically here; it still needs a Windows run.
"""
import subprocess, sys, tempfile, zipfile
from pathlib import Path

root = Path(__file__).resolve().parent.parent
merge = root / 'merge_localization.py'


def run(module, *extra, ok=True):
    r = subprocess.run([sys.executable, str(merge), str(module), *extra], capture_output=True, text=True)
    assert (r.returncode == 0) == ok, r.stdout + r.stderr
    return r


with tempfile.TemporaryDirectory() as tmp:
    mod = Path(tmp) / 'TestMod'
    cns = mod / 'languages' / 'cns'
    cns.mkdir(parents=True)
    (mod / 'module.ini').write_text('')
    original = '﻿trp_swadian_knight|斯 瓦 迪 亚 骑 士　\ntrp_af04_greywolf_captain|旧名\n'
    (cns / 'troops.csv').write_text(original, 'utf-8')

    run(mod)
    raw = (cns / 'troops.csv').read_bytes()
    assert raw.startswith(b'\xef\xbb\xbf\r\n'), 'first line must stay an empty header line (engine skips it)'
    merged = (cns / 'troops.csv').read_text('utf-8-sig')
    assert 'trp_swadian_knight|斯 瓦 迪 亚 骑 士　' in merged, 'native translation lost'
    assert 'trp_af04_greywolf_captain|裂 旗　' in merged, 'mod-owned key not refreshed'
    assert 'trp_af04_saltraven_captain_pl|' in merged, 'new key not inserted'
    assert (cns / 'troops.csv.bak').read_text('utf-8') == original
    for name in ('game_menus.csv', 'quick_strings.csv', 'party_templates.csv'):
        assert not (cns / name).exists(), f'{name} must not be created (shadows native Chinese)'

    run(mod)  # idempotent, and the first backup is never overwritten
    assert (cns / 'troops.csv').read_text('utf-8-sig') == merged
    assert (cns / 'troops.csv.bak').read_text('utf-8') == original

    gbk = '兵|骑士\n'.encode('gbk')
    (cns / 'troops.csv').write_bytes(gbk)
    run(mod, ok=False)
    assert (cns / 'troops.csv').read_bytes() == gbk, 'non-UTF-8 file must be left untouched'

    run(Path(tmp) / 'nope', ok=False)  # not a module folder

    # Only cn_s present -> auto-select cn_s
    mod2 = Path(tmp) / 'Mod2'
    (mod2 / 'languages' / 'cn_s').mkdir(parents=True)
    (mod2 / 'module.ini').write_text('')
    (mod2 / 'languages' / 'cn_s' / 'troops.csv').write_text(original, 'utf-8')
    run(mod2)
    assert 'trp_af04_saltraven_captain|' in (mod2 / 'languages' / 'cn_s' / 'troops.csv').read_text('utf-8-sig')
    assert not (mod2 / 'languages' / 'cns').exists()

    # Package layout: no CSV under an engine-readable name; merge tools bundled.
    out = Path(tmp) / 'dist'
    subprocess.run([sys.executable, str(root / 'package_v09.py'), str(out)], check=True, capture_output=True)
    zips = sorted(out.glob('*.zip'))
    assert len(zips) == 3, zips
    for zp in zips:
        with zipfile.ZipFile(zp) as z:
            names = z.namelist()
            assert not [n for n in names if n.endswith('.csv') and not n.endswith('.merge.csv')]
            assert not [n for n in names if n.startswith(('localization/', 'languages/'))]
            loc = '汉化_需合并_不要直接复制/'
            for need in ('双击合并汉化.bat', 'merge_localization.ps1', 'merge_localization.py',
                         'cns/troops.merge.csv', 'cn_s/troops.merge.csv'):
                assert loc + need in names, (zp.name, need)
            bat = z.read(loc + '双击合并汉化.bat')
            assert bat.isascii() and b'\r\n' in bat and b'\n' not in bat.replace(b'\r\n', b'')
            ps1 = z.read(loc + 'merge_localization.ps1')
            assert ps1.startswith(b'\xef\xbb\xbf'), 'ps1 needs UTF-8 BOM for Windows PowerShell 5.1'
            assert z.read('FewerBandits/scripts.txt') == (root / 'game-data' / 'scripts.txt').read_bytes()

        # The packaged Python merger must work from the package layout (*.merge.csv).
        ext = Path(tmp) / ('x_' + zp.stem)
        with zipfile.ZipFile(zp) as z:
            z.extractall(ext)
        mod3 = Path(tmp) / ('m_' + zp.stem)
        (mod3 / 'languages' / 'cns').mkdir(parents=True)
        (mod3 / 'module.ini').write_text('')
        (mod3 / 'languages' / 'cns' / 'troops.csv').write_text(original, 'utf-8')
        subprocess.run([sys.executable, str(ext / '汉化_需合并_不要直接复制' / 'merge_localization.py'), str(mod3)],
                       check=True, capture_output=True)
        assert 'trp_af04_blackpine_captain|' in (mod3 / 'languages' / 'cns' / 'troops.csv').read_text('utf-8-sig')
        assert not list((mod3 / 'languages' / 'cns').glob('*.merge.csv'))

    with zipfile.ZipFile(out / '烽烟与暗流-v0.9-从v7.4累计包.zip') as z:
        base = root / 'baseline' / 'v74' / 'compiled'
        expected = [f for f in (root / 'game-data').glob('*.txt') if f.read_bytes() != (base / f.name).read_bytes()]
        assert len([n for n in z.namelist() if n.startswith('FewerBandits/')]) == len(expected)

print('merge/package checks passed')
