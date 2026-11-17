#!/usr/bin/env python3
"""离线推演：一座城镇＋周边村子的钱，按天算 52 周，表里只列前 13 周。

玩家 2026-11-17 指出：现实玩几个小时游戏里才过几个月，所以平衡要看头一到三个月（4～13 周），不看一年。

只是估算，用来比较「改之前」和「改之后」的走向，不代替实机。公式取自源码：
- 城镇每周进账：(有效繁荣×15＋700)×1.5（module_simple_triggers.py 每周金库结算；超出 100 的繁荣只算一半）
- 驻军工资：开局约 378 人、每周 2450；新招的兵每人每周 4.36（docs/调查_驻军工资.md）
- 每天招兵：金库÷2 > 450 时花 450 招约 9.45 人，招到 378 人为止（同上，估算）
- 农民货款：一趟 = 村子产量×价格÷10，代码里没有固定值，这里用 PAY_PER_TRIP（估算，可改）
- 农民一周约 1.75 趟（每天 60% 出发、来回约 3～4 天，估算）
- 村长投资：旧＝钱袋超过「留存」的部分，每天最多换 1 点繁荣（200 第纳尔／点）；新（繁荣即家底）＝每周把钱袋 500 以上部分的四分之一投进去，城镇金库超过 5000 的部分每周投十分之一（500 一点），借给村子的钱每周 1% 利息，付不出先急卖繁荣（160 一点）
- 村民采买（新）：每趟花（钱袋−1000）÷10，最多 1000，进杂货商；城镇记账每周减半，每 100 繁荣加成 +1，最多 +25
- 商人补钱：周转金不足时，由城里人的购买力（繁荣×15＋500 的份额；新：×45＋1500）补（推演过再从金库补 1/8：卖货量几乎不变，金库被掏空，已放弃）
- 繁荣：每周向理想值走 1 点；有经营加成又低于理想值再 +1（新：各 2 点，2026-11-17 玩家定加快一倍）
- 驻军花销（新）：金库实际发出的饷的三分之一进杂货商；城镇记账每周减半，每 100 繁荣加成 +1，最多 +15
- 商队（新）：每成交一次记 +10、每周减半，加成 = 记数÷2，最多 +25（原：14 天内有成交就 +25）
- 王室税（新）：金库加上本周进账、扣掉本周驻军饷后还剩 2000 以上，才收本周进账的 CROWN%；金库超过 10000 的部分再收 CROWN%（富城多交、穷城少交）
用法：python tools/sim_town_economy.py [货款每趟] [村长留存] [每周商队支数] [王室税%]
"""
import sys

WEEKS = 52
PAY_PER_TRIP = int(sys.argv[1]) if len(sys.argv) > 1 else 300
TRIPS_PER_WEEK = 1.75
RESERVE = int(sys.argv[2]) if len(sys.argv) > 2 else 2000  # 村长留存（新）
CARAVANS = float(sys.argv[3]) if len(sys.argv) > 3 else 2  # 每周来成交的商队支数（估算）
CROWN = int(sys.argv[4]) if len(sys.argv) > 4 else 10  # 王室税：本周进账的百分之几交给国王（新）
N_VILLAGES = 3


def eff(p):
    return p if p <= 100 else 100 + (p - 100) // 2


