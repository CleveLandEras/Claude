"""审查复算 Q54（只读）：首储 = 50 元、16,800 点。独立写法：直接按储值额与充值赠点，不经回馈比。"""
import pandas as pd

P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(d)
pay = d[d['总充值金额'] > 0].copy()
NP = len(pay)
pay['A'] = pay['总充值金额'].round(2)
pay['G'] = pay['充值赠点'].round(0)
print('N', N, 'NP', NP)

s50 = pay[pay['A'] == 50]
print('储值=50 人数', len(s50), '赠点分布', s50['G'].value_counts().head(6).to_dict())
fb = pay[(pay['A'] == 50) & (pay['G'] == 16800)]
f15 = pay[(pay['A'] == 50) & (pay['G'] == 15000)]
print('只买首储 16800:', len(fb), '%.2f%% / %.2f%%' % (len(fb) / NP * 100, len(fb) / N * 100), '储值合计', fb['总充值金额'].sum())
print('50@15000:', len(f15), '占储值=50 %.2f%%' % (len(f15) / len(s50) * 100), '; 16800 占储值=50 %.2f%%' % (len(fb) / len(s50) * 100))
print('赠点恰为 16800 的储值额', pay[pay['G'] == 16800]['A'].value_counts().to_dict())

# 组合：首储 + 一个已知档位（各档用 an_q54 的赠点众数）
tiers = [(70, 14000), (30, 10000), (33, 10000), (30, 3000), (30, 3240), (50, 5000), (60, 6240), (50, 15000)]
tot = 0
hit_ids = set()
for a, g in tiers:
    s = pay[(pay['A'] == 50 + a) & (pay['G'] == 16800 + g)]
    print('首储+', (a, g), '->', (50 + a, 16800 + g), len(s))
    tot += len(s)
    hit_ids |= set(s.index)
print('组合合计', tot, '去重', len(hit_ids), '下界2', len(fb) + len(hit_ids))
# 组合 120 元 30800 是否也可能是别的解？列 120 元的赠点分布
print('储值=120 赠点前 6', pay[pay['A'] == 120]['G'].value_counts().head(6).to_dict())

# 画像
ref = pd.Timestamp('2026-09-16')
fbd = d.loc[fb.index].copy()
fbd['reg'] = (ref - pd.to_datetime(fbd['注册时间'], errors='coerce').dt.normalize()).dt.days
fbd['last'] = (ref - pd.to_datetime(fbd['最後登入時間'], errors='coerce').dt.normalize()).dt.days
print('普卡 %.2f' % ((fbd['卡别'] == 1).mean() * 100))
print('身份', (fbd['身份'].value_counts(normalize=True) * 100).round(2).to_dict())
print('注册<91天 %.2f' % ((fbd['reg'] <= 90).mean() * 100), ' 注册<=29 %.2f' % ((fbd['reg'] <= 29).mean() * 100))
print('0-7天 %.2f' % ((fbd['last'] <= 7).mean() * 100))
pl = fbd['登入平台'].astype(str).str.lower()
print('浏览器类 %.2f' % (pl.isin(['web', 'mweb', 'mh5', 'h5']).mean() * 100), pl.value_counts().to_dict())
print('押注中位', fbd['游戏总押注'].median(), ' >10万 %.2f' % ((fbd['游戏总押注'] > 100000).mean() * 100))

nw = d[(d['身份'] == '新增') & (d['总充值金额'] > 0)].copy()
nA = nw['总充值金额'].round(2); nG = nw['充值赠点'].round(0)
print('新增有储值', len(nw), '50元', int((nA == 50).sum()), '16800', int(((nA == 50) & (nG == 16800)).sum()), '15000', int(((nA == 50) & (nG == 15000)).sum()))
print('其他有储值', NP - len(fb) - len(f15))
