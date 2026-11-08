#!/usr/bin/env python3
"""Ashfall v0.3 static and save-compatibility gate; no in-game validation claimed."""
from pathlib import Path
import ast, re, hashlib
root=Path(__file__).resolve().parent.parent
old=root/'baseline/v02';baseline=old/'compiled';game=root/'game-data';build=root/'build'
def must(ok,msg):
    if not ok:raise AssertionError(msg)
def read(p):return p.read_text(encoding='utf-8')
def records(path,name):
    tree=ast.parse(read(path))
    for e in tree.body:
        if isinstance(e,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in e.targets):
            return e.value.elts
    raise AssertionError('missing '+name)
def indexed(items):return {v.elts[0].value:v for v in items}
for file in ('module_scripts.py','module_party_templates.py','module_game_menus.py','module_constants.py','module_simple_triggers.py'):
    ast.parse(read(build/file))
old_s=indexed(records(old/'source/module_scripts.py','scripts'))
new_s=indexed(records(build/'module_scripts.py','scripts'))
expected_new={'af03_faction_at_war','af03_find_route','af03_find_enemy_route','af03_can_accept',
              'af03_spawn_convoy','af03_accept_contract','af03_confirm_victory',
              'af03_escort_watch','af03_daily_update','af03_settle_contract',
              'af03_prepare_contract','af03_debug_dispatch','af03_cancel_contract'}
must(set(new_s)-set(old_s)==expected_new,'new scripts diff')
for n,v in old_s.items():
    must(n in new_s,'missing old script '+n)
    if n!='game_event_party_encounter':
        must(ast.dump(v)==ast.dump(new_s[n]),'existing script modified: '+n)
old_m=indexed(records(old/'source/module_game_menus.py','game_menus'))
new_m=indexed(records(build/'module_game_menus.py','game_menus'))
expected_m={'af03_contract_board','af03_journal','af03_convoy','af03_debug'}
must(set(new_m)-set(old_m)==expected_m,'new menus diff')
for n,v in old_m.items():
    must(n in new_m,'missing old menu '+n)
    if n not in {'town','camp','camp_cheat','total_victory'}:
        must(ast.dump(v)==ast.dump(new_m[n]),'existing menu changed: '+n)
old_pt=records(old/'source/module_party_templates.py','party_templates')
new_pt=records(build/'module_party_templates.py','party_templates')
must(len(new_pt)==len(old_pt)+1,'party template count mismatch')
for x,y in zip(old_pt,new_pt):must(ast.dump(x)==ast.dump(y),'existing party template modified')
must(new_pt[-1].elts[0].value=='af03_supply_convoy','new convoy template missing')
old_tr=records(old/'source/module_simple_triggers.py','simple_triggers')
new_tr=records(build/'module_simple_triggers.py','simple_triggers')
must(len(new_tr)==len(old_tr)+2,'new triggers count')
for a,b in zip(old_tr,new_tr):must(ast.dump(a)==ast.dump(b),'old trigger modified')
for file in ('ID_scripts.py','ID_menus.py','ID_party_templates.py'):
    a=[line for line in read(old/file).splitlines() if line.strip()]
    b=[line for line in read(build/file).splitlines() if line.strip()]
    must(b[:len(a)]==a,'old IDs shifted: '+file)
must(read(baseline/'variables.txt')==read(game/'variables.txt'),'global variables index changed')
q0=read(baseline/'quick_strings.txt').splitlines();q1=read(game/'quick_strings.txt').splitlines()
must(q0[1:]==q1[1:len(q0)],'old quick_strings reordered')
names0={x.name for x in baseline.glob('*.txt')};names1={x.name for x in game.glob('*.txt')}
must(names0==names1,'compiled data file set altered')
changed={n for n in names0 if (baseline/n).read_bytes()!=(game/n).read_bytes()}
expected_delta={'menus.txt','party_templates.txt','quick_strings.txt','scripts.txt','simple_triggers.txt','variable_uses.txt'}
must(changed==expected_delta,'unexpected game-file changes: '+repr(changed^expected_delta))
for f in ('conversation.txt','strings.txt','troops.txt','quests.txt','factions.txt','parties.txt'):
    must((baseline/f).read_bytes()==(game/f).read_bytes(),'legacy data changed: '+f)
old_constants=read(old/'source/module_constants.py');new_constants=read(build/'module_constants.py')
for id in range(690,708):
    must(not re.search(r'^slot_\w+\s*=\s*'+str(id)+r'\b',old_constants,re.M),'old slot collision '+str(id))
    must(len(re.findall(r'^slot_af03_\w+\s*=\s*'+str(id)+r'\b',new_constants,re.M))==1,'slot id missing/duplicate '+str(id))
# Explicit behavioral contracts: player-only battle success; no duplicate money payout; bounded traffic.
assert '"script_af03_confirm_victory"' in read(build/'module_game_menus.py')
assert 'slot_af03_contract_stage, 2' in read(build/'module_scripts.py')
assert 'store_num_parties_of_template' in read(build/'module_scripts.py')
assert 'slot_af03_contract_guard_ticks' in read(build/'module_scripts.py')
assert '"script_af03_cancel_contract"' in read(build/'module_game_menus.py')
compiled_scripts=read(game/'scripts.txt');compiled_menus=read(game/'menus.txt');compiled_templates=read(game/'party_templates.txt')
for v in expected_new:
    must(re.search(r'^'+re.escape(v)+r' -1\s',compiled_scripts,re.M),'compiled script missing '+v)
for v in ('menu_af03_contract_board','menu_af03_journal','menu_af03_convoy','mno_af03_take_escort','mno_af03_take_intercept','mno_af03_journal_cancel'):
    must(v in compiled_menus,'compiled menu missing '+v)
must('pt_af03_supply_convoy' in compiled_templates,'missing convoy compiled template')
print('PASS: 13 new scripts, 4 new menus, 1 new party template, 2 triggers, slots 690-707.')
print('PASS: original IDs, old political scripts/menus, quick_strings prefix and global variable numbers are unchanged.')
print('PASS: player victory-specific interception, bounded transport, contract exit and legacy resources audited.')
print('DELTA: '+', '.join(sorted(changed)))
print('NOTE: Windows client, battle callback paths, AI pathfinding, save loading NOT tested.')
