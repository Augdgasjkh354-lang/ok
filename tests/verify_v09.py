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
    'dlga_village_elder_talk:village_elder_donate',  # v1.0 NPC对白 A-14: 捐钱选项只写动作和代价
    'dlga_village_elder_recruit_start:village_elder_talk',  # v1.0 扩展 B1: 村长招兵价按威名档位打折（条件改单价）
    'dlga_village_elder_recruit_start:village_elder_recruit_decision',  # v1.0 扩展 B1: 同上，文本改中文并显示单价
    'dlga_start:village_elder_talk', 'dlga_start:village_elder_talk.1',  # v1.0 NPC对白 B-3: 村长认出劫掠者, 旧问候加互斥条件
    'dlga_start:village_elder_talk.2', 'dlga_start:village_elder_talk.3',
    'dlga_start:lord_meet_neutral',  # v1.0 NPC对白 B-1/B-2/B-6: 领主初见专属招呼, 通用句加互斥条件
    'dlga_start:tavernkeeper_talk',  # v1.0 NPC对白 B-5: 酒馆老板专属招呼, 通用句加互斥条件
    'dlga_lady_marriage_discussion:lady_proposal_refused.1',  # v1.0 NPC对白 B-7: 道德派低荣誉拒绝排除凶名
    'dlga_merchant_demand_toll:merchant_demand_toll_2', 'dlga_merchant_demand_toll:merchant_demand_toll_2.1',
    'dlga_merchant_demand_toll_accept:close_window'}  # v1.0: tolls come out of the caravan's cash box
# v1.0: lords, kings and towns pay the player from their real money (af19_*).
# v1.0 第六批（十）: arena prizes and ladies' quest rewards are paid from
# real money too (town treasury / the lady's guardian).
ALLOWED_DIALOG_CHANGES|={
    'dlga_arena_master_fight_result:arena_master_pre_talk.2',
    'dlga_arena_master_fight_result:arena_master_pre_talk.3',
    'dlga_arena_master_fight_result:arena_master_pre_talk.4',
    'dlga_arena_master_fight_result:arena_master_pre_talk.5',
    'dlga_arena_master_fight_result:arena_master_pre_talk.6',
    'dlga_lady_qst_duel_for_lady_succeeded_2:lady_pretalk',
    'dlga_start:lady_escort_lady_succeeded',
    'dlga_start:lady_generic_mission_succeeded',
    'dlga_start:rescue_prisoner_succeed_1',
    'dlga_capture_enemy_hero_thank:capture_enemy_hero_thank_2',
    'dlga_event_triggered:close_window.1',
    'dlga_lord_buy_prisoner_accept:lord_pretalk',
    'dlga_lord_hunt_down_fugitive_reward_accept:lord_pretalk',
    'dlga_lord_kill_local_merchant_let_go_2:lord_pretalk',
    'dlga_lord_marriage_permission_engagement_date:close_window',
    'dlga_lord_mercenary_service_verify_2:lord_mercenary_service_accept_3',
    'dlga_lord_mission_accepted:close_window',
    'dlga_lord_mission_deal_with_bandits_accepted:close_window',
    'dlga_lord_mission_deliver_message_accepted:close_window',
    'dlga_lord_mission_raise_troops_accepted:close_window',
    'dlga_lord_persuade_lords_to_make_peace_pay:close_window',
    'dlga_lord_return_dower:close_window',
    'dlga_lord_start:close_window.1',
    'dlga_lord_start:lord_deal_with_bandits_completed',
    'dlga_lord_start:lord_deliver_cattle_to_army_thank',
    'dlga_lord_start:lord_follow_spy_completed',
    'dlga_lord_start:lord_follow_spy_half_completed',
    'dlga_lord_start:lord_follow_spy_half_completed.1',
    'dlga_lord_start:lord_generic_mission_completed.2',
    'dlga_lord_start:lord_pretalk',
    'dlga_lord_start:lord_runaway_serf_half_completed',
    'dlga_lord_tell_mission_incriminate_commander_fin:lord_pretalk',
    'dlga_mayor_begin:close_window',
    'dlga_mayor_begin:close_window.1',
    'dlga_mayor_begin:lord_deal_with_night_bandits_completed',
    'dlga_mayor_begin:mayor_friendly_pretalk',
    'dlga_mayor_begin:mayor_friendly_pretalk.1',
    'dlga_mayor_looters_quest_destroyed:mayor_looters_quest_destroyed_2',
    'dlga_mayor_looters_quest_destroyed_2:close_window',
    'dlga_mayor_looters_quest_goods_2:close_window',
    'dlga_mayor_looters_quest_goods_response:mayor_looters_quest_goods_2',
    'dlga_quest_meet_spy_in_enemy_town_completed_2:lord_pretalk',
    'dlga_start:close_window.23',
    'dlga_start:rescue_prisoner_succeed_2',
    'dlga_tavernkeeper_deliver_wine:tavernkeeper_pretalk',
    'dlga_tavernkeeper_deliver_wine_incomplete:tavernkeeper_pretalk',
}
# v1.0 NPC对白 B-0: append-only. Old dialogue IDs must appear in order at the
# head of the new file; new rows may only be appended at the end.
_old=(base/'compiled/conversation.txt').read_text('utf-8').split('\n')
_new=(data/'conversation.txt').read_text('utf-8').split('\n')
if _old and _old[-1]=='': _old=_old[:-1]
if _new and _new[-1]=='': _new=_new[:-1]
assert len(_new)>=len(_old), 'dialogue lines removed'
# v1.0 NPC对白 B-3 修正: 第 0 行是文件头, 第 1 行是对话总数, 都不是对话 ID;
# 追加行使总数 +1, 只比对第 2 行起的 ID。
assert int(_new[1])==len(_new)-2, 'dialogue count mismatch'
assert [n.split(' ',1)[0] for n in _new[2:len(_old)]]==[o.split(' ',1)[0] for o in _old[2:]], 'dialogue order changed'
_changed={n.split(' ',1)[0] for o,n in zip(_old[2:],_new[2:]) if o!=n}
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
