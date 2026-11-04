"""审查复算 Q53（只读）：押注 1 千万–1 亿的普卡与银卡，按注册时长摊到每两个月的平均押注，看是否可能从未在任一两个月内押满 500 万。"""
import pandas as pd

P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
ref = pd.Timestamp('2026-09-16')
d['regdays'] = (ref - pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()).dt.days
d['last'] = (ref - pd.to_datetime(d['最後登入時間'], errors='coerce').dt.normalize()).dt.days
b = d[(d['游戏总押注'] > 1e7) & (d['游戏总押注'] <= 1e8)].copy()
b['per2m'] = b['游戏总押注'] / (b['regdays'].clip(lower=61) / 61)
for c, name in [(1, '普卡'), (2, '银卡')]:
    s = b[b['卡别'] == c]
    print(name, len(s), '注册天数中位', s['regdays'].median(), '押注中位', s['游戏总押注'].median(),
          '每两月平均押注中位 %.0f' % s['per2m'].median(),
          '每两月平均 < 500万 占 %.2f%%' % ((s['per2m'] < 5e6).mean() * 100),
          '0-7天 %.2f%%' % ((s['last'] <= 7).mean() * 100))
    lo = s[s['per2m'] < 5e6]
    hi = s[s['per2m'] >= 5e6]
    print('   平均<500万:', len(lo), '0-7天 %.2f%%' % ((lo['last'] <= 7).mean() * 100) if len(lo) else '',
          ' 平均>=500万:', len(hi), '0-7天 %.2f%%' % ((hi['last'] <= 7).mean() * 100) if len(hi) else '')
