#!/usr/bin/env python3
"""Validate Ashfall v0.7 compile and append-only legacy compatibility; not an engine playtest."""
from pathlib import Path
import ast, re, hashlib
root=Path(__file__).resolve().parent.parent
base=root/'baseline/v06'
new=root/'build';newdata=root/'game-data'
olddata=base/'compiled'

def require(cond,msg):
 if not cond:raise AssertionError(msg)
def parsed(path):return ast.parse(path.read_text(encoding='utf-8'))
def collection(path,name):
 for s in parsed(path).body:
  if isinstance(s,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in s.targets):
   return s.value.elts
 raise AssertionError('missing '+name+' in '+str(path))
def index(records):return {e.elts[0].value:e for e in records}
def same_node(a,b):return ast.dump(a)==ast.dump(b)
for name in ('module_scripts.py','module_game_menus.py','module_constants.py','module_simple_triggers.py'):
 parsed(new/name)
oldscripts=index(collection(base/'source/module_scripts.py','scripts'))
scripts=index(collection(new/'module_scripts.py','scripts'))
require(list(scripts)[:len(oldscripts)]==list(oldscripts),'old script IDs have shifted')
require(set(scripts)-set(oldscripts)=={'af07_retarget_refugees','af07_prepare_world'},'unexpected new scripts')
changed_scripts={name for name in oldscripts if not same_node(oldscripts[name],scripts[name])}
require(changed_scripts=={'af02_daily_update','af03_daily_update','af04_daily_update'},'unexpected legacy script changes '+repr(changed_scripts))
oldmenus=index(collection(base/'source/module_game_menus.py','game_menus'))
menus=index(collection(new/'module_game_menus.py','game_menus'))
require(list(menus)[:len(oldmenus)]==list(oldmenus),'old menu IDs shifted')
require(set(menus)-set(oldmenus)=={'af07_world'},'unexpected new menus')
changed_menus={name for name in oldmenus if not same_node(oldmenus[name],menus[name])}
require(changed_menus=={'camp'},'unexpected legacy menus changed: '+repr(changed_menus))
for f in ('module_simple_triggers.py','module_constants.py','module_troops.py','module_party_templates.py','module_dialogs.py','module_mission_templates.py'):
 require((base/'source'/f).read_bytes()==(new/f).read_bytes(),'changed legacy file '+f)
for f in ('ID_scripts.py','ID_menus.py','ID_troops.py','ID_party_templates.py'):
 before=[x for x in (base/f).read_text().splitlines() if x.strip()];after=[x for x in (new/f).read_text().splitlines() if x.strip()]
 require(after[:len(before)]==before,'legacy numeric IDs changed '+f)
for f in ('variables.txt','conversation.txt','party_templates.txt','troops.txt'):
 require((olddata/f).read_bytes()==(newdata/f).read_bytes(),'unexpected persistent ID/dlg/party change '+f)
bfiles={p.name for p in olddata.glob('*.txt')};cfiles={p.name for p in newdata.glob('*.txt')}
require(bfiles==cfiles and len(bfiles)==32,'compiled file inventory mismatch')
changed={f for f in bfiles if (olddata/f).read_bytes()!=(newdata/f).read_bytes()}
require(changed=={'scripts.txt','menus.txt','quick_strings.txt','variable_uses.txt'},'unexpected data file delta '+repr(changed))
src=(new/'module_scripts.py').read_text('utf-8')
chunk=src[src.index('  ("af02_daily_update", ['):src.index('  ("af02_prepare_status", [')]
require(chunk.index('script_af07_retarget_refugees')<chunk.index('call_script, "script_change_center_prosperity"'),'refugees can settle without destination recheck')
require('(eq, ":can_deliver", 1),' in chunk,'arrival permits unsafe towns')
require('lt, ":roll", 16' in chunk and 'lt, ":roll", 10' in chunk,'spawn pacing not adjusted')
chunk=src[src.index('  ("af03_daily_update", ['):src.index('  ("af03_settle_contract", [')]
require('lt, ":native_prosperity", 70' in chunk and 'lt, ":roll", 18' in chunk,'ambient economy/frequency balancing missing')
chunk=src[src.index('  ("af04_daily_update", ['):src.index('  ("af04_commission_raid", [')]
require('lt, ":roll", 18' in chunk,'gang event pacing missing')
ui=(new/'module_game_menus.py').read_text('utf-8')
require('mnu_af07_world' in ui and 'script_af07_prepare_world' in ui,'overview unreachable')
require('slot_af01_unrest' in src and 'slot_af03_contract_stage' in src and 'slot_af06_recovery_score' in src,'world overview lacks cross-system data')
compiled=(newdata/'scripts.txt').read_text('utf-8')
for name in ('af07_retarget_refugees','af07_prepare_world'):
 require(bool(re.search('^'+name+r' -1\s',compiled,re.M)),'new script not compiled '+name)
require('menu_af07_world ' in (newdata/'menus.txt').read_text('utf-8'),'new overview not compiled')
print('PASS: 2 appended scripts, 1 appended menu; 3 intentional old script revisions')
print('PASS: original troop/party/template/dialog files, global variables and trigger order preserved')
print('PASS: all v0.6 numerical script and menu IDs retained; no new slots')
print('PASS: old game-data unchanged except:',', '.join(sorted(changed)))
print('NOTE: compile/static checks only; no Windows client test')
