"""Q37：复算 A8 表 3「≤ 1 万」段剔除 VIP 后银卡的押注构成，以及全体押注恰为 6,000 的人数。
复核 Q35 的「37 人中 32 人 2025 年以前注册」「45 人最后在浏览器登录」。不带参数运行。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
p = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('剔除后人数', len(d))
d['reg'] = pd.to_datetime(d['注册时间'], errors='coerce')
print('登入平台取值', d['登入平台'].value_counts(dropna=False).to_dict())

s = d[(d['卡别'] == 2) & (d['身份'] != 'VIP') & (d['游戏总押注'] <= 10000)].copy()
print('\n=== 非 VIP 银卡、押注 <= 1 万 ===  n =', len(s))
print('储值>0', (s['总充值金额'] > 0).sum(), '储值中位', s['总充值金额'].median())
b = s['游戏总押注']
print('押注取值分布：')
print(b.value_counts().sort_index().to_string())
grp = pd.Series('其他', index=s.index)
grp[b == 0] = '0'
grp[b == 6000] = '恰为6000'
grp[b == 5600] = '恰为5600'
grp[(b > 0) & (b < 2)] = '0.1-1.6(小于2)'
print('分组：', grp.value_counts().to_dict())
z = s[b == 0]
print('押注为0者', len(z), '其中2025年以前注册', (z['reg'] < '2025-01-01').sum(), '注册时间缺值', z['reg'].isna().sum())
print('押注为0者 身份', z['身份'].value_counts().to_dict())
print('60 人登入平台', s['登入平台'].value_counts().to_dict())
s6 = s[b == 6000]
print('恰为6000者 身份', s6['身份'].value_counts().to_dict(), '平台', s6['登入平台'].value_counts().to_dict(),
      '储值中位', s6['总充值金额'].median(), '注册年份', s6['reg'].dt.year.value_counts().sort_index().to_dict())

print('\n=== 全体押注恰为某值 ===')
B = d['游戏总押注']
for v in [5000, 6000, 7000, 10000]:
    print(v, int((B == v).sum()))
a6 = d[B == 6000]
print('全体恰为6000 卡别', a6['卡别'].value_counts().sort_index().to_dict(), '身份', a6['身份'].value_counts().to_dict(),
      '平台', a6['登入平台'].value_counts().to_dict(), '含VIP', int((a6['身份'] == 'VIP').sum()))
