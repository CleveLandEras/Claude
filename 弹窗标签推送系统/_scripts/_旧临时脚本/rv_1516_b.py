# 审查者只读复算二：A46 "持續老账号 7,764"、回流最小注册天数、全体有储值者集中度基准
import pandas as pd
B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
df = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
c = list(df.columns)
idn = c[-1]; pay = c[6]; bet = c[7]; card = c[4]
df = df[~df[idn].isin(['機器人', '測試帳號'])].copy()
ref = pd.Timestamp('2026-09-16')
df['age'] = (ref - pd.to_datetime(df[c[1]], errors='coerce').dt.normalize()).dt.days
df['dsl'] = (ref - pd.to_datetime(df[c[3]], errors='coerce').dt.normalize()).dt.days
print(df[idn].value_counts().to_dict())
pp = df[(df[pay] <= 0) & (df[bet] > 10000)]
for nm, m in [('持續在场>=365', (pp[idn] == '持續') & (pp['dsl'] <= 7) & (pp['age'] >= 365)),
              ('持續在场>=300', (pp[idn] == '持續') & (pp['dsl'] <= 7) & (pp['age'] >= 300)),
              ('持續在场>=365 含全体在场', (pp['dsl'] <= 7) & (pp['age'] >= 365)),
              ('持續在场 age>365', (pp[idn] == '持續') & (pp['dsl'] <= 7) & (pp['age'] > 365)),
              ('持續 全部>=365', (pp[idn] == '持續') & (pp['age'] >= 365)),
              ('任意身份在场 age>=365 不限PP 持續 未储值', 0)]:
    print(nm, int(m.sum()) if not isinstance(m, int) else m)
w = df[(df[pay] <= 0) & (df['dsl'] <= 7) & (df['age'] >= 365) & (df[idn] == '持續')]
print('持續 未储值 在场 >=365 (不限押注)', len(w), '其中押注>10000', (w[bet] > 10000).sum())
back = df[df[idn] == '回流']; print('回流 age min', back['age'].min(), '<30', (back['age'] < 30).sum())
s = df[df[pay] > 0][pay].sort_values(ascending=False); n = len(s)
print('全体有储值者 top10% 占比', s.head(int(round(n * .1))).sum() / s.sum())
g = df[(df[pay] > 0) & (df[card] >= 3)]; print('全体金卡以上有储值', len(g), g[pay].sum() / s.sum())
print('全体金卡以上人数占活跃', (df[card] >= 3).sum() / len(df))
