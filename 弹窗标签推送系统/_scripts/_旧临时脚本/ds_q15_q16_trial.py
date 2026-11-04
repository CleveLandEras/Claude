"""设计者试算（只读）：为 Q15、Q16 设计卡确定切分与阈值，不产出结论。"""
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
act_raw = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
print('列：', list(act_raw.columns))

ref = pd.Timestamp('2026-09-16')
def days(s):
    return (ref - pd.to_datetime(s.astype(str).str[:10], errors='coerce')).dt.days

act_raw['d_last'] = days(act_raw['最後登入時間'])
act_raw['d_reg'] = days(act_raw['注册时间'])

# (a) 机器人与测试账号
bots = act_raw[act_raw['身份'].isin(['機器人', '測試帳號'])]
print('\n[a] 机器人/测试 行数：', len(bots))
print(bots.groupby('身份').agg(n=('会员编号', 'size'),
                              last0_7=('d_last', lambda x: (x <= 7).sum()),
                              pay_pos=('总充值金额', lambda x: (x > 0).sum()),
                              bet_pos=('游戏总押注', lambda x: (x > 0).sum())))
print('机器人/测试 卡别分布：', bots['卡别'].value_counts().sort_index().to_dict())
print('机器人/测试 平台缺值：', bots['登入平台'].isna().sum())
print('机器人/测试 注册<=30天：', (bots['d_reg'] <= 30).sum())

act = act_raw[~act_raw['身份'].isin(['機器人', '測試帳號'])].copy()
print('\n剔除后：', len(act))

# (b) 新增身份 vs 注册 30 天以内
reg30 = act['d_reg'] <= 30
new = act['身份'] == '新增'
print('\n[b] 身份新增：', new.sum(), '；注册<=30天：', reg30.sum(),
      '；两者都满足：', (new & reg30).sum(), '；新增但>30天：', (new & ~reg30).sum(),
      '；<=30天但非新增：', (~new & reg30).sum())
print('<=30天但非新增 的身份：', act.loc[~new & reg30, '身份'].value_counts().to_dict())
print('注册天数 29/30/31 各多少：', act['d_reg'].value_counts().reindex([28, 29, 30, 31, 32]).to_dict())

# (c) 金卡以上 按最后登录分档 的储值集中度
hi = act[act['卡别'] >= 3].copy()
tot = act['总充值金额'].sum()
bins = [-1, 0, 3, 7, 14, 31]
labels = ['0', '1-3', '4-7', '8-14', '15-31']
hi['bk'] = pd.cut(hi['d_last'], bins=bins, labels=labels)
print('\n[c] 金卡以上 6,366：')
for b, g in hi.groupby('bk', observed=True):
    s = g['总充值金额'].sort_values(ascending=False)
    top10 = s.head(10).sum() / s.sum() if s.sum() else 0
    print(f'  {b}: n={len(g)} 储值占全部={s.sum()/tot:.4%} 前10占本档={top10:.2%} 中位={s.median():.0f} VIP={int((g["身份"]=="VIP").sum())}')
g8 = hi[hi['d_last'] >= 8]
s = g8['总充值金额'].sort_values(ascending=False)
print(f'  8天以上合计 n={len(g8)} 占全部={s.sum()/tot:.4%} 前10占={s.head(10).sum()/s.sum():.2%} 去VIP后 n={int((g8["身份"]!="VIP").sum())} 占={g8.loc[g8["身份"]!="VIP","总充值金额"].sum()/tot:.4%}')
print('  8天以上 按卡别：', g8['卡别'].value_counts().sort_index().to_dict())
print('  8天以上 按身份：', g8['身份'].value_counts().to_dict())
# 按每档的日均人数
for lo, hi_ in [(0, 7), (8, 14), (15, 31)]:
    n = ((hi['d_last'] >= lo) & (hi['d_last'] <= hi_)).sum()
    print(f'  {lo}-{hi_}天 日均 {n/(hi_-lo+1):.1f}')

# (d) 普卡银卡 有储值者（ID10/11 可能命中的上限）与金卡以上有储值者
print('\n[d] 有储值：普银', int(((act['卡别'] <= 2) & (act['总充值金额'] > 0)).sum()),
      '金卡以上', int(((act['卡别'] >= 3) & (act['总充值金额'] > 0)).sum()))
