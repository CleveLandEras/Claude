"""Q117 复算：金卡以上占累计储值的比例、人数。只读，不带参数。"""
import pandas as pd

B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
a = a[~a['身份'].isin(['機器人', '測試帳號'])].copy()
amt = pd.to_numeric(a['总充值金额'], errors='coerce').fillna(0)
g = a['卡别'] >= 3
print('活跃', len(a), '金卡以上', int(g.sum()), round(g.mean() * 100, 2), '%')
print('金卡以上占累计储值', round(amt[g].sum() / amt.sum() * 100, 2), '%；普银', round(amt[~g].sum() / amt.sum() * 100, 2), '%')
print('普银人数', int((~g).sum()), round((~g).mean() * 100, 2), '%')
