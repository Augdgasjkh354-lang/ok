#!/usr/bin/env python3
"""Simplified deterministic 120-day pressure model of cap/probability choices.
Not the game's AI or economic engine: checks parameters and population caps only.
"""
import random
R=random.Random(7007)
CAPS={'refugees':10,'deserters':7,'convoys':8}
CHANCE={'refugees':16,'deserters':10,'convoys':18}
LIFE={'refugees':20,'deserters':16,'convoys':16}
pools={kind:[] for kind in CAPS}
peak={kind:0 for kind in CAPS}
created={kind:0 for kind in CAPS}
for day in range(120):
 for kind in CAPS:
  pools[kind][:]=[born for born in pools[kind] if day-born<LIFE[kind]]
 # The 18 candidate villages model a sustained, severe border-war case.
 for village in range(18):
  for kind in ('refugees','deserters'):
   if len(pools[kind]) < CAPS[kind] and R.randrange(100) < CHANCE[kind]:
    pools[kind].append(day); created[kind]+=1
 # Six kingdoms: a conservative upper-bound stress test (ignores one-per-faction requirement).
 for kingdom in range(6):
  if len(pools['convoys'])<CAPS['convoys'] and R.randrange(100)<CHANCE['convoys']:
   pools['convoys'].append(day);created['convoys']+=1
 for kind in CAPS:
  peak[kind]=max(peak[kind],len(pools[kind]));assert peak[kind]<=CAPS[kind]
print('PASS: 120-day synthetic high-war spawn pressure bounded by existing active-party caps')
for kind in CAPS:
 print(f'  {kind}: peak={peak[kind]} cap={CAPS[kind]} synthetic_created={created[kind]}')
print('NOTE: not a substitute for actual in-game AI and save-load tests')
