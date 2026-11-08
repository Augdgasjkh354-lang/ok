#!/usr/bin/env python3
"""Ashfall v0.6 source/compiled regression checks, not a game-client playtest."""
from pathlib import Path
import ast,re
root=Path(__file__).resolve().parent.parent
old=root/'baseline/v05'
base=old/'compiled';cur=root/'game-data';b=root/'build'
def require(condition,message):
 if not condition:raise AssertionError(message)
def text(p):return p.read_text('utf-8')
def records(p,name):
 for stmt in ast.parse(text(p)).body:
  if isinstance(stmt,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in stmt.targets):
   return stmt.value.elts
 raise AssertionError('missing collection '+name)
def index(records):return {e.elts[0].value:e for e in records}
for file in ('module_scripts.py','module_game_menus.py','module_simple_triggers.py','module_constants.py'):
 ast.parse(text(b/file))
old_scripts=index(records(old/'source/module_scripts.py','scripts'))
new_scripts=index(records(b/'module_scripts.py','scripts'))
expected={
 'af06_check_siege','af06_prepare_siege','af06_scout','af06_sabotage',
 'af06_bribe','af06_supply','af06_on_capture','af06_daily_update',
 'af06_prepare_recovery','af06_rebuild'}
require(set(new_scripts)-set(old_scripts)==expected,'new scripts differ from design')
for key,node in old_scripts.items():
 require(key in new_scripts,'deleted old script: '+key)
 if key!='give_center_to_faction_aux':
  require(ast.dump(node)==ast.dump(new_scripts[key]),'changed legacy script: '+key)
old_menus=index(records(old/'source/module_game_menus.py','game_menus'))
new_menus=index(records(b/'module_game_menus.py','game_menus'))
require(set(new_menus)-set(old_menus)=={'af06_siege_ops','af06_recovery','af06_debug'},'new menus differ')
for key,node in old_menus.items():
 require(key in new_menus,'deleted old menu: '+key)
 if key not in {'town','castle_besiege','siege_started_defender','camp_cheat'}:
  require(ast.dump(node)==ast.dump(new_menus[key]),'changed legacy menu: '+key)
a=records(old/'source/module_simple_triggers.py','simple_triggers')
c=records(b/'module_simple_triggers.py','simple_triggers')
require(len(c)==len(a)+1 and all(ast.dump(x)==ast.dump(y) for x,y in zip(a,c)),'old simple triggers shifted')
for name in ('module_troops.py','module_party_templates.py','module_dialogs.py','module_mission_templates.py'):
 require(text(old/'source'/name)==text(b/name),'legacy source changed '+name)
for name in ('ID_scripts.py','ID_menus.py','ID_troops.py','ID_party_templates.py'):
 a=[ln.strip() for ln in text(old/name).splitlines() if ln.strip()]
 c=[ln.strip() for ln in text(b/name).splitlines() if ln.strip()]
 require(c[:len(a)]==a,'old engine IDs shifted: '+name)
const0=text(old/'source/module_constants.py');const1=text(b/'module_constants.py')
slots=re.findall(r'^slot_af06_(\w+)\s*=\s*(\d+)',const1,re.M)
require(len(slots)==8 and sorted(int(x[1]) for x in slots)==list(range(780,788)),'v0.6 slot ids invalid')
for n,v in slots:require(not re.search(r'^slot_\w+\s*=\s*'+v+r'\b',const0,re.M),'slot collision: '+v)
files0={p.name for p in base.glob('*.txt')};files1={p.name for p in cur.glob('*.txt')}
require(files0==files1 and len(files0)==32,'32-data-file inventory changed')
changed={name for name in files0 if (base/name).read_bytes()!=(cur/name).read_bytes()}
expect={'menus.txt','quick_strings.txt','scripts.txt','simple_triggers.txt','variable_uses.txt'}
require(changed==expect,'unexpected compiled output delta '+repr(changed^expect))
for name in ('variables.txt','conversation.txt','troops.txt','party_templates.txt','parties.txt','factions.txt','quests.txt','mission_templates.txt'):
 require((base/name).read_bytes()==(cur/name).read_bytes(),'stable game file changed '+name)
source=text(b/'module_scripts.py')
menu=text(b/'module_game_menus.py')
oncapture=source[source.index('  ("af06_on_capture", ['):source.index('  ("af06_daily_update", [')]
require('slot_af01_previous_faction' in oncapture and 'slot_af01_change_unrest' not in oncapture, 'old village changes miswired')
require('"script_af01_change_unrest"' in oncapture,'v0.1 unrest hook missing')
require('slot_af06_capture_token' in oncapture and 'kingdoms_begin' in oncapture,'capture transition missing')
conquest=source[source.index('  ("give_center_to_faction_aux",'):source.index('  # script_change_troop_faction')]
require('"script_af06_on_capture"' in conquest,'actual conquest script unhooked')
sabo=source[source.index('  ("af06_sabotage", ['):source.index('  ("af06_bribe", [')]
require(sabo.index('troop_remove_gold')<sabo.index('slot_party_food_store, ":food"'),'sabotage rewards before payment')
require('"script_center_get_food_consumption"' in sabo and 'slot_af06_sabotage_token' in sabo,'native siege costs/cooldown missing')
supply=source[source.index('  ("af06_supply", ['):source.index('  ("af06_on_capture", [')]
require('troop_remove_items, "trp_player", "itm_grain", 2' in supply,'supply not paying cargo')
require('"script_center_get_food_store_limit"' in supply and 'slot_party_food_store' in supply,'real siege supply not modified')
rebuild=source[source.index('  ("af06_rebuild", ['):]
require('slot_af06_rebuild_token' in rebuild and '"script_change_center_prosperity"' in rebuild and '"script_af01_change_unrest"' in rebuild,'rebuild not connected to native economy')
require('"script_af06_daily_update"' in text(b/'module_simple_triggers.py'),'daily recovery trigger missing')
require('"mnu_af06_siege_ops"' in menu and '"mnu_af06_recovery"' in menu,'menu not wired')
require('粮仓情报：{s41}' in menu,'scouting intel is not hidden')
require('reg(81)' not in menu[menu.index('  ("af06_siege_ops",'):].split('"none"',1)[0],'bad GUI register token')
compiled_scripts=text(cur/'scripts.txt');compiled_menus=text(cur/'menus.txt')
for name in expected:
 require(bool(re.search(r'^'+name+r' -1\s',compiled_scripts,re.M)),'missing compiled script '+name)
for name in ('af06_siege_ops','af06_recovery','af06_debug'):
 require('menu_'+name+' ' in compiled_menus,'missing compiled menu '+name)
print('PASS: 10 scripts, 3 menus, 1 appended trigger and 8 new center slots')
print('PASS: v0.5 old menus/scripts IDs, global IDs and 27 untouched compiled files preserved')
print('PASS: real siege food supply, paid sabotage, garrison bribery and real conquest hook compiled')
print('DELTA v0.5 -> v0.6:', ', '.join(sorted(changed)))
print('NOTE: No Windows Warband gameplay test performed')
