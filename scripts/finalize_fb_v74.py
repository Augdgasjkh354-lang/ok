#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent.parent
subprocess.run([sys.executable,str(root/'scripts/finalize_fb_v73.py')],cwd=root,check=True)
translations={"For {reg57} denars, will you join {s54}'s private compact?": '我出{reg57}第纳尔，你愿意转投{s54}的秘密派系吗？', 'Our agreement is sealed. I have joined the other compact, and I shall owe you one future vote.': '交易成立。我已经加入新的派系，下一次封地投票还欠你一票。', 'I refuse your offer. Such whispers are dangerous at court.': '我拒绝。这种风声在宫廷里会害死人。', 'Have you heard any credible whispers of secret dealings?': '最近有什么可信的秘密交易传闻吗？', 'There are whispers about {s63}. I can offer a lead of strength {reg58}; you may bring it before our king.': '有人在议论{s63}。我掌握一条可信度为{reg58}的线索，你可以向国王报告。', 'No reliable story has reached me recently. The court is silent for now.': '近来没有新的可靠传闻，宫廷暂时风平浪静。', 'My liege, I bring you evidence of secret deals among the nobles.': '陛下，我掌握了贵族秘密交易的证据。', 'You have served the crown. I will investigate {s65}; you have earned my gratitude.': '你为王室立了功。我会调查{s65}，并记住你的忠诚。', 'I cannot proceed with this claim without fresher testimony.': '没有更新的证词，我无法继续调查此事。'}
p=root/'game-data/conversation.txt'
data=p.read_bytes()
for english,chinese in translations.items():
 src=english.replace(' ','_').encode('utf-8')
 num=data.count(src)
 if num != 1: raise RuntimeError((english,num))
 data=data.replace(src,chinese.encode('utf-8'))
p.write_bytes(data)
# Game log text encoded as a script constant, localized without changing opcode count.
p=root/'game-data/strings.txt'
data=p.read_bytes()
src=b'Royal_scrutiny:_{s60}_has_been_implicated_in_covert_court_deals.'
if data.count(src)!=1: raise RuntimeError('Missing court scrutiny script message')
data=data.replace(src,'王室密探发现{s60}卷入了秘密交易。'.encode('utf-8'))
p.write_bytes(data)
print('Localized v7.4 court interactions and notices.')
