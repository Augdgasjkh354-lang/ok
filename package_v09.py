#!/usr/bin/env python3
"""Create v0.9 player packages: game .txt files plus a merge-only localization folder.

Usage: python package_v09.py [OUTPUT_DIR]      (default: dist/)

Warband only reads fixed CSV names (troops.csv, game_menus.csv ...), so the mod's
translations can never live in separate files. To make accidental overwrites
impossible, packages never ship CSVs under those engine names: they are renamed
*.merge.csv and placed in a folder that says it must be merged, together with a
no-Python double-click merge tool (tools/merge_localization.ps1 + .bat).
"""
from pathlib import Path
import sys, zipfile

root = Path(__file__).resolve().parent
out = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'dist'
out.mkdir(parents=True, exist_ok=True)
LOC_DIR = '汉化_需合并_不要直接复制'
BAT = '双击合并汉化.bat'

VARIANTS = [
    ('v08', '游戏增量包', '适用于已安装《烽烟与暗流》v0.8 的模组。'),
    ('v75', '累计安装包', '适用于已安装 FewerBandits v7.5 的模组，一次取得 v0.1～v0.9 全部游戏数据。'),
    ('v74', '从v7.4累计包', '适用于已安装 FewerBandits v7.4 的模组，已包含 v7.5，无需另装 v7.5 增量包。'),
]

INSTALL = '''《卡拉迪亚：烽烟与暗流》v0.9 —— {desc}

一、游戏数据（必做）
1. 先备份整个 Modules\\TestMod 文件夹和存档。
2. 打开本包的 FewerBandits 文件夹，全选里面的 {n} 个 .txt，复制到 Modules\\TestMod\\ 根目录。
   出现“替换或跳过文件”时选“替换目标中的文件”。不要把 FewerBandits 文件夹本身拖进去。
3. 核对：TestMod\\scripts.txt 应为 {size} 字节（约 {kb} KB）。大小没变说明没有替换成功。
4. 进游戏扎营，应能看到“烽烟与暗流：卡拉迪亚战局总览”等新选项。

二、中文汉化（只能合并，不能复制）
游戏每种语言只认固定文件名（如 troops.csv），本 Mod 的译文必须写进你已有的同名文件。
直接复制会把你原有的完整汉化整份盖掉，所以本包里的汉化文件已改名为 *.merge.csv，复制过去游戏也不会读取。
正确做法：打开“{loc}”文件夹，把 Modules\\TestMod 文件夹拖到“{bat}”上（或双击后按提示拖入）。
工具只新增本 Mod 的条目，不改动原版兵种名等译文；首次合并前的原文件会保存为 *.csv.bak。
已装 Python 的也可以运行：python merge_localization.py "...\\Modules\\TestMod"

三、说明
- v7.4 的全局变量顺序未改动，旧存档理论上可载入，但尚未实机验证，请另存副本测试。
- 本包只含 .txt 与汉化增量，不是可独立运行的完整 Mod；保留 module.ini、map.txt、SceneObj 等原有文件。
- 此版已编译并通过静态检查，尚未在 Windows 游戏客户端实测。完整说明见 README_ASHFALL_V09.md。
'''


def build(base_name, suffix, desc):
    baseline = root / 'baseline' / base_name / 'compiled'
    changed = sorted((p for p in (root / 'game-data').glob('*.txt')
                      if p.read_bytes() != (baseline / p.name).read_bytes()), key=lambda p: p.name)
    scripts = root / 'game-data' / 'scripts.txt'
    note = INSTALL.format(desc=desc, n=len(changed), size=f'{scripts.stat().st_size:,}',
                          kb=-(-scripts.stat().st_size // 1024), loc=LOC_DIR, bat=BAT)
    destination = out / f'烽烟与暗流-v0.9-{suffix}.zip'
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=7) as z:
        z.writestr('安装说明.txt', note.replace('\n', '\r\n').encode('utf-8-sig'))
        z.write(root / 'README_ASHFALL_V09.md', 'README_ASHFALL_V09.md')
        for p in changed:
            z.write(p, 'FewerBandits/' + p.name)
        z.write(root / 'tools' / BAT, f'{LOC_DIR}/{BAT}')
        z.write(root / 'tools' / 'merge_localization.ps1', f'{LOC_DIR}/merge_localization.ps1')
        z.write(root / 'merge_localization.py', f'{LOC_DIR}/merge_localization.py')
        for p in sorted((root / 'localization').rglob('*.csv')):
            lang = p.parent.name
            z.write(p, f'{LOC_DIR}/{lang}/{p.stem}.merge.csv')
    with zipfile.ZipFile(destination) as z:
        assert z.testzip() is None
        for p in changed:
            assert z.read('FewerBandits/' + p.name) == p.read_bytes()
        assert not [n for n in z.namelist() if n.endswith('.csv') and not n.endswith('.merge.csv')]
    print(suffix, destination, destination.stat().st_size, 'bytes', len(changed), 'txt files')
    return destination


if __name__ == '__main__':
    for variant in VARIANTS:
        build(*variant)
