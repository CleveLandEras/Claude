"""设计卡 Q166 只读试算：近期注册者、回流者里累计充值 > 0 的占比，以及 P99 是否可能为 0。
只用来判断「P99 截尾值为 0」的退路是否需要写进卡，不作任何结论。累计值是上界（窗口内只会更少）。"""
import os
import pandas as pd
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
df['注册时间'] = pd.to_datetime(df['注册时间'], errors='coerce')
amt = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
df['amt'] = amt
end = pd.Timestamp('2026-09-16')
for days in (14, 30):
    sub = df[df['注册时间'] >= end - pd.Timedelta(days=days)]
    n = len(sub)
    pos = (sub['amt'] > 0).sum()
    print(f'注册于最近 {days} 天：{n} 人，累计充值>0 {pos} 人，占 {pos / max(n,1):.2%}，P99={sub["amt"].quantile(0.99):.0f}')
for s in ('新增', '回流'):
    sub = df[df['身份'] == s]
    n = len(sub)
    pos = (sub['amt'] > 0).sum()
    print(f'身份={s}：{n} 人，累计充值>0 {pos} 人，占 {pos / max(n,1):.2%}，P99={sub["amt"].quantile(0.99):.0f}')
