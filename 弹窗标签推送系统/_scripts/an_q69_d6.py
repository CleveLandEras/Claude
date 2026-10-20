"""Q69（只做 D6，D5 按问题 3 答复撤销）：破产位排序链推演各类玩家的人数上下界。只读，不带参数。
复用 an_q54_firstpay.py（A10 首储指纹）的定义；复用 an_q68_fatigue.simulate 不需要（D6 是单次取第一个可买项）。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import runpy
import io
import contextlib
import pandas as pd

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path(_ROOT + '/_scripts/an_q54_firstpay.py')
d, pay, fb, known, FA, FG = g['d'], g['pay'], g['fb'], g['known'], g['FA'], g['FG']

# 买过首储（16,800 点口径）下界：只买首储 + 首储 + 一个已知档位
idx146 = set(fb.index)
for name, (a, gg, n, _) in known.items():
    idx146 |= set(pay[(pay['a0'] == FA + a) & (pay['g0'] == FG + gg)].index)
# 若 50 元 15,000 点也是首储：只买它 + 它 + 一个已知档位（不含它自身那一档）
idx734 = set(idx146) | set(pay[(pay['a0'] == 50) & (pay['g0'] == 15000)].index)
for name, (a, gg, n, _) in known.items():
    if name.startswith('50@300'):
        continue
    idx734 |= set(pay[(pay['a0'] == 50 + a) & (pay['g0'] == 15000 + gg)].index)
print('买过首储下界（16,800 口径）', len(idx146), '；（含 15,000 档）', len(idx734))

d['main'] = ~d['身份'].isin(['VIP', '黑名單'])
d['r07'] = d['days'] <= 7
d['paid'] = d['amt'] > 0


def cnt(mask):
    return int((mask & d['main']).sum()), int((mask & d['main'] & d['r07']).sum()), int(mask.sum())


never = ~d['paid']
b146 = d.index.isin(idx146)
b734 = d.index.isin(idx734)
print('\n列：主数（剔除 VIP、黑名单）｜主数且 0–7 天｜含 VIP、黑名单')
print('从未储值（G1 的下界，首储开放时）', cnt(never))
print('有储值（买过首储者上界 = G2 + G3 上界）', cnt(d['paid']))
print('买过首储下界 146 口径', cnt(pd.Series(b146, index=d.index)))
print('买过首储下界 734 口径', cnt(pd.Series(b734, index=d.index)))
# 有储值但一定没买首储（A19 的 D4a 下界：赠点 < 15,000）——破产时看到的也是首储（首储开放时），归 G1 一侧
nofp = d['paid'] & (d['充值赠点'] < 15000)
print('有储值且赠点 < 15,000（一定没买首储，破产时同 G1）', cnt(nofp))
# 卡别构成（买过首储上界 = 有储值）
m = d['paid'] & d['main']
print('有储值主数卡别', d.loc[m, 'cardg'].value_counts().to_dict())
print('买过首储下界 146 卡别', d.loc[b146 & d['main'], 'cardg'].value_counts().to_dict())
# 收紧后的买过首储上界：有储值 − 一定没买首储（赠点 < 15,000）
ub = d['paid'] & ~nofp
print('买过首储上界（收紧：有储值且赠点 ≥ 15,000）', cnt(ub))
for c in ['普卡', '银卡', '金卡以上']:
    x = ub & (d['cardg'] == c)
    print(f'  {c}', cnt(x), f'储值占主数有储值总额 {d.loc[x & d["main"], "amt"].sum() / d.loc[d["paid"] & d["main"], "amt"].sum() * 100:.2f}%')
