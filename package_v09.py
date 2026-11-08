#!/usr/bin/env python3
"""Create cumulative and delta Warband txt plus localization-overlay deliverables."""
from pathlib import Path
import zipfile,hashlib
root=Path(__file__).resolve().parent
out=Path('/mnt/data')
for base_name,suffix,desc in [
 ('v08','游戏增量包','v0.9 增量包：仅适用于《烽烟与暗流》v0.8。'),
 ('v75','累计安装包','v0.9 累计包：适用于 FewerBandits v7.5，可一次取得 v0.1～v0.9 游戏数据。'),
]:
    baseline=root/'baseline'/base_name/'compiled'
    changed=sorted((p for p in (root/'game-data').glob('*.txt') if p.read_bytes()!=(baseline/p.name).read_bytes()),key=lambda p:p.name)
    destination=out/f'烽烟与暗流-v0.9-{suffix}.zip'
    text=desc+'''\n先备份存档和模块。将压缩包 FewerBandits 文件夹内的 .txt 文件覆盖到现有 Warband 模块根目录。\nlocalization/ 是中文增量键值文件，千万别直接用它覆盖已有的完整中文汉化 CSV；使用随包的 merge_localization.py 安全合并。\n完整说明见 README_ASHFALL_V09.md。此版已编译/静态测试，尚未在 Windows 游戏客户端实测。'''
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        z.writestr('安装说明.txt',text.encode('utf-8-sig'))
        z.write(root/'README_ASHFALL_V09.md','README_ASHFALL_V09.md')
        z.write(root/'merge_localization.py','merge_localization.py')
        for p in changed:z.write(p,'FewerBandits/'+p.name)
        for p in (root/'localization').rglob('*.csv'):z.write(p,p.relative_to(root))
    with zipfile.ZipFile(destination) as z:
        assert not z.testzip()
        for p in changed:assert z.read('FewerBandits/'+p.name)==p.read_bytes()
    print(suffix,destination.stat().st_size,'bytes',len(changed),'files')
