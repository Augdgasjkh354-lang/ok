#!/usr/bin/env python3
"""离线推演：一座城镇＋周边村子的钱，按天算 52 周。

只是估算，用来比较「改之前」和「改之后」的走向，不代替实机。公式取自源码：
- 城镇每周进账：(有效繁荣×15＋700)×1.5（module_simple_triggers.py 每周金库结算；超出 100 的繁荣只算一半）
- 驻军工资：开局约 378 人、每周 2450；新招的兵每人每周 4.36（docs/调查_驻军工资.md）
- 每天招兵：金库÷2 > 450 时花 450 招约 9.45 人，招到 378 人为止（同上，估算）
- 农民货款：一趟 = 村子产量×价格÷10，代码里没有固定值，这里用 PAY_PER_TRIP（估算，可改）
- 农民一周约 1.75 趟（每天 60% 出发、来回约 3～4 天，估算）
- 村长投资：钱袋超过「留存」的部分，每天最多换 1 点繁荣（200 第纳尔／点）
- 村民采买（新）：每趟花（钱袋−1000）÷10，最多 1000，进杂货商；城镇记账每周减半，每 100 繁荣加成 +1，最多 +25
- 商人补钱：周转金不足时，由城里人的购买力（繁荣×15＋500 的份额；新：×45＋1500）补（推演过再从金库补 1/8：卖货量几乎不变，金库被掏空，已放弃）
- 繁荣：每周向理想值走 1 点；有经营加成又低于理想值再 +1
- 驻军花销（新）：金库实际发出的饷的三分之一进杂货商；城镇记账每周减半，每 100 繁荣加成 +1，最多 +15
- 商队（新）：每成交一次记 +10、每周减半，加成 = 记数÷2，最多 +25（原：14 天内有成交就 +25）
用法：python tools/sim_town_economy.py [货款每趟] [村长留存] [每周商队支数]
"""
import sys

WEEKS = 52
PAY_PER_TRIP = int(sys.argv[1]) if len(sys.argv) > 1 else 300
TRIPS_PER_WEEK = 1.75
RESERVE = int(sys.argv[2]) if len(sys.argv) > 2 else 3000  # 村长留存（新）
CARAVANS = float(sys.argv[3]) if len(sys.argv) > 3 else 2  # 每周来成交的商队支数（估算）
N_VILLAGES = 3


def eff(p):
    return p if p <= 100 else 100 + (p - 100) // 2


