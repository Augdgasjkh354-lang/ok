#!/usr/bin/env python3
"""Ashfall v0.5 static regression gate. Not a Windows gameplay test."""
from pathlib import Path
import ast,re
root=Path(__file__).resolve().parent.parent
old=root/'baseline/v04'
base=old/'compiled'; current=root/'game-data'; build=root/'build'
def check(condition,msg):
 if not condition:raise AssertionError(msg)
def txt(p):return p.read_text(encoding='utf-8')
def records(p,name):
 for stmt in ast.parse(txt(p)).body:
  if isinstance(stmt,ast.Assign) and any(isinstance(x,ast.Name) and x.id==name for x in stmt.targets):
   return stmt.value.elts
 raise AssertionError('missing '+name)
def indexed(v):return {r.elts[0].value:r for r in v}
for file in ('module_scripts.py','module_game_menus.py','module_simple_triggers.py','module_constants.py'):
 ast.parse(txt(build/file))
olds=indexed(records(old/'source/module_scripts.py','scripts'))
news=indexed(records(build/'module_scripts.py','scripts'))
new_scripts=set(news)-set(olds)
expected={'af05_daily_plots','af05_confirm_strike','af05_find_case','af05_investigate','af05_find_proven_case','af05_deliver_report','af05_silence_case','af05_prepare_ledger'}
check(new_scripts==expected,'unexpected new script set: '+repr(new_scripts^expected))
for key,value in olds.items():
 check(key in news,'missing old script '+key)
 if key not in {'af04_harass_convoy','af04_daily_update','fb74_player_report'}:
  check(ast.dump(value)==ast.dump(news[key]),'unexpected edited script: '+key)
oldm=indexed(records(old/'source/module_game_menus.py','game_menus'))
newm=indexed(records(build/'module_game_menus.py','game_menus'))
check(set(newm)-set(oldm)=={'af05_ledger','af05_debug'},'unexpected new menus')
for key,value in oldm.items():
 check(key in newm,'missing old menu '+key)
 if key not in {'camp','camp_cheat'}:
  check(ast.dump(value)==ast.dump(newm[key]),'unexpected menu modification: '+key)
a=records(old/'source/module_simple_triggers.py','simple_triggers')
b=records(build/'module_simple_triggers.py','simple_triggers')
check(len(b)==len(a)+1 and all(ast.dump(x)==ast.dump(y) for x,y in zip(a,b)),'triggers shifted')
for name in ('module_troops.py','module_party_templates.py','module_dialogs.py','module_mission_templates.py'):
 check(txt(old/'source'/name)==txt(build/name),'legacy source changed '+name)
for name in ('ID_scripts.py','ID_menus.py','ID_troops.py','ID_party_templates.py'):
 a=[x for x in txt(old/name).splitlines() if x.strip()]
 b=[x for x in txt(build/name).splitlines() if x.strip()]
 check(b[:len(a)]==a,'save ID shift '+name)
const0=txt(old/'source/module_constants.py');const1=txt(build/'module_constants.py')
slots=re.findall(r'^slot_af05_(\w+)\s*=\s*(\d+)',const1,re.M)
check(len(slots)==8 and sorted(int(x[1]) for x in slots)==list(range(760,768)),'new slot inventory')
for n,v in slots:
 check(not re.search(r'^slot_\w+\s*=\s*'+v+r'\b',const0,re.M),'slot collision '+v)
check(txt(base/'variables.txt')==txt(current/'variables.txt'),'global-variable ID shift')
q0=txt(base/'quick_strings.txt').splitlines();q1=txt(current/'quick_strings.txt').splitlines()
check(q0[1:]==q1[1:len(q0)],'compiled string prefix change')
files0={x.name for x in base.glob('*.txt')};files1={x.name for x in current.glob('*.txt')}
check(files0==files1 and len(files0)==32,'file list change')
changed={x for x in files0 if (base/x).read_bytes()!=(current/x).read_bytes()}
expect={'menus.txt','quick_strings.txt','scripts.txt','simple_triggers.txt','variable_uses.txt'}
check(changed==expect,'unexpected compiled data delta: '+str(changed^expect))
for file in ('conversation.txt','troops.txt','party_templates.txt','variables.txt','mission_templates.txt','factions.txt','parties.txt','quests.txt'):
 check((base/file).read_bytes()==(current/file).read_bytes(),'legacy runtime data changed: '+file)
src=txt(build/'module_scripts.py')
# Reject accidental evidence without real transport damage, or illicit player contract credit.
harass=src[src.index('  ("af04_harass_convoy", ['):src.index('  ("af04_daily_update", [')]
check(harass.index('party_remove_members')<harass.index('script_af05_confirm_strike'),'evidence before real casualty')
check('eq, ":hired", 1' in harass and 'eq, ":hired", 2' in harass,'AI vs player sponsorship distinction')
check('script_af03_confirm_victory' not in harass,'AI compensated as player victory')
plot=src[src.index('  ("af05_daily_plots", ['):src.index('  ("af05_confirm_strike", [')]
for term in ('slot_fb71_fief_grievance','slot_fb72_ambition','slot_fb71_cabal_leader','slot_town_lord','slot_af04_order_target','slot_af03_role'):
 check(term in plot,'unlinked political prerequisite '+term)
check('slot_af05_resolved_token' in src and 'slot_af05_known_token' in src,'case consume/evidence missing')
royal=src[src.index('  (\"fb74_player_report\", ['):src.index('  # Daily faded suspicion',src.index('  (\"fb74_player_report\", ['))]
check('slot_af05_resolved_token' in royal,'legacy court reporting could leave a saleable old incident')
check('script_fb74_expose' in src[src.index('  ("af05_deliver_report", ['):], 'royal court consequences missing')
compiled=txt(current/'scripts.txt');menus=txt(current/'menus.txt')
for key in new_scripts:check(' '+key+' -1 ' in compiled or re.search('^'+key+r' -1\s',compiled,re.M),'script not compiled '+key)
for name in ('af05_ledger','af05_debug'):
 check('menu_'+name+' ' in menus,'menu missing '+name)
print('PASS v0.5: 8 new scripts, 2 menus, 1 trigger, 8 party/troop slots, unchanged old indexes and globals')
print('PASS v0.5: evidence only from actual damage; one-shot report/blackmail, player contract isolated')
print('PASS v0.5: 32 game files present; unchanged political dialogue/troops/templates')
print('DELTA v0.4 -> v0.5:',', '.join(sorted(changed)))
print('NOTE: Warband engine simulation and old-save load not tested')
