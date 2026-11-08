#!/usr/bin/env python3
"""Restore all historical Chinese dialogue plus v7.3 political dialogue."""
from pathlib import Path
import sys,subprocess
base=Path(__file__).resolve().parent.parent
subprocess.run([sys.executable,str(base/'scripts/finalize_fb_v72.py')],cwd=base,check=True)
translations={'Let us discuss our political interests in private.': '我想和你私下谈谈王国中的政治交易。', 'We can speak away from the court. Your political credit is {reg41}; mine is {reg42}. What is your proposal?': '这里没有旁人。你的政治信用为{reg41}，我的信用为{reg42}。说说你的提议吧。', 'I offer {reg40} denars for your vote in this fief council.': '我愿付出{reg40}第纳尔，换取你在本次封地议事中支持我。', 'Agreed. I will vote for you in this council. I know the price of breaking my word.': '成交。本次封地投票我会支持你。我清楚背信的代价。', 'I will not sell you my vote. Keep your money.': '这张票我不卖。把钱收回去吧。', 'I shall vote for you now; promise me your vote in the next fief council.': '这次我投你一票。你得承诺下次封地议事支持我。', 'I accept. Your vote is cast for me. If you honor it, I will owe you a future vote.': '我接受。你现在已经投票支持我。如果守约，我就欠你下次封地议事的一票。', 'I cannot make that promise at present.': '眼下我无法与你订下这份交易。', 'I withdraw my oath to support you, whatever the consequences.': '我决定撕毁支持你的承诺，后果由我承担。', 'You have dishonored your word. I shall remember this insult.': '你背弃了誓言。这份羞辱我会记在心里。', 'What do we still owe each other?': '我们之间还有哪些尚未兑现的人情债？', 'I owe you one vote in a later fief council. Your credit is {reg46}; I have broken {reg45} promises.': '我还欠你下一次封地议事的一票。你的政治信用为{reg46}；我累计失信{reg45}次。', 'I have promised to vote for you in the current council. Your credit is {reg46}.': '本次封地议事我已承诺支持你。你的政治信用为{reg46}。', 'We have no outstanding promise between us. Your credit is {reg46}; my breaches number {reg45}.': '我们目前没有待兑现的承诺。你的政治信用为{reg46}；我累计失信{reg45}次。', 'Enough of secret politics for now.': '密谈就到这里吧。'}
p=base/'game-data/conversation.txt'
data=p.read_bytes()
for en,cn in translations.items():
 src=en.replace(' ','_').encode('utf-8')
 n=data.count(src)
 if n!=1:raise RuntimeError('Missing or repeated dialogue: '+en+' '+str(n))
 data=data.replace(src,cn.encode('utf-8'))
p.write_bytes(data)
print('Localized',len(translations),'v7.3 private-politics lines.')
