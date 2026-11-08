#!/usr/bin/env python3
"""Ship additive Warband Chinese keys, never overwrite a user's full translation."""
import sys,re,shutil
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'build'))
from module_game_menus import game_menus
from module_troops import troops
from module_party_templates import party_templates

langs=root/'localization'
if langs.exists():shutil.rmtree(langs)
(langs/'cns').mkdir(parents=True)

cjk=re.compile(r'[\u3400-\u9fff]')
# Menu keys are engine-generated; retain IDs exactly. Output only mod-owned keys.
menus={}
for m in game_menus:
    id,flag,body,mesh,ops,opts=m
    if id.startswith(('af','fb')):
        menus['menu_'+id]=body
    for item in opts:
        if item[0].startswith(('af','fb')):
            menus['mno_'+item[0]]=item[2]

quick={}
for line in (root/'game-data/quick_strings.txt').read_text('utf-8').splitlines()[1:]:
    if not line.strip():continue
    parts=line.split(' ',1)
    if len(parts)<2:continue
    id,txt=parts
    if cjk.search(txt):
        quick[id]=txt
# Known legacy mojibake IDs are intentionally excluded from language CSV.
# Their compiled display payload is repaired by build_v09.py without shifting IDs.
quick={k:v for k,v in quick.items() if not k.startswith('qstr_æ')}

# The user's supplied translation style uses spaced Hanzi for troop labels.
# Only newly introduced named gang leaders are shipped; no native troop keys replaced.
trp={}
for t in troops:
    tid=t[0]
    if tid.startswith('af04_'):
        name=t[1]; plural=t[2]
        def spaced_chinese(s):
            return ' '.join(s)+'\u3000' if cjk.search(s) else s
        trp['trp_'+tid]=spaced_chinese(name)
        trp['trp_'+tid+'_pl']=spaced_chinese(plural)

# Party template labels will be shown on map; translate only Ashfall templates.
pt_map={
    'af02_refugees':'流 民', 'af02_deserters':'逃 兵',
    'af03_supply_convoy':'军 粮 运 输 队',
    'af04_blackpine':'黑 松 帮', 'af04_greywolf':'灰 狼 团',
    'af04_saltraven':'盐 鸦 商 路',
}
pts={'pt_'+t[0]:pt_map[t[0]] for t in party_templates if t[0] in pt_map}

def save(name,rows):
    assert len(rows)==len(set(rows))
    for k,v in rows.items():
        assert '\n' not in k and '\n' not in v and '|' not in k and '|' not in v,(k,v)
    text=''.join(f'{k}|{v}\n' for k,v in rows.items())
    (langs/'cns'/name).write_text(text,encoding='utf-8-sig')

save('game_menus.csv',menus)
save('quick_strings.csv',quick)
save('troops.csv',trp)
save('party_templates.csv',pts)
# Some Warband localizations use cn_s for module language data; ship both variants.
shutil.copytree(langs/'cns',langs/'cn_s')
print({x.name:sum(1 for ln in x.read_text('utf-8-sig').splitlines() if '|' in ln) for x in (langs/'cns').glob('*.csv')})