def run(new, raid_week=None, player_sells=0, lend=0):
    loan_income = [0]
    town_p, treasury = 80, 3000
    garrison, wage = 378.0, 2450.0
    floats = [6000, 3750, 3750, 2400] if new else [2000, 1250, 1250, 800]
    shares = [40, 20, 20, 20]
    mgold = list(floats)
    reserve = RESERVE if new else 1000
    vil = [{'p': 40, 'purse': 1500, 'looted': -1, 'loan': 0} for _ in range(N_VILLAGES)]
    for v in vil:
        if lend:
            v['purse'] += lend
            v['loan'] = lend
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
            # 村长投资（旧：每天，留存以上每 200 一点、每天最多 1 点）
            if not new:
                for v in vil:
                    if v['looted'] < 0 and v['purse'] - reserve >= 200 and v['p'] < 260:
                        v['purse'] -= 200
                        v['p'] += 1
            # 驻军每天招兵
            if treasury // 2 > 450 and garrison < 378:
                treasury -= 450
                garrison += 9.45
                wage += 9.45 * 4.36
        # 新（繁荣即家底）：村长每周把钱袋 500 以上部分的四分之一投进去（200 一点）；
        # 城镇金库超过 5000 的部分每周拿十分之一投进去（500 一点）；借给村子的钱每周 1% 利息
        if new:
            for v in vil:
                if v['looted'] < 0:
                    pts = min(max(v['purse'] - 500, 0) // 4 // 200, 260 - v['p'])
                    if pts > 0:
                        v['purse'] -= pts * 200
                        v['p'] += pts
                if v.get('loan', 0) > 0:
                    i = max(v['loan'] // 100, 1)
                    pay = min(i, v['purse'] * 3 // 4)
                    v['purse'] -= pay
                    short = i - pay
                    if short > 0 and v['p'] > 10:  # 急卖：160 一点，最多 2 点
                        pts = min((short + 159) // 160, 2, v['p'] - 10)
                        v['p'] -= pts
                        raised = pts * 160
                        v['purse'] += max(raised - short, 0)
                        short = max(short - raised, 0)
                    v['loan'] += short
                    loan_income[0] += i - short
            pts = min(max(treasury - 5000, 0) // 10 // 500, 260 - town_p)
            if pts > 0:
                treasury -= pts * 500
                town_p += pts
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
        income = (eff(town_p) * 15 + 700) * 3 // 2
        treasury += income
        crown_paid = 0
        if new:
            # 看家底收：发完本周的饷还剩 2000 以上才收进账的 CROWN%；金库超过 10000 的部分再收 CROWN%
            crown_paid = (income * CROWN // 100) if treasury - int(wage) >= 2000 else 0
            crown_paid += max(treasury - 10000, 0) * CROWN // 100
            crown_paid = min(crown_paid, max(treasury, 0))
            treasury -= crown_paid
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
        step = 2 if new else 1  # 2026-11-17：每周靠拢 1 → 2 点，有经营加成再 +2（原 +1），不冲过理想值
        if town_p < ideal:
            town_p = min(ideal, town_p + (2 * step if bonus > 0 else step))
        elif town_p > ideal:
            town_p = max(ideal, town_p - step)
        for v in vil:
            if v['p'] > 70:
                v['p'] -= 1  # 村子原版理想值约 40，加经营加成约 70 封顶（估算）
        spend_slot //= 2
        garrison_slot //= 2
        caravan_slot //= 2
        rows.append(dict(week=week + 1, town_p=town_p, treasury=treasury, crown=crown_paid, garrison=int(garrison),
                         goods_merchant=mgold[0], sold=sold, villager_spend=weekly_villager_spend,
                         payments=weekly_payments, vil_p=sum(v['p'] for v in vil) // N_VILLAGES,
                         vil_purse=sum(v['purse'] for v in vil) // N_VILLAGES))
    return rows


def table(title, rows, weeks=(1, 2, 3, 4, 5, 6, 8, 10, 13)):
    out = [f'### {title}', '',
           '| 周 | 城镇繁荣 | 金库 | 本周王室税 | 驻军 | 杂货商现钱 | 玩家卖出 | 本周村民采买 | 本周货款 | 村子平均繁荣 | 村长平均钱袋 |',
           '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        if r['week'] in weeks:
            out.append('| {week} | {town_p} | {treasury} | {crown} | {garrison} | {goods_merchant} | {sold} | {villager_spend} | {payments} | {vil_p} | {vil_purse} |'.format(**r))
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    print(f'# 推演：城镇三根柱子＋王室税（一趟货款 {PAY_PER_TRIP}、村长留存 {RESERVE}、每周商队 {CARAVANS} 支、王室税 {CROWN}%，前三项为估算）\n')
    print(table('A. 改之前，和平', run(False)))
    print(table('B. 改之后，和平', run(True)))
    print(table('C. 改之后，第 5 周两个村被劫', run(True, raid_week=4)))
    print(table('D. 改之前，玩家每周卖 3000 的货', run(False, player_sells=3000)))
    print(table('E. 改之后，玩家每周卖 3000 的货', run(True, player_sells=3000)))
    r = run(True, lend=3000)
    print(table('F. 改之后，第 1 周你借给三个村各 3000', r))
