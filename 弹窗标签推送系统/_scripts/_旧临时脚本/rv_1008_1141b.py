# 审查者复算（只读）：普卡回流「从未储值且押注 0」2,524 人的注册龄分布
import pandas as pd

P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
ref = pd.Timestamp('2026-09-16')
df['age'] = (ref - pd.to_datetime(df['注册时间'], errors='coerce').dt.normalize()).dt.days
rp = df[(df['身份'] == '回流') & (df['卡别'] == 1)]
nz = rp[(rp['总充值金额'] <= 0) & (rp['游戏总押注'] == 0)]
print(len(nz))
print(nz['age'].describe())
print('注册>=365天', (nz['age'] >= 365).sum(), round((nz['age'] >= 365).mean() * 100, 2))
print('注册>=180天', (nz['age'] >= 180).sum())
print('活动赠点分布', nz['活动赠点'].value_counts().head(5).to_dict())
print('游戏总输赢=0', (nz['游戏总输赢'] == 0).sum())
