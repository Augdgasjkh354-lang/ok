#!/usr/bin/env python3
"""Static compiler / save-compatibility and feature contract checks (not client gameplay)."""
from pathlib import Path
import ast, re, hashlib
root=Path(__file__).resolve().parent.parent
b=root/'baseline/v01'
bas=b/'compiled'; game=root/'game-data'; build=root/'build'

def must(condition,message):
    if not condition: raise AssertionError(message)
def read(p): return p.read_text(encoding='utf-8')
def records(path,name):
    tree=ast.parse(read(path))
    for el in tree.body:
        if isinstance(el,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in el.targets):
            return el.value.elts
    raise AssertionError(name)
def map_records(path,name):return {i.elts[0].value:i for i in records(path,name)}

names={'scripts':'module_scripts.py','game_menus':'module_game_menus.py','party_templates':'module_party_templates.py','simple_triggers':'module_simple_triggers.py'}
for target in ['module_scripts.py','module_party_templates.py','module_game_menus.py','module_simple_triggers.py','module_constants.py']:
    ast.parse(read(build/target))

old=map_records(b/'source/module_scripts.py','scripts'); new=map_records(build/'module_scripts.py','scripts')
new_names=set(new)-set(old)
expected={'af02_find_safe_town','af02_spawn_refugees','af02_spawn_deserters','af02_daily_update','af02_prepare_status'}
must(new_names==expected,'new script set wrong: '+str(new_names^expected))
for k,v in old.items():
    must(k in new,'old script deleted: '+k)
    if k!='game_event_party_encounter':must(ast.dump(new[k])==ast.dump(v),'unexpected edit to old script: '+k)
menus_old=map_records(b/'source/module_game_menus.py','game_menus')
menus_new=map_records(build/'module_game_menus.py','game_menus')
must(set(menus_new)-set(menus_old)=={'af02_refugees','af02_deserters'},'new menus mismatch')
for k,v in menus_old.items():
    if k not in {'af01_village_status','af01_debug'}:
        must(ast.dump(v)==ast.dump(menus_new[k]),'unexpected old menu edit: '+k)
pts_old=records(b/'source/module_party_templates.py','party_templates')
pts_new=records(build/'module_party_templates.py','party_templates')
must(len(pts_new)==len(pts_old)+2,'templates count')
for i,item in enumerate(pts_old):must(ast.dump(item)==ast.dump(pts_new[i]),'old party template changed')
must([x.elts[0].value for x in pts_new[-2:]]==['af02_refugees','af02_deserters'],'template order')
old_tr=records(b/'source/module_simple_triggers.py','simple_triggers')
new_tr=records(build/'module_simple_triggers.py','simple_triggers')
must(len(new_tr)==len(old_tr)+1,'extra trigger count')
for a,c in zip(old_tr,new_tr):must(ast.dump(a)==ast.dump(c),'old trigger modified')
for filename in ('ID_scripts.py','ID_menus.py','ID_party_templates.py'):
    old_ids=[line for line in read(b/filename).splitlines() if line.strip()]
    new_ids=[line for line in read(build/filename).splitlines() if line.strip()]
    must(new_ids[:len(old_ids)]==old_ids,'old indices reordered: '+filename)
must(read(bas/'variables.txt')==read(game/'variables.txt'),'new global variables or shifted IDs')
old_qs=read(bas/'quick_strings.txt').splitlines()
new_qs=read(game/'quick_strings.txt').splitlines()
must(new_qs[1:len(old_qs)]==old_qs[1:],'existing quick string indices changed')
oldfiles={x.name for x in bas.glob('*.txt')}
newfiles={x.name for x in game.glob('*.txt')}
must(oldfiles==newfiles,'compiled data file set changed')
changed={x for x in oldfiles if (bas/x).read_bytes()!=(game/x).read_bytes()}
expected_changed={'menus.txt','party_templates.txt','quick_strings.txt','scripts.txt','simple_triggers.txt','variable_uses.txt'}
must(changed==expected_changed,'delta mismatch '+str(changed^expected_changed))
for x in ('conversation.txt','strings.txt','factions.txt','troops.txt'):
    must((bas/x).read_bytes()==(game/x).read_bytes(),x+' unexpectedly changed')
old_consts=read(b/'source/module_constants.py')
new_consts=read(build/'module_constants.py')
for slot in range(670,680):
    must(not re.search(r'^slot_\w+\s*=\s*'+str(slot)+r'\b',old_consts,re.M),'slot collision '+str(slot))
    must(len(re.findall(r'^slot_af02_\w+\s*=\s*'+str(slot)+r'\b',new_consts,re.M))==1,'new slot '+str(slot))
must('slot_af02_popular_support' not in new_consts,'unrequested new popularity statistic')
compiled_scripts=read(game/'scripts.txt'); compiled_menus=read(game/'menus.txt'); pts=read(game/'party_templates.txt')
for item in expected:
    must(re.search(r'^'+re.escape(item)+r' -1\s',compiled_scripts,re.M),'compiled script missing: '+item)
for item in ('menu_af02_refugees','menu_af02_deserters','mno_af02_refugee_help','mno_af02_deserter_attack'):
    must(item in compiled_menus, 'compiled menu missing: '+item)
for item in ('pt_af02_refugees','pt_af02_deserters'):
    must(item in pts,'template missing: '+item)
must('民心' not in read(build/'module_constants.py')[-1600:],'wrong separate popularity stat')
print('PASS: all v0.1 script/menu/template IDs stable; 5 new scripts; 2 new templates; 2 new menus; 1 new daily trigger; no new globals.')
print('PASS: preexisting scripts unchanged except encounter routing; v0.1 menus only extended; slots 670-679 unique.')
print('PASS: quick strings prefix, original dialogues, factions/troops/other resources unchanged.')
print('DELTA:',', '.join(sorted(changed)))
print('NOTE: Windows game client not run.')
