#!/usr/bin/env python3
from pathlib import Path
import ast, re, sys, hashlib
root=Path(__file__).resolve().parents[1]
base=root/'baseline/v08'; current=root/'build';data=root/'game-data'; local=root/'localization'

assert len(list(data.glob('*.txt')))==32, 'Incomplete 32-file Module System output'
assert all((base/'compiled'/x.name).is_file() for x in data.glob('*.txt'))

for idfile in ('ID_scripts.py','ID_menus.py','ID_troops.py','ID_party_templates.py'):
    original=[x for x in (base/idfile).read_text('utf-8').splitlines() if x.strip()]
    now=[x for x in (current/idfile).read_text('utf-8').splitlines() if x.strip()]
    assert now[:len(original)]==original, f'Old ID order changed: {idfile}'
assert (base/'compiled/variables.txt').read_bytes()==(data/'variables.txt').read_bytes(), 'global variables changed'
# Dialogues may change only where intended (logic edits); text stays as compiled before.
ALLOWED_DIALOG_CHANGES={'dlga_village_elder_donate:village_elder_pretalk',  # v1.0: donation stays in village purse
    'dlga_merchant_demand_toll:merchant_demand_toll_2', 'dlga_merchant_demand_toll:merchant_demand_toll_2.1',
    'dlga_merchant_demand_toll_accept:close_window'}  # v1.0: tolls come out of the caravan's cash box
_old=(base/'compiled/conversation.txt').read_text('utf-8').split('\n')
_new=(data/'conversation.txt').read_text('utf-8').split('\n')
assert len(_old)==len(_new), 'dialogue count changed'
_changed={n.split(' ',1)[0] for o,n in zip(_old,_new) if o!=n}
assert _changed<=ALLOWED_DIALOG_CHANGES, ('unexpected dialogue changes', _changed-ALLOWED_DIALOG_CHANGES)
assert (base/'compiled/troops.txt').read_bytes()==(data/'troops.txt').read_bytes(), 'legacy troop data changed'
assert (base/'compiled/party_templates.txt').read_bytes()==(data/'party_templates.txt').read_bytes()

# Quick-string *indices* must remain compatible; display payload repairs are allowed.
def quick(path):
    x=path.read_text('utf-8').splitlines()
    count=int(x[0].strip());items=[row.split(' ',1) for row in x[1:] if row]
    assert len(items)==count,(path,len(items),count)
    return items
qold=quick(base/'compiled/quick_strings.txt');qnew=quick(data/'quick_strings.txt')
assert [x[0] for x in qnew[:len(qold)]]==[x[0] for x in qold], 'Quick-string IDs reordered'
assert len(qnew)>len(qold)
for x in qnew:
    assert 'æš' not in x[1] and 'æœ' not in x[1], ('Mojibake payload',x)
assert len([x for x in qnew if x[0].startswith('qstr_æ')])==3

# All game text translated in a localized layer; do not replace native troops.
needed={'game_menus.csv','troops.csv','party_templates.csv','quick_strings.csv','game_strings.csv','dialogs.csv'}
for lang in ('cns','cn_s'):
    folder=local/lang
    assert {f.name for f in folder.glob('*.csv')}==needed
    for file in folder.glob('*.csv'):
        b=file.read_bytes();assert b.startswith(b'\xef\xbb\xbf')
        seen=set()
        lines=b.decode('utf-8-sig').splitlines()
        assert lines and lines[0]=='',(file,'first line must be empty: the engine skips it')
        for line in lines[1:]:
            assert line.count('|')==1,(file,line)
            key,val=line.split('|',1)
            assert key not in seen,(file,key)
            assert val,(file,key)
            seen.add(key)
            # Official Chinese style: every non-ASCII char followed by a space
            # (troop names keep the player's own trailing ideographic space).
            for i,ch in enumerate(val):
                if ord(ch)>127 and ch!='\u3000':
                    assert i+1<len(val) and val[i+1] in ' \u3000',(file,key,val)
menu=(local/'cns/game_menus.csv').read_text('utf-8-sig')
for key in ('mno_af09_village_echo','menu_af09_echo','mno_af09_take_aid_watchmen','mno_af09_leave_deserter_guard'):
    assert key+'|' in menu,key
assert (current/'module_scripts.py').read_text('utf-8').startswith('# -*- coding: utf-8 -*-')
assert not (base/'compiled/scripts.txt').read_bytes()==(data/'scripts.txt').read_bytes()
assert not (base/'compiled/menus.txt').read_bytes()==(data/'menus.txt').read_bytes()

# Confirm all special memory effects include corresponding once-only claim markers.
scripts=(current/'module_scripts.py').read_text('utf8')
for required in ('slot_af09_refugee_thanked','slot_af09_deserter_thanked','slot_af09_aid_thanked',
                 '"af09_check_echo"','"af09_take_echo"','script_af01_change_unrest',
                 'slot_af09_aid_count','slot_af09_refugee_homecoming'):
    assert required in scripts
print('VERIFY_V09_OK')
print('Original scripts preserved:',len([x for x in (base/'ID_scripts.py').read_text('utf8').splitlines() if x.strip()]))
print('New scripts:',len([x for x in (current/'ID_scripts.py').read_text('utf8').splitlines() if x.strip()])-len([x for x in (base/'ID_scripts.py').read_text('utf8').splitlines() if x.strip()]))
print('New menus:',len([x for x in (current/'ID_menus.py').read_text('utf8').splitlines() if x.strip()])-len([x for x in (base/'ID_menus.py').read_text('utf8').splitlines() if x.strip()]))
print('Translation entries:',{p.name:len(p.read_text('utf-8-sig').splitlines()) for p in (local/'cns').glob('*.csv')})
print('Changed data:',[f.name for f in sorted(data.glob('*.txt')) if f.read_bytes()!=(base/'compiled'/f.name).read_bytes()])
