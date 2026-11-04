# 设计者试算（只读）：Q68 / Q69 设计卡用的人群规模，只用于确定切分，不下结论
import pandas as pd
base = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(base + '近一月活跃_20260916.csv', encoding='utf-8-sig')
a = a[~a['身份'].isin(['機器人', '測試帳號'])].copy()
print('活跃剔除后', len(a))
t = pd.to_datetime(a['最後登入時間'], errors='coerce')
a['days'] = (pd.Timestamp('2026-09-16') - t.dt.normalize()).dt.days
a['grp'] = a['卡别'].map(lambda c: '普银' if c in (1, 2) else '金卡以上')
main = a[~a['身份'].isin(['VIP', '黑名單'])]
print('主数（剔除 VIP 黑名单）', len(main))
d07 = main[main['days'] <= 7]
print('0-7 天', len(d07))
print(pd.crosstab(d07['grp'], d07['身份'], margins=True))
pay = d07['总充值金额'] > 0
print('0-7 天 有储值 by 卡组'); print(pd.crosstab(d07['grp'], pay, margins=True))
print('全体主数 有储值 by 卡组'); print(pd.crosstab(main['grp'], main['总充值金额'] > 0, margins=True))
print('0-7 天 押注>0', int((d07['游戏总押注'] > 0).sum()))
