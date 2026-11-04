"""审查者复算：全体活跃 62,292 人中前 10% 的累计储值占比。只读。"""
import pandas as pd

p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
a = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0).sort_values(ascending=False)
n = len(a)
for k in [int(n * 0.1), round(n * 0.1)]:
    print(n, k, f'{a.iloc[:k].sum() / a.sum() * 100:.2f}%')
