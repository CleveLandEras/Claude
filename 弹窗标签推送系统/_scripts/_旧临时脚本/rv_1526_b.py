import sys
sys.path.insert(0, '/Users/decheng.huang/claude/弹窗标签推送系统/_scripts')
import pandas as pd
from an_a45_members import load
df, m = load()
pay, bet, idn, card, act = m['pay'], m['bet'], m['idn'], m['card'], m['act']
new = df[df['is_new']]
z = new[new[bet] == 0]
print('新增押注0', len(z), '其中赠点=1000', (z[act] == 1000).sum())
print('押注0 的新增 注册天数分布 0/1/2-6/7-29:', (z['age'] == 0).sum(), (z['age'] == 1).sum(), ((z['age'] >= 2) & (z['age'] <= 6)).sum(), ((z['age'] >= 7)).sum())
print('押注0新增 age>=7 且在场', ((z['age'] >= 7) & z['present']).sum())
print('新增 age>=7 总', (new['age'] >= 7).sum(), '其中押注0', ((new['age'] >= 7) & (new[bet] == 0)).sum())
print('新增在场率', new['present'].mean(), '全体', df['present'].mean())
# 同龄对照: 全体 age<=29 就是新增; 对照回到 age 30-59 的非新增在场率
old = df[(df['age'] >= 30) & (df['age'] <= 59)]
print('age30-59 在场率', old['present'].mean(), len(old))
# 新增金卡以上占其储值
nv = new[new[pay] > 0]
print('新增有储值', len(nv), '金卡以上占其储值', nv[nv[card] >= 3][pay].sum() / nv[pay].sum())
bk = df[df['is_back'] & (df[pay] > 0)]
print('回流金卡以上', (bk[card] >= 3).sum(), bk[bk[card] >= 3][pay].sum() / bk[pay].sum())
hv = df[df['has_paid']]
print('全体金卡以上', (hv[card] >= 3).sum(), hv[hv[card] >= 3][pay].sum() / hv[pay].sum())
pp = df[df['pp_wide'] & df['present'] & (df['age'] >= 365) & (df[idn] == '持續')]
print('7181', len(pp))
# 在场 8-14 天 App 分布不需要
# 新增 age 对在场率: age<=7
print('新增 age>=8 在场率', new[new['age'] >= 8]['present'].mean())
