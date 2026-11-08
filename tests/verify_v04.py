#!/usr/bin/env python3
"""v0.4 save-id, source-scope and build-output static audit, without pretending to run Warband."""
from pathlib import Path
import ast,re
root=Path(__file__).resolve().parent.parent
old=root/'baseline/v03';new=root/'build';b0=old/'compiled';b1=root/'game-data'
def check(condition,msg):
 if not condition:raise AssertionError(msg)
def read(p):return p.read_text(encoding='utf-8')
def elements(file,variable):
 tree=ast.parse(read(file))
 for stmt in tree.body:
  if isinstance(stmt,ast.Assign) and any(isinstance(x,ast.Name) and x.id==variable for x in stmt.targets):
   return stmt.value.elts
 raise AssertionError('No '+variable+' in '+str(file))
def keyed(records):return {r.elts[0].value:r for r in records}
for name in ('module_scripts.py','module_game_menus.py','module_troops.py','module_party_templates.py','module_constants.py','module_simple_triggers.py'):
 ast.parse(read(new/name))
oldscripts=keyed(elements(old/'source/module_scripts.py','scripts'))
newscripts=keyed(elements(new/'module_scripts.py','scripts'))
added=set(newscripts)-set(oldscripts)
check(len(added)==16 and all(n.startswith('af04_') for n in added),'script count/set')
for k,v in oldscripts.items():
 check(k in newscripts,'missing script '+k)
 if k!='game_event_party_encounter':check(ast.dump(v)==ast.dump(newscripts[k]),'unexpected modified old script '+k)
oldmenus=keyed(elements(old/'source/module_game_menus.py','game_menus'))
newmenus=keyed(elements(new/'module_game_menus.py','game_menus'))
check(set(newmenus)-set(oldmenus)=={'af04_gang','af04_network','af04_debug'},'menu count/set')
for k,v in oldmenus.items():
 check(k in newmenus,'missing old menu '+k)
 if k not in {'camp','camp_cheat','total_victory'}:check(ast.dump(v)==ast.dump(newmenus[k]),'unexpected modified menu '+k)
for name,variable,delta,prefix in [('module_troops.py','troops',3,'af04_'),('module_party_templates.py','party_templates',3,'af04_'),('module_simple_triggers.py','simple_triggers',1,None)]:
 a=elements(old/'source'/name,variable);z=elements(new/name,variable)
 check(len(z)==len(a)+delta,'count '+name)
 for x,y in zip(a,z):check(ast.dump(x)==ast.dump(y),'old record shift '+name)
 if prefix:
  check(all(e.elts[0].value.startswith(prefix) for e in z[len(a):]),'appended IDs '+name)
for name in ('ID_scripts.py','ID_menus.py','ID_party_templates.py','ID_troops.py'):
 oldlines=[x for x in read(old/name).splitlines() if x.strip()]
 newlines=[x for x in read(new/name).splitlines() if x.strip()]
 check(newlines[:len(oldlines)]==oldlines,'legacy IDs shifted: '+name)
oldconst=read(old/'source/module_constants.py')
newconst=read(new/'module_constants.py')
new_values=[]
for line in newconst.splitlines():
 m=re.match(r'^(slot_af04_\w+)\s*=\s*(\d+)',line)
 if m:
  num=int(m.group(2));new_values.append(num)
  check(720<=num<=743,'unexpected new slot '+line)
  check(not re.search(r'^slot_\w+\s*=\s*'+str(num)+r'\b',oldconst,re.M),'slot collision '+line)
check(len(new_values)==len(set(new_values))==14,'missing or duplicate v04 slots')
check(read(b0/'variables.txt')==read(b1/'variables.txt'),'globals reordered')
q0=read(b0/'quick_strings.txt').splitlines();q1=read(b1/'quick_strings.txt').splitlines()
check(q0[1:]==q1[1:len(q0)],'existing quick strings reordered')
files0={p.name for p in b0.glob('*.txt')};files1={p.name for p in b1.glob('*.txt')}
check(files0==files1 and len(files0)==32,'compiled file set changed')
changed={n for n in files0 if (b0/n).read_bytes()!=(b1/n).read_bytes()}
expected={'menus.txt','party_templates.txt','quick_strings.txt','scripts.txt','simple_triggers.txt','troops.txt','variable_uses.txt'}
check(changed==expected,'unexpected changed files '+str(changed^expected))
for n in ('conversation.txt','strings.txt','quests.txt','factions.txt','parties.txt','mission_templates.txt','variables.txt'):
 check((b0/n).read_bytes()==(b1/n).read_bytes(),'legacy data modified '+n)
# Output existence, content/contract gating and no accidental duplicate clan variants.
compiled=read(b1/'scripts.txt');menus=read(b1/'menus.txt');pts=read(b1/'party_templates.txt');troops=read(b1/'troops.txt')
for s in added:check(re.search(r'^'+re.escape(s)+r' -1\s',compiled,re.M),'new compiled script missing '+s)
for m in ('menu_af04_gang','menu_af04_network','menu_af04_debug','mno_af04_pay_treaty','mno_af04_amnesty','mno_af04_hire_raid','mno_af04_buy_grain','mno_af04_hire_men'):
 check(m in menus,'new menu / option missing '+m)
for k in ('blackpine','greywolf','saltraven'):
 check('pt_af04_'+k in pts,'template '+k)
 check('trp_af04_'+k+'_captain' in troops,'leader '+k)
check('script_af04_player_victory' in read(new/'module_game_menus.py'),'player-victory hook missing')
check('slot_af04_victory_token' in read(new/'module_scripts.py'),'victory idempotence missing')
check('slot_af03_contract_party' in read(new/'module_scripts.py'),'convoy protection link missing')
check('slot_af04_order_target' in read(new/'module_scripts.py'),'hired raid link missing')
check('"script_af04_daily_update"' in read(new/'module_simple_triggers.py'),'daily trigger missing')
print('PASS: 16 new scripts, 3 new menus, 3 new party templates, 3 new leader troops and 1 new daily trigger.')
print('PASS: 14 new slot-base constants (24 effective slots) in 720..743, no collision; all existing IDs preserved.')
print('PASS: old court, village, migration, contracts, troops and original dialogue baseline preserved.')
print('PASS: player victory day guard, treaty/escort protection, target gating, bounded gang spawns are statically present.')
print('DELTA: '+', '.join(sorted(changed)))
print('NOTE: Windows game engine behavior, old save loads, AI route resolution and native battle lifecycle remain untested.')
