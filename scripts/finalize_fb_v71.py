#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Postprocess Warband 1.171 Python3 compiler output, preserving v7 Chinese.
Usage: python finalize_fb_v71.py PATH_TO_V6_COMPILED PATH_TO_V71_COMPILED PATH_TO_V71_FINAL
Requires finalize_fb_v7.py in this script's directory.
"""
from pathlib import Path
import subprocess,sys
v6, compiled, dest=map(lambda s:Path(s).resolve(),sys.argv[1:4])
legacy=Path(__file__).with_name('finalize_fb_v7.py')
subprocess.run([sys.executable,str(legacy),str(v6),str(compiled),str(dest)],check=True)
replacements={
 'conversation.txt':{
 b'Do_you_have_secret_alliances_at_court?': '我听说贵族之间常有秘密盟约。你参与其中吗？',
 b'There_are_many_rumors_at_court._I_have_nothing_to_tell_you_about_any_private_oaths.': '宫廷里流言四起。至于谁与谁私下结盟，我无可奉告。',
 b'I_have_sworn_a_compact_with_{s61}._My_commitment_is_{reg62},_and_my_grievance_over_fiefs_is_{reg63}._Allies_in_danger_can_count_on_me.': '我与{s61}订有盟约。盟约忠诚度为{reg62}，对封地分配的不满为{reg63}。盟友遇险时，我自会伸出援手。',
 b'I_have_no_secret_compact_at_present._The_allegiances_of_the_nobility_change_with_the_winds.': '目前我没有加入任何秘密派系。贵族之间的关系总在变化。',
 },
 'quick_strings.txt':{
 b'Full_start_enabled:_level_62,_attributes_63,_skills_10,_weapon_proficiencies_699.': '满级开局已启用：等级62、属性63、技能10、武器熟练度699。',
 }
}
for file,mapping in replacements.items():
 p=dest/file
 b=p.read_bytes()
 for src,tgt in mapping.items():
  n=b.count(src)
  assert n==1,(file,src,n)
  b=b.replace(src,tgt.encode('utf-8'))
 p.write_bytes(b)
print('Localized 4 new political dialogs and full-start notification.')
