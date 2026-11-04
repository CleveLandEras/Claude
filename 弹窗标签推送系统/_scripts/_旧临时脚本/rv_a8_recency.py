"""审查复算：A8 卡别 × 最后登录，A7 上界 9,786 / 3,638。独立写法：按日期字符串取日，卡别缺值单列。只读。"""
import os
import pandas as pd

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
print('原始', len(df), '身份取值', df['身份'].value_counts().to_dict())
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(df)
pay = pd.to_numeric(df['总充值金额'], errors='coerce')
print('剔除后', N, '充值缺值', int(pay.isna().sum()), '负值', int((pay < 0).sum()))
pay = pay.fillna(0)
df['pay'] = pay
TOTAL = pay.sum()
card = pd.to_numeric(df['卡别'], errors='coerce')
print('卡别缺值', int(card.isna().sum()), card.value_counts().sort_index().to_dict())
df['card'] = card
d = pd.to_datetime(df['最後登入時間'].astype(str).str[:10], errors='coerce')
df['gap'] = (pd.Timestamp('2026-09-16') - d).dt.days
print('gap 缺值', int(df['gap'].isna().sum()), 'min', df['gap'].min(), 'max', df['gap'].max())


def show(name, s):
    n = len(s)
    le3 = (s['gap'] <= 3).sum()
    le7 = (s['gap'] <= 7).sum()
    gt7 = n - le7
    print(f'{name} n={n} 0天={(s.gap==0).sum()} 0-3={le3}({le3/n*100:.2f}%) 0-7={le7}({le7/n*100:.2f}%) '
          f'>7={gt7}({gt7/n*100:.2f}%) 行储值占比={s.pay.sum()/TOTAL*100:.2f}% '
          f'>7储值占全部={s.loc[s.gap > 7, "pay"].sum()/TOTAL*100:.2f}% '
          f'>7占本行={s.loc[s.gap > 7, "pay"].sum()/s.pay.sum()*100:.2f}%')


show('全部', df)
show('普卡', df[df.card == 1])
show('银卡', df[df.card == 2])
show('金卡以上', df[df.card >= 3])
for c in [3, 4, 5, 6, 7]:
    show(f'卡别{c}', df[df.card == c])
print('0-3天储值占全部', f'{df.loc[df.gap <= 3, "pay"].sum()/TOTAL*100:.2f}%')

# A7 上界
ids = df['身份'].astype(str)
print('身份分布', ids.value_counts().to_dict())
bet_col = [c for c in df.columns if '押注' in c]
print('押注列', bet_col)
bet = pd.to_numeric(df[bet_col[0]], errors='coerce').fillna(0)
never = df.pay <= 0
pp = never & (bet > 10000)
nr = ids.isin(['新增', '回流'])
print('从未储值', int(never.sum()), '潜在付费上限', int(pp.sum()), '新增回流', int(nr.sum()),
      '新增回流∩潜在付费', int((nr & pp).sum()), '新增回流∩储值>0', int((nr & (df.pay > 0)).sum()))
print('新增∩储值>0', int(((ids == '新增') & (df.pay > 0)).sum()), '回流∩储值>0', int(((ids == '回流') & (df.pay > 0)).sum()))
