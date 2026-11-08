#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys
base=Path(__file__).resolve().parent.parent
v6=base/'baseline/v6'
c=base/'build/compiled'
out=base/'game-data'
subprocess.run([sys.executable,str(base/'scripts/finalize_fb_v71.py'),str(v6),str(c),str(out)],check=True)
strings={
 "Which_fief_do_you_covet,_and_who_has_your_alliance's_support?":"你觊觎哪块封地？你的盟友又支持谁？",
 "I_do_not_discuss_my_claims_or_court_intrigues_with_outsiders.":"我不会向外人透露我的封地野心和宫廷谋划。",
 "I_seek_{s60}._My_ambition_is_{reg61},_and_my_anger_over_past_grants_is_{reg62}._For_the_current_award,_my_compact_backs_{s61}.":"我想得到{s60}。我的封地野心为{reg61}，对过往分封的不满为{reg62}。目前的封赏争夺中，我的派系支持{s61}。",
 "I_seek_{s60}._My_ambition_is_{reg61},_and_my_anger_over_past_grants_is_{reg62}._No_compact_candidate_is_declared_right_now.":"我想得到{s60}。我的封地野心为{reg61}，对过往分封的不满为{reg62}。目前我们没有共同推举的候选人。",
 "I_have_no_specific_landed_claim_yet._My_ambition_stands_at_{reg61},_and_my_resentment_at_{reg62}.":"我暂时没有锁定具体的封地目标。我的野心为{reg61}，对分封的不满为{reg62}。",
}
p=out/'conversation.txt';data=p.read_bytes()
for en,cn in strings.items():
 needle=en.encode('utf-8');assert data.count(needle)==1,(en,data.count(needle));data=data.replace(needle,cn.encode('utf-8'))
p.write_bytes(data)
print('Restored previous Chinese and localized 5 v7.2 dialogue lines.')
