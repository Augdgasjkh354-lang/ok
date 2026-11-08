#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reconcile converted compiler output against original v6 UTF-8 text.

Usage: python finalize_fb_v7.py /path/to/fb6-output /path/to/fb7-compiled /path/to/fb7-final
Keeps existing Chinese strings byte-perfect; localizes newly added v7 dialogue.
"""
from pathlib import Path
import sys, shutil

baseline, compiled, dest = map(lambda s: Path(s).resolve(), sys.argv[1:4])
assert baseline.is_dir() and compiled.is_dir()
dest.mkdir(parents=True,exist_ok=True)
for f in compiled.glob('*.txt'):
    shutil.copy2(f, dest/f.name)

# These three existing UTF-8 lines are the only Latin1→UTF-8 mishandlings
# found by the v6 regression comparison of 32 exported data files.
def replace_line_by_key(file, prefix, from_file):
    data=file.read_bytes().splitlines(keepends=True)
    old=from_file.read_bytes().splitlines(keepends=True)
    mine=[i for i,line in enumerate(data) if line.startswith(prefix)]
    them=[line for line in old if line.startswith(prefix)]
    assert len(mine)==1 and len(them)==1, (file.name,prefix)
    data[mine[0]]=them[0]
    file.write_bytes(b''.join(data))

for key in [b'dlga_village_elder_talk:village_elder_donate ',
            b'dlga_village_elder_donate:village_elder_pretalk ']:
    replace_line_by_key(dest/'conversation.txt',key,baseline/'conversation.txt')
replace_line_by_key(dest/'strings.txt',b'str_fb_companions_gathered ',baseline/'strings.txt')

localizations={
  b'What_do_you_remember_of_our_past_dealings?': '你还记得我们过去的恩怨吗？',
  b'You_freed_me_{reg51}_times,_imprisoned_me_{reg52}_times._I_carry_a_grudge_of_{reg54}._Your_deeds_against_my_family_add_another_{reg55}._I_have_not_forgotten.':
     '你放走过我{reg51}次，也囚禁过我{reg52}次。我对你的仇怨有{reg54}之深，家族之恨还有{reg55}。这笔账，我不会忘。',
  b'You_freed_me_{reg51}_times,_imprisoned_me_{reg52}_times._My_debt_of_gratitude_stands_at_{reg53},_and_my_grievance_at_{reg54}._I_remember_your_mercy.':
     '你放走过我{reg51}次、囚禁我{reg52}次。我欠你的恩情是{reg53}，旧怨是{reg54}。你的仁慈，我记得。',
  b"I_remember_{reg51}_acts_of_mercy_and_{reg52}_imprisonments._My_gratitude_is_{reg53},_my_resentment_{reg54},_and_my_family's_grievance_{reg55}.":
     '我记得你放走我{reg51}次，囚禁我{reg52}次。恩情{reg53}，私怨{reg54}，家族之恨{reg55}。',
}
p=dest/'conversation.txt'
data=p.read_bytes()
for english,chinese in localizations.items():
    assert data.count(english)==1,(english,data.count(english))
    data=data.replace(english,chinese.encode('utf-8'))
p.write_bytes(data)

p=dest/'quick_strings.txt'
data=p.read_bytes()
old=b'Rumor:_{s57}_is_hunting_you_over_a_personal_grudge.'
assert data.count(old)==1,data.count(old)
data=data.replace(old,'传闻：{s57}因私怨正在追寻你的行踪。'.encode('utf-8'))
p.write_bytes(data)
print('Restored 3 original Chinese entries; localized 4 new dialogues + 1 rumor message.')
