"""审查复算：R30 表 8b、敏感度、赠点比值旁证、对照分布（2026-09-28 12:28 审查）。只读，不带参数。"""
import os
import pandas as pd
import numpy as np

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
df = pd.read_csv(os.path.join(BASE, '数据', '近一月活跃_20260916.csv'), encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
amt = pd.to_numeric(df['总充值金额'], errors='coerce').fillna(0)
bet = pd.to_numeric(df['游戏总押注'], errors='coerce').fillna(0)
gift = pd.to_numeric(df['活动赠点'], errors='coerce').fillna(0)
card = pd.to_numeric(df['卡别'], errors='coerce')
ident = df['身份'].replace({'VIP': '持續', '黑名單': '持續'})
last = pd.to_datetime(df['最後登入時間'], errors='coerce').dt.normalize()
days = (pd.Timestamp('2026-09-16') - last).dt.days
print('N', len(df), '卡别取值', sorted(card.dropna().unique().tolist()), '卡别空', int(card.isna().sum()))
print('身份取值', ident.value_counts().to_dict())
nopay = amt <= 0
pay = amt > 0
pp = nopay & (bet > 10000)
print('nopay', int(nopay.sum()), 'pay', int(pay.sum()), 'pp', int(pp.sum()))
nr = pp & ident.isin(['新增', '回流'])
print('A7 下限', int(nr.sum()))
for th in [1e6, 1e7, 1e8]:
    m = nopay & (bet > th)
    grp = pd.cut(card[m], [0, 1, 2, 99], labels=['普', '银', '金+']).value_counts().to_dict()
    print(f'>{th:,.0f}', int(m.sum()), f'{m.sum()/nopay.sum()*100:.2f}% / {m.sum()/pp.sum()*100:.2f}%',
          grp, ident[m].value_counts().to_dict(), '0-7天', int((m & (days <= 7)).sum()),
          '剔后pp', int((pp & ~m).sum()), '剔后nopay', int((nopay & ~m).sum()), '剔后A7', int((nr & ~m).sum()))
    mp = pay & (bet > th)
    print('   有储值', int(mp.sum()), f'{mp.sum()/pay.sum()*100:.2f}%')
print('nopay P90 P99', bet[nopay].quantile(.9), bet[nopay].quantile(.99), 'pay P90', bet[pay].quantile(.9))
for name, m in [('pp', pp), ('pay', pay), ('nopay>1M', nopay & (bet > 1e6))]:
    t = m & (gift > 0)
    print(name, int(t.sum()), '比值中位', round((bet[t] / gift[t]).median(), 2))
hi = nopay & (card >= 2)
print('530', int(hi.sum()), 'min', bet[hi].min(), 'median', bet[hi].median(), 'max', bet[hi].max(),
      '>1M', int((hi & (bet > 1e6)).sum()))
# 同押注段对照：有储值者押注 >1M、以及 1M–1千万 段的比值中位
for name, m in [('pay>1M', pay & (bet > 1e6)), ('pay 1M-10M', pay & (bet > 1e6) & (bet <= 1e7)),
                ('nopay 1M-10M', nopay & (bet > 1e6) & (bet <= 1e7)), ('pp<=1M', pp & (bet <= 1e6))]:
    t = m & (gift > 0)
    print(name, int(t.sum()), '比值中位', round((bet[t] / gift[t]).median(), 2))
# 0 赠点者在 >1M 里的人数，看旁证覆盖
print('nopay>1M 赠点=0', int((nopay & (bet > 1e6) & (gift <= 0)).sum()))
# 回流有储值 0-7 天
rp = pay & (ident == '回流')
print('回流有储值 0-7', int((rp & (days <= 7)).sum()), int(rp.sum()))
