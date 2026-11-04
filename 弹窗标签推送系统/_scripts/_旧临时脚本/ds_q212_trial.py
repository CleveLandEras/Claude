# 试算（设计 Q212 用，只读）：离线分档 × 身份 × 储值 × 平台，确认切分方式可行；不得替执行者下结论
import pandas as pd
B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
b = pd.read_csv(B + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
bad = ['機器人', '測試帳號']
a = a[~a['身份'].isin(bad)].copy()
b = b[~b['身份'].isin(bad)].copy()
print('活跃剔除后', len(a), '名单剔除后', len(b))
ref = pd.Timestamp('2026-09-16')
for d in (a, b):
    d['gap'] = (ref - pd.to_datetime(d['最後登入時間'], errors='coerce').dt.normalize()).dt.days
print('gap缺失', a['gap'].isna().sum(), b['gap'].isna().sum())
print('活跃gap范围', a['gap'].min(), a['gap'].max(), '名单gap范围', b['gap'].min(), b['gap'].max())
only = b[~b['会员编号'].isin(a['会员编号'])].copy()
print('仅名单', len(only), '名单∩活跃', len(b) - len(only))
print('仅名单gap范围', only['gap'].min(), only['gap'].max())
print('登入平台取值(活跃)'); print(a['登入平台'].astype(str).str.lower().value_counts(dropna=False).to_string())
print('登入平台取值(仅名单)'); print(only['登入平台'].astype(str).str.lower().value_counts(dropna=False).to_string())
print('身份(仅名单)'); print(only['身份'].value_counts().to_string())
bins = [-1, 0, 7, 14, 31, 99]
labs = ['0', '1-7', '8-14', '15-31', '32+']
a['tier'] = pd.cut(a['gap'], bins, labels=labs)
print('活跃分档'); print(a['tier'].value_counts().sort_index().to_string())
tot = a['总充值金额'].sum()
print('活跃累计储值总额', tot)
a['sv'] = a['总充值金额'] > 0
only['sv'] = only['总充值金额'] > 0
print('分档 有储值/储值额占比')
print(a.groupby('tier', observed=True).agg(n=('sv', 'size'), sv=('sv', 'sum'), amt=('总充值金额', 'sum')).assign(share=lambda x: x.amt / tot).to_string())
print('仅名单 n/有储值/储值额', len(only), only['sv'].sum(), only['总充值金额'].sum())
print('身份×分档'); print(pd.crosstab(a['身份'], a['tier']).to_string())
print('登录星期(8-14天档)'); print(pd.to_datetime(a.loc[a['tier']=='8-14','最後登入時間']).dt.dayofweek.value_counts().sort_index().to_string())
print('逐日人数(活跃 gap 0-31)'); print(a['gap'].value_counts().sort_index().to_string())
