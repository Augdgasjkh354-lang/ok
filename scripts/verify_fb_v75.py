#!/usr/bin/env python3
"""Static regression checks for FewerBandits v7.5 release from v7.4."""
from pathlib import Path
import ast
import hashlib
import json
root=Path(__file__).resolve().parent.parent
export=root/'game-data'
base=root/'baseline/v74'

def must(ok,reason):
    if not ok:raise AssertionError(reason)

def lines(p):return p.read_text(encoding='utf-8').splitlines()

for name in ('module_constants.py','module_scripts.py','module_dialogs.py','module_game_menus.py'):
    ast.parse((root/'build'/name).read_text(encoding='utf-8'), filename=name)

old_vars=lines(base/'variables.txt')
new_vars=lines(export/'variables.txt')
must(new_vars[:len(old_vars)]==old_vars,'v7.4 variable IDs moved')
must(new_vars[len(old_vars):]==['g_fb75_gossip_wait','g_fb75_view_lord'],'unexpected v7.5 global variables')
for id_file in ('ID_scripts.py','ID_menus.py'):
    old=[line for line in lines(base/id_file) if line.strip()]
    now=[line for line in lines(root/'build'/id_file) if line.strip()]
    must(now[:len(old)]==old,id_file+' changed an existing ID')

old_hash=json.loads((base/'release_sha256.json').read_text(encoding='utf-8'))
actual_files={f.name for f in export.glob('*.txt')}
must(actual_files==set(old_hash),'release .txt files missing or introduced')
changed={name for name in actual_files if hashlib.sha256((export/name).read_bytes()).hexdigest()!=old_hash[name]}
expected={'conversation.txt','menus.txt','quick_strings.txt','scripts.txt','variable_uses.txt','variables.txt'}
must(changed==expected,'unexpected changed game-data files: '+str(changed^expected))

conversation=(export/'conversation.txt').read_text(encoding='utf-8')
menus=(export/'menus.txt').read_text(encoding='utf-8')
scripts=(export/'scripts.txt').read_text(encoding='utf-8')
constants=(root/'build/module_constants.py').read_text(encoding='utf-8')
for text in ('请再过{reg59}天来打听','近来没有新的可靠传闻','陛下，我掌握了贵族秘密交易的证据'):
    must(text in conversation,'unlocalized or missing dialogue: '+text)
for text in ('menu_fb75_intel_book','menu_fb75_intel_detail','menu_fb75_debt_detail','menu_fb75_debug','宫廷政治情报簿'):
    must(text in menus,'missing menu '+text)
for text in ('fb75_gossip_wait','fb75_book_overview','fb75_find_next_intel','fb75_debug_make_evidence'):
    must(text in scripts,'missing script '+text)
must('slot_fb75_last_rumor_token = 641' in constants,'slot 641 changed')

# Every newly referenced script/menu has a compiler-provided stable identifier.
ids=(root/'build/ID_scripts.py').read_text(encoding='utf-8')
menus_ids=(root/'build/ID_menus.py').read_text(encoding='utf-8')
for script in ('fb75_gossip_wait','fb75_book_overview','fb75_find_next_intel','fb75_prepare_intel_detail','fb75_find_next_debtor','fb75_debug_make_evidence','fb75_debug_try_flip'):
    must('script_'+script+' =' in ids,'no compiled ID for '+script)
for menu in ('fb75_intel_book','fb75_intel_detail','fb75_debt_detail','fb75_intel_help','fb75_debug'):
    must('menu_'+menu+' =' in menus_ids,'no compiled ID for '+menu)

print('PASS: Python syntax, 1,272 original globals, old menu/script IDs, 6-file release delta, localization, new IDs.')
