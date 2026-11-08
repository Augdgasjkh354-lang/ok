#!/usr/bin/env python3
"""Append-only legacy compatibility and source-level consistency checks; not a Warband client test."""
from pathlib import Path
import ast, hashlib, json, re
r=Path(__file__).resolve().parent.parent
b=r/'baseline/v07'; build=r/'build'; out=r/'game-data'

def check(x,msg):
    if not x:raise AssertionError(msg)

def ast_collection(p,key):
    t=ast.parse(p.read_text('utf8'))
    for a in t.body:
        if isinstance(a,ast.Assign) and any(isinstance(z,ast.Name) and z.id==key for z in a.targets):
            return [(x.elts[0].value,ast.dump(x)) for x in a.value.elts]
    raise AssertionError('missing '+key)

for filename,key,expected in [
    ('module_scripts.py','scripts',{'af08_record_rumor','af08_refresh_jurisdictions','af08_score_lord',
    'af08_governance_tick','af08_pick_patrol','af08_patrol_relief','af08_prepare_desk','af08_ask_town_rumor'}),
    ('module_game_menus.py','game_menus',{'af08_desk','af08_town_rumor'})]:
    old=ast_collection(b/'source'/filename,key); newer=ast_collection(build/filename,key)
    check([x[0] for x in newer[:len(old)]]==[x[0] for x in old],filename+' older IDs reordered')
    added=set(x[0] for x in newer[len(old):]);check(added==expected,filename+' unexpected added entries '+str(added))
    print('APPEND-ONLY',filename,'+',len(added))

checks=['ID_scripts.py','ID_menus.py','ID_party_templates.py','ID_troops.py']
for x in checks:
    if not (b/x).exists():continue
    before=[z for z in (b/x).read_text('utf8').splitlines() if z.strip()];after=[z for z in (build/x).read_text('utf8').splitlines() if z.strip()]
    check(after[:len(before)]==before,'numeric ID shift: '+x)

for x in ['module_dialogs.py','module_party_templates.py','module_troops.py','module_mission_templates.py']:
    # v07 source of this file is still authoritative even if no baseline copy
    p=b/'source'/x
    if p.exists():check((build/x).read_bytes()==p.read_bytes(),'modified '+x)

for x in ['conversation.txt','variables.txt','party_templates.txt','troops.txt','parties.txt','factions.txt','quests.txt']:
    check((b/'compiled'/x).read_bytes()==(out/x).read_bytes(),'unsafe compiled change: '+x)
check(len(list(out.glob('*.txt')))==32,'not exactly 32 game files')
oldnames={x.name for x in (b/'compiled').glob('*.txt')}
changed={x for x in oldnames if (b/'compiled'/x).read_bytes()!=(out/x).read_bytes()}
check(changed=={'scripts.txt','menus.txt','quick_strings.txt','simple_triggers.txt','variable_uses.txt'},
      'unexpected generated file changes '+str(changed))

s=(build/'module_scripts.py').read_text('utf8');m=(build/'module_game_menus.py').read_text('utf8')
check('script_af08_pick_patrol' in s and 'spai_patrolling_around_center' in s,'AI patrol not connected')
check('slot_af08_negligence' in s and 'slot_troop_controversy' in s,'crown accountability disconnected')
check('slot_party_food_store' in s and 'slot_af08_initial_guard_size' in s,'food system disconnected')
check('is_between, ":destination", walled_centers_begin, walled_centers_end' in s,'castle destinations unavailable')
check('slot_af08_contract_last' in s,'contract cooldown absent')
check('lt, ":grain", 4' in s and 'lt, ":count", 6' in s,'grain costs unbalanced')
check('af08_desk_entry' in m and 'af08_town_rumor_entry' in m,'entry UI unavailable')
check('mnu_af08_desk' in m and 'mnu_af08_town_rumor' in m,'menu destinations missing')
check('script_af08_ask_town_rumor' in m,'town rumor ungrounded')
check('"af08_ask_town_rumor"' in s and 'slot_af08_rumor_center' in s,'town rumor does not persist')
check('{reg(81)}' not in s,'bad quick-string placeholder')
check('script_indict_lord_for_treason' not in s[s.index('  ("af08_record_rumor", ['):],
      'v0.8 should not automatically indict or confiscate fiefs')
# Existing numerical slots below new block must not be mutated.
check((b/'source/module_constants.py').read_text('utf8') in (build/'module_constants.py').read_text('utf8'),
      'changed existing slot constant declarations')
nums=[]
for name,v in re.findall(r'^slot_af08_(\w+)\s*=\s*(\d+)',(build/'module_constants.py').read_text('utf8'),re.M):nums.append(int(v))
check(len(nums)==15 and len(nums)==len(set(nums)), 'new slot collision or missing slot')
check(not any('slot_af08' in line for line in (b/'source/module_constants.py').read_text('utf8').splitlines()),'overlap with v07')

sha={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(out.glob('*.txt'))}
(r/'tests/v08_sha_final.json').write_text(json.dumps(sha,indent=2,ensure_ascii=False)+'\n')
print('PASS: 8 appended scripts, 2 appended menus, 15 new unique Slots')
print('PASS: original numerical IDs, original dialogs and global variables are preserved')
print('PASS: compiled files changed:',', '.join(sorted(changed)))
print('NOTE: this is static/compile verification, not a Windows engine runtime test')
