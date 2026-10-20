"""设计卡 Q195 只读试算：回流用户的活动赠点是否有一个固定值（线索：回流任务的奖励大小）。
只用来决定方法里怎么切分，不作结论。回流与持續只在普卡、注册满一年内比，避免卡别、注册时长的混杂。"""
import os
import pandas as pd
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
df['注册时间'] = pd.to_datetime(df['注册时间'], errors='coerce')
end = pd.Timestamp('2026-09-16')
df['reg_days'] = (end - df['注册时间']).dt.days
df['pts'] = pd.to_numeric(df['活动赠点'], errors='coerce').fillna(0)
df['bet'] = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
df['amt'] = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
print('列：', list(df.columns))
base = df[(df['卡别'] == 1) & (df['reg_days'] >= 365) & (df['身份'].isin(['回流', '持續']))]
print('普卡且注册满一年：', base['身份'].value_counts().to_dict())
for ident in ('回流', '持續'):
    sub = base[base['身份'] == ident]
    n = len(sub)
    print(f'\n== {ident} n={n}  活动赠点 Top12 值（占比，分母={n}）')
    vc = sub['pts'].round(0).value_counts().head(12)
    for v, c in vc.items():
        print(f'  {v:>10.0f}  {c:>6}  {c / n:.2%}')
    for lo, hi in ((0, 1), (1, 500), (500, 501), (501, 1000), (1000, 1001), (1001, 5000), (5000, 1e12)):
        m = ((sub['pts'] >= lo) & (sub['pts'] < hi)).sum()
        print(f'  赠点[{lo},{hi}) {m} {m / n:.2%}')
print('\n== 回流全体（不限卡别）活动赠点恰为 500 的人')
r = df[df['身份'] == '回流']
g = r[r['pts'].round(0) == 500]
print('人数', len(g), '占回流', f'{len(g) / len(r):.2%}', '押注为0', (g['bet'] == 0).sum(), '押注中位', g['bet'].median(),
      '有储值', (g['amt'] > 0).sum(), '注册龄中位', g['reg_days'].median())
print('卡别分布', g['卡别'].value_counts().to_dict())
print('最后登录天数分布（0-7 / 8+）：')
last = pd.to_datetime(g['最後登入時間'], errors='coerce')
d = (end - last.dt.normalize()).dt.days
print('  0-7:', (d <= 7).sum(), ' 8+:', (d > 7).sum())
print('\n== 对照：持續恰为 500 的人', ((df['身份'] == '持續') & (df['pts'].round(0) == 500)).sum(),
      ' 新增恰为 500：', ((df['身份'] == '新增') & (df['pts'].round(0) == 500)).sum())