def run(new, raid_week=None, player_sells=0):
    town_p, treasury = 80, 3000
    garrison, wage = 378.0, 2450.0
    floats = [6000, 3750, 3750, 2400] if new else [2000, 1250, 1250, 800]
    shares = [40, 20, 20, 20]
    mgold = list(floats)
    reserve = RESERVE if new else 1000
    vil = [{'p': 40, 'purse': 1500, 'looted': -1} for _ in range(N_VILLAGES)]
    spend_slot = 0
    garrison_slot = 0
    caravan_slot = 0
    native_ideal, caravan_bonus = 55, 25
    rows = []
    trip_acc = [0.0] * N_VILLAGES
    for week in range(WEEKS):
        weekly_villager_spend = 0
        weekly_payments = 0
        for day in range(7):
            # 农民进城
            for i, v in enumerate(vil):
                if v['looted'] >= 0:
                    continue
                trip_acc[i] += TRIPS_PER_WEEK / 7
                while trip_acc[i] >= 1:
                    trip_acc[i] -= 1
                    pay = min(PAY_PER_TRIP, treasury * 3 // 4)
                    treasury -= pay
                    v['purse'] += pay
                    weekly_payments += pay
                    if new:
                        s = min(max(v['purse'] - 1000, 0) // 10, 1000)
                        v['purse'] -= s
                        mgold[0] += s
                        spend_slot += s
                        weekly_villager_spend += s
            # 村长投资
            for v in vil:
                if v['looted'] < 0 and v['purse'] - reserve >= 200 and v['p'] < 260:
                    v['purse'] -= 200
                    v['p'] += 1
            # 驻军每天招兵
            if treasury // 2 > 450 and garrison < 378:
                treasury -= 450
                garrison += 9.45
                wage += 9.45 * 4.36
        # 劫村
        if raid_week is not None and week == raid_week:
            for v in vil[:2]:
                v['purse'] -= min(400, v['purse'])
                v['p'] = max(0, v['p'] - 20)
                v['looted'] = 2  # 两周不派农民
        for v in vil:
            if v['looted'] >= 0:
                v['looted'] -= 1
        # 每周：进账、工资
        treasury += (eff(town_p) * 15 + 700) * 3 // 2
        if new:
            paid = min(int(wage), max(treasury, 0))
            mgold[0] += paid // 3
            garrison_slot += paid // 3
            caravan_slot += int(10 * CARAVANS)
        treasury -= int(wage)
        if treasury < 0:
            # 金库不够：城主补或开小差，这里简化为兵走掉一些
            short = -treasury
            treasury = 0
            lost = short / max(wage / garrison, 1)
            garrison = max(garrison - lost, 0)
            wage = max(wage - short, 0)
        # 玩家卖货给杂货商
        sold = min(player_sells, mgold[0])
        mgold[0] -= sold
        # 商人补钱 / 交回
        merchant_from_power = merchant_from_treasury = 0
        for k in range(4):
            if mgold[k] < floats[k]:
                short = floats[k] - mgold[k]
                power = ((eff(town_p) * 45 + 1500) if new else (eff(town_p) * 15 + 500)) * shares[k] // 100
                give = min(short, power)
                merchant_from_power += give
                short -= give
                mgold[k] += give
            elif mgold[k] > floats[k]:
                treasury += mgold[k] - floats[k]
                mgold[k] = floats[k]
        # 繁荣
        if new:
            bonus = min(caravan_slot // 2, 25) + min(spend_slot // 100, 25) + min(garrison_slot // 100, 15)
        else:
            bonus = caravan_bonus
        ideal = native_ideal + bonus
        if town_p < ideal:
            town_p += 2 if bonus > 0 else 1
        elif town_p > ideal:
            town_p -= 1
        for v in vil:
            if v['p'] > 70:
                v['p'] -= 1  # 村子原版理想值约 40，加经营加成约 70 封顶（估算）
        spend_slot //= 2
        garrison_slot //= 2
        caravan_slot //= 2
        rows.append(dict(week=week + 1, town_p=town_p, treasury=treasury, garrison=int(garrison),
                         goods_merchant=mgold[0], sold=sold, villager_spend=weekly_villager_spend,
                         payments=weekly_payments, vil_p=sum(v['p'] for v in vil) // N_VILLAGES,
                         vil_purse=sum(v['purse'] for v in vil) // N_VILLAGES))
    return rows


def table(title, rows, weeks=(1, 4, 8, 13, 20, 21, 22, 24, 26, 39, 52)):
    out = [f'### {title}', '',
           '| 周 | 城镇繁荣 | 金库 | 驻军 | 杂货商现钱 | 玩家卖出 | 本周村民采买 | 本周货款 | 村子平均繁荣 | 村长平均钱袋 |',
           '|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        if r['week'] in weeks:
            out.append('| {week} | {town_p} | {treasury} | {garrison} | {goods_merchant} | {sold} | {villager_spend} | {payments} | {vil_p} | {vil_purse} |'.format(**r))
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    print(f'# 推演：城镇三根柱子（一趟货款 {PAY_PER_TRIP}、村长留存 {RESERVE}、每周商队 {CARAVANS} 支，均为估算）\n')
    print(table('A. 改之前，和平', run(False)))
    print(table('B. 改之后，和平', run(True)))
    print(table('C. 改之后，第 21 周两个村被劫', run(True, raid_week=20)))
    print(table('D. 改之前，玩家每周卖 3000 的货', run(False, player_sells=3000)))
    print(table('E. 改之后，玩家每周卖 3000 的货', run(True, player_sells=3000)))
