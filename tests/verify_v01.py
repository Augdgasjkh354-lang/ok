#!/usr/bin/env python3
"""Source/compiled ID and deterministic compatibility audit (not a Warband client test)."""
from pathlib import Path
import ast
import hashlib
import re

root=Path(__file__).resolve().parent.parent
old=root/'baseline/v75/source'
assert old.is_dir(), 'Missing bundled v7.5 source snapshots.'
compiled=root/'game-data'
base=root/'baseline/v75/compiled'

def must(b,msg):
    if not b: raise AssertionError(msg)

def read(p):return p.read_text(encoding='utf-8')

def assignment_items(path, var):
    tree=ast.parse(read(path))
    for stmt in tree.body:
        if isinstance(stmt,ast.Assign) and any(isinstance(t,ast.Name) and t.id==var for t in stmt.targets):
            return stmt.value.elts
    raise AssertionError('missing '+var)

def labeled_blocks(path,var):
    items=assignment_items(path,var)
    return {e.elts[0].value:e for e in items}

for p in root.glob('build/module_*.py'):
    # Most are vanilla and unchanged. Validate every edited file at minimum.
    if p.stem in {'module_constants','module_scripts','module_game_menus','module_simple_triggers'}:
        ast.parse(read(p))

# No changes to any historical script except the two explicitly instrumented.
old_scripts=labeled_blocks(old/'module_scripts.py','scripts')
new_scripts=labeled_blocks(root/'build/module_scripts.py','scripts')
allowed={'village_set_state','update_volunteer_troops_in_village'}
for name,oldnode in old_scripts.items():
    must(name in new_scripts,'Old script deleted: '+name)
    if name not in allowed:
        must(ast.dump(oldnode)==ast.dump(new_scripts[name]),'Old script unexpectedly modified: '+name)
newscriptnames=set(new_scripts)-set(old_scripts)
expected_new={
    'af01_ensure_village','af01_change_unrest','af01_record_event',
    'af01_on_raid_started','af01_on_looted','af01_settle_aid','af01_daily_update',
    'af01_check_aid','af01_begin_aid','af01_prepare_aid_error',
    'af01_prepare_status','af01_find_nearest_village',
}
must(newscriptnames==expected_new,'New scripts set mismatch: '+str(newscriptnames^expected_new))

old_menus=labeled_blocks(old/'module_game_menus.py','game_menus')
new_menus=labeled_blocks(root/'build/module_game_menus.py','game_menus')
for name,oldnode in old_menus.items():
    must(name in new_menus,'Old menu deleted: '+name)
    if name not in {'village','camp_cheat'}:
        must(ast.dump(oldnode)==ast.dump(new_menus[name]),'Old menu modified: '+name)
must(set(new_menus)-set(old_menus)=={'af01_village_status','af01_debug'},'New menu IDs mismatch')

simple_old=assignment_items(old/'module_simple_triggers.py','simple_triggers')
simple_new=assignment_items(root/'build/module_simple_triggers.py','simple_triggers')
must(len(simple_new)==len(simple_old)+1,'Daily trigger not appended')
for index,item in enumerate(simple_old):
    must(ast.dump(item)==ast.dump(simple_new[index]),'Existing simple trigger reordered')

for name in ('ID_scripts.py','ID_menus.py'):
    oldlines=[s for s in read(root/'baseline/v75'/name).splitlines() if s.strip()]
    newlines=[s for s in read(root/'build'/name).splitlines() if s.strip()]
    must(newlines[:len(oldlines)]==oldlines,'Old IDs moved: '+name)

oldvars=read(base/'variables.txt').splitlines()
newvars=read(compiled/'variables.txt').splitlines()
must(newvars[:len(oldvars)]==oldvars,'Existing global vars renumbered')
must(newvars[len(oldvars):]==['g_af01_debug_village'],'Unexpected global additions')

# The initial v7.5 quick-string IDs must remain stable; additions go at end.
oldqs=read(base/'quick_strings.txt').splitlines()
newqs=read(compiled/'quick_strings.txt').splitlines()
must(newqs[2:2+len(oldqs)-2]==oldqs[2:],'Existing quick strings shifted')

oldfiles={p.name for p in base.glob('*.txt')}
newfiles={p.name for p in compiled.glob('*.txt')}
must(newfiles==oldfiles,'Missing or additional compiled text files')
changed={name for name in oldfiles if hashlib.sha256((base/name).read_bytes()).digest()!=hashlib.sha256((compiled/name).read_bytes()).digest()}
expected_changed={'variables.txt','variable_uses.txt','scripts.txt','menus.txt','simple_triggers.txt','quick_strings.txt'}
must(changed==expected_changed,'Unexpected generated data changes: '+str(changed^expected_changed))

# Confirm no unintentional new popularity/loyalty stat and no slot collisions.
constants=read(root/'build/module_constants.py')
old_constants=read(old/'module_constants.py')
must('slot_af01_popular_support' not in constants,'A separate popular support stat was reintroduced')
for value in range(650,661):
    must(not re.search(r'^slot_\w+\s*=\s*'+str(value)+r'\b',old_constants,re.M),'Existing slot conflict at '+str(value))
    must(len(re.findall(r'^slot_af01_\w+\s*=\s*'+str(value)+r'\b',constants,re.M))==1,'Missing unique new slot '+str(value))

menus=read(compiled/'menus.txt')
qs=read(compiled/'quick_strings.txt')
scripts=read(compiled/'scripts.txt')
for text in ('menu_af01_village_status','menu_af01_debug','查看地方战乱与援助','运送赈灾粮'):
    must(text in menus,'Missing menu text '+text)
for text in ('地方援助已完成','第纳尔不足','七天援助冷却','再次援助还需'):
    must(text in qs,'Missing Chinese quick-string '+text)
for token in expected_new:
    must(re.search(r'^'+re.escape(token)+r' -1\s',scripts,re.M), 'Missing compiled script '+token)
must((compiled/'conversation.txt').read_bytes()==(base/'conversation.txt').read_bytes(),'Political dialogues changed')
must((compiled/'strings.txt').read_bytes()==(base/'strings.txt').read_bytes(),'v7.5 strings changed')

# Specific anti-exploit, native relation/prosperity, raid idempotency hooks in source.
script_text=read(root/'build/module_scripts.py')
for token in ('slot_af01_last_tick_token','slot_af01_last_looted_token',
              'slot_af01_pending_action','script_change_player_relation_with_center',
              'script_change_center_prosperity','script_af01_on_looted'):
    must(token in script_text,'Missing anti-exploit or native integration: '+token)

print('PASS: v7.5 script/menu/trigger prefixes; new script/menu IDs; slots;')
print('      1 appended global; quick-string order; 26 untouched data files; Chinese UI;')
print('      court dialogue and strings byte-exact; no independent popular-support stat.')
print('COMPILED DELTA:',', '.join(sorted(changed)))
