#!/usr/bin/env python3
"""Deliver cumulative and delta txt-only updates, no external resources overwritten."""
from pathlib import Path
import zipfile,hashlib
r=Path(__file__).resolve().parent
out=Path('/mnt/data')
data=r/'game-data';base07=r/'baseline/v07/compiled';base75=r/'baseline/v75/compiled'
assert len(list(data.glob('*.txt')))==32
assert base07.exists() and base75.exists()

def make(base,dest,description):
    changed=sorted((p for p in data.glob('*.txt') if p.read_bytes()!=(base/p.name).read_bytes()),key=lambda x:x.name)
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        z.writestr('安装说明.txt',description)
        for p in changed:z.write(p,'FewerBandits/'+p.name)
    with zipfile.ZipFile(dest) as z:
        assert not z.testzip()
        for p in changed:assert z.read('FewerBandits/'+p.name)==p.read_bytes()
    print('Created',dest.name,'files',len(changed),[p.name for p in changed],dest.stat().st_size)

make(base07,out/'烽烟与暗流-v0.8-游戏增量包.zip',
'''《烽烟与暗流》v0.8 更新包。仅适用于已安装 v0.7 的游戏模块。先备份旧文件，再将 FewerBandits 文件夹内 .txt 覆盖到你的游戏模块目录。未在 Windows 客户端实测。''')
make(base75,out/'烽烟与暗流-v0.8-累计安装包.zip',
'''《烽烟与暗流》v0.8 累计更新包。适用于已安装 FewerBandits v7.5 的模块；覆盖一次即取得 v0.1～v0.8 的改动。不是可直接运行的独立原版 Mod；须保留资源目录与 module.ini。未在 Windows 客户端实测。''')
