import sys
sys.path.insert(0, '/Users/decheng.huang/claude/弹窗标签推送系统/_scripts')
from an_a45_members import load
df, m = load()
pay, card, idn = m['pay'], m['card'], m['idn']
N = len(df)
g = df[card] >= 3
print('金卡以上全体', g.sum(), g.sum() / N)
print('金卡以上且有储值', (g & df['has_paid']).sum(), (g & df['has_paid']).sum() / N)
nar = df['is_new'] | df['back_present'] | df['pp_verified']
u = df[~nar & df['present']]
print('窄口径 在场未覆盖', len(u), '其中有储值', u['has_paid'].sum())
pres_off = df[~df['present']]
print('宽未覆盖 离线/在场', (~df['present'] & ~(df['is_new'] | df['is_back'] | df['pp_wide'] | df['churn_ub'])).sum())
