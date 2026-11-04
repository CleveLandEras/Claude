import pandas as pd
p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
df = pd.read_csv(p, encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(df)
print('N', N)
amt = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
bet = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
t = pd.to_datetime(df['最後登入時間'], errors='coerce')
gap = (pd.Timestamp('2026-09-17') - t.dt.normalize()).dt.days
card = df['卡别'].apply(lambda c: '普卡' if c == 1 else ('银卡' if c == 2 else '金卡以上'))
ident = df['身份'].map({'持續': '持续', 'VIP': '持续', '黑名單': '持续', '回流': '回流', '新增': '新增'})
new = ident == '新增'
back = ident == '回流'
potpay = (amt == 0) & (bet > 10000)
churn_proxy = (card != '普卡') & (gap > 7)  # 银卡、金卡以上 且 >7 天未登录（仅代理）
print('ident x card')
print(pd.crosstab(ident, card, margins=True))
print('potpay', potpay.sum())
print('potpay by ident', potpay.groupby(ident).sum().to_dict())
print('potpay by card', potpay.groupby(card).sum().to_dict())
print('churn_proxy', churn_proxy.sum(), 'by ident', churn_proxy.groupby(ident).sum().to_dict())
k = new.astype(int) + back.astype(int) + potpay.astype(int) + churn_proxy.astype(int)
print('audience count dist', k.value_counts().sort_index().to_dict())
print('back & potpay', (back & potpay).sum(), 'new & potpay', (new & potpay).sum())
print('back & churn', (back & churn_proxy).sum())
# 回流 by card and paying
print('back paying by card', df[back].assign(pay=amt[back] > 0).groupby(card[back])['pay'].agg(['size', 'sum']).to_dict())
