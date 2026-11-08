#!/usr/bin/env python3
"""Merge mod-localized CSV additions with a player's existing Warband localization.

Usage: python merge_localization.py PATH_TO_WARBAND_MODULE [cns|cn_s]

Only adds new keys and refreshes mod-owned keys; never deletes or rewrites the
player's existing native translations. Windows players without Python can use
tools/merge_localization.ps1 (double-click the bundled .bat), which follows the
same rules.

Source CSVs are looked up next to this script in either layout:
  - repository:   localization/<lang>/<name>.csv
  - release zip:  <lang>/<name>.merge.csv   (renamed so the engine ignores them
                                              even if someone copies them by hand)
"""
import argparse, shutil, sys
from pathlib import Path

OWNED_PREFIXES = ('menu_af', 'mno_af', 'trp_af', 'pt_af',
                  'menu_fb', 'mno_fb', 'trp_fb', 'pt_fb', 'qstr_æ')
MERGE_SUFFIX = '.merge.csv'


def find_source(lang):
    here = Path(__file__).resolve().parent
    for cand in (here / lang, here / 'localization' / lang, here.parent / 'localization' / lang):
        if cand.is_dir() and any(cand.glob('*.csv')):
            return cand
    sys.exit(f'找不到 {lang} 的汉化源文件（应位于本脚本旁的 {lang}/ 或 localization/{lang}/）。')


def target_name(path):
    name = path.name
    return name[:-len(MERGE_SUFFIX)] + '.csv' if name.endswith(MERGE_SUFFIX) else name


def read_utf8(path):
    try:
        return path.read_bytes().decode('utf-8-sig')
    except UnicodeDecodeError:
        sys.exit(f'{path} 不是 UTF-8 编码（可能是 GBK）。为避免损坏原汉化，本次未修改任何文件。')


def fallback_file(module, lang, name):
    """Full native translation shipped with the game, if any."""
    module = module.resolve()
    for cand in (module.parent.parent / 'languages' / lang / name,
                 module.parent / 'Native' / 'languages' / lang / name):
        if cand.is_file() and cand.resolve() != (module / 'languages' / lang / name).resolve():
            return cand
    return None


def parse(text):
    records, order = {}, []
    for raw in text.splitlines():
        if '|' not in raw:
            continue
        key, value = raw.split('|', 1)
        key = key.lstrip('﻿')
        if key not in records:
            order.append(key)
        records[key] = value
    return order, records


def merge(previous, incoming):
    order, existing = parse(previous)
    new_order, new = parse(incoming)
    inserted = updated = 0
    for key in new_order:
        if key not in existing:
            order.append(key); existing[key] = new[key]; inserted += 1
        elif key.startswith(OWNED_PREFIXES) and existing[key] != new[key]:
            existing[key] = new[key]; updated += 1
    return ''.join(f'{k}|{existing[k]}\n' for k in order), inserted, updated, len(order)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('module', help='Your current Warband Modules/<mod> directory')
    p.add_argument('lang', nargs='?', choices=['cns', 'cn_s'],
                   help='默认自动选择：languages/ 下已有 cns 用 cns，只有 cn_s 用 cn_s')
    args = p.parse_args(argv)
    module = Path(args.module.strip().strip('"'))
    if not (module / 'module.ini').is_file():
        sys.exit(f'{module} 里没有 module.ini，不像模组文件夹。请指向 Modules\\TestMod 这一层。')
    lang = args.lang
    if lang is None:
        lang = 'cn_s' if (module / 'languages' / 'cn_s').is_dir() and not (module / 'languages' / 'cns').is_dir() else 'cns'
    source = find_source(lang)
    target = module / 'languages' / lang

    # Read and validate everything first so a bad file aborts before any write.
    plans = []
    for incoming in sorted(source.glob('*.csv')):
        dest = target / target_name(incoming)
        previous = read_utf8(dest) if dest.is_file() else ''
        incoming_text = read_utf8(incoming)
        # A module file holding only this mod's keys (missing, or created by an
        # older merge) shadows the game's full Chinese file, turning native menus
        # English. Seed it from the full file the game used to fall back to.
        old_keys, _ = parse(previous)
        new_keys = set(parse(incoming_text)[0])
        if all(k in new_keys for k in old_keys):
            base = fallback_file(module, lang, dest.name)
            if base:
                previous = read_utf8(base)
                print(f'{dest.name}: 已从 {base} 补入完整原版译文')
            else:
                print(f'{dest.name}: 未找到游戏自带的完整 {dest.name}，该文件只含本 Mod 条目，原版相关文字可能显示英文')
        plans.append((dest, *merge(previous, incoming_text)))

    target.mkdir(parents=True, exist_ok=True)
    for dest, text, inserted, updated, total in plans:
        backup = dest.with_name(dest.name + '.bak')
        if dest.exists() and not backup.exists():
            shutil.copy2(dest, backup)  # keep the very first original; reruns never overwrite it
        dest.write_text(text, encoding='utf-8-sig')
        print(f'{dest.name}: 新增={inserted}, 更新={updated}, 共={total}')
    print(f'完成：已合并到 {target}。原文件首次合并前的版本保存为 *.csv.bak')


if __name__ == '__main__':
    main()
