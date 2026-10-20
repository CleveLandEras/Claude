"""R77 复算：押注 1 千万–1 亿的普卡 120 人 / 银卡 512 人，平均每两个月押注（累计押注 ÷ 注册天数 × 61）不到 500 万的比例。只读，不带参数。
口径：押注段 (1e7, 1e8]，注册天数按日期相减、9/16 为第 0 天，注册天数 ≤ 0 的按 1 天计。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
p = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
ref = pd.Timestamp('2026-09-16')
d['regdays'] = (ref.normalize() - pd.to_datetime(d['注册时间'], errors='coerce').dt.normalize()).dt.days
seg = d[(d['游戏总押注'] > 1e7) & (d['游戏总押注'] <= 1e8)].copy()
seg['per2m'] = seg['游戏总押注'] / seg['regdays'].clip(lower=1) * 61
for c, name in [(1, '普卡'), (2, '银卡')]:
    g = seg[seg['卡别'] == c]
    print(name, len(g), ' 押注中位', round(g['游戏总押注'].median()), ' 注册天数中位', g['regdays'].median(),
          ' 每两个月押注中位', round(g['per2m'].median()), ' 不到 500 万 %.2f%%' % ((g['per2m'] < 5e6).mean() * 100))
