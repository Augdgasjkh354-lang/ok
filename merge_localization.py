#!/usr/bin/env python3
"""Merge mod-localized CSV additions with a player's existing Warband localization.
Usage: python merge_localization.py PATH_TO_WARBAND_MODULE [cns|cn_s]
Only changes mod-localized keys. Never destroys untranslated native keys.
"""
import argparse,shutil
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('module',help='Your current Warband Modules/<mod> directory')
p.add_argument('lang',nargs='?',default='cns',choices=['cns','cn_s'])
args=p.parse_args()
source=Path(__file__).resolve().parent/'localization'/args.lang
target=Path(args.module)/'languages'/args.lang
target.mkdir(parents=True,exist_ok=True)

def parse(lines):
  records={};order=[]
  for raw in lines.splitlines():
    if '|' not in raw:continue
    key,value=raw.split('|',1)
    key=key.lstrip('\ufeff')
    if key not in records:order.append(key)
    records[key]=value
  return order,records
for incoming in sorted(source.glob('*.csv')):
  dest=target/incoming.name
  previous=dest.read_text('utf-8-sig') if dest.is_file() else ''
  add=incoming.read_text('utf-8-sig')
  order,existing=parse(previous)
  new_order,new=parse(add)
  inserted=updated=0
  for key in new_order:
    if key not in existing:
      order.append(key);existing[key]=new[key];inserted+=1
    elif key.startswith(('menu_af','mno_af','trp_af','pt_af')) or key.startswith(('menu_fb','mno_fb','trp_fb','pt_fb')) or key.startswith('qstr_æ'):
      if existing[key]!=new[key]: existing[key]=new[key];updated+=1
  if dest.exists():shutil.copy2(dest,dest.with_suffix(dest.suffix+'.bak'))
  dest.write_text(''.join(f'{key}|{existing[key]}\n' for key in order),encoding='utf-8-sig')
  print(f'{incoming.name}: new={inserted}, updated={updated}, total={len(order)}')
print('Completed. Original files (if any) backed up as *.csv.bak')
