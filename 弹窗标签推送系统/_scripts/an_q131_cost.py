"""Q131 成本：赠点规模与集中度。只读；不使用「活动咬分比」。
数据：近一月活跃（剔除機器人、測試帳號；VIP、黑名單保留）。金额、点数都是账号累计值。
加赠点 = 充值赠点 − 100 × 总充值金额（只对储值 > 0 的人；推断口径：回馈比 100 = 1 元 100 点、无加赠）。
"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np, pandas as pd
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
B = _ROOT + '/数据/'
a = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
col = {k: [x for x in a.columns if k in x][0] for k in ['会员编号', '注册', '最後登入', '卡别', '总充值', '押注', '输赢', 'RTP', '活动赠点', '充值赠点', '回馈', '身份']}
ID, CARD, IDN = col['会员编号'], col['卡别'], col['身份']
a = a[~a[IDN].isin(['機器人', '測試帳號'])].copy()
print('人数', len(a), '身份', a[IDN].value_counts().to_dict())
ref = pd.Timestamp('2026-09-16')
a['age'] = (ref - pd.to_datetime(a[col['注册']], errors='coerce').dt.normalize()).dt.days
a['months'] = (a['age'] / 30.44).clip(lower=1)
a['S'] = a[col['总充值']]
a['ev'] = a[col['活动赠点']]
a['cz'] = a[col['充值赠点']]
a['bet'] = a[col['押注']]
a['hk'] = a[col['回馈']]

# ---------- S1 口径核验 ----------
print('\n== S1 口径核验')
for nm, c in [('活动赠点', 'ev'), ('充值赠点', 'cz'), ('回馈比', 'hk'), ('总充值金额', 'S'), ('押注', 'bet'), ('输赢', col['输赢']), ('RTP', col['RTP'])]:
    s = a[c]
    print(nm, '缺值', int(s.isna().sum()), '<0', int((s < 0).sum()), '=0', int((s == 0).sum()), '合计', round(float(s.sum()), 0))
neg = a[a.ev < 0]
print('活动赠点为负', len(neg), '卡别', neg[CARD].value_counts().sort_index().to_dict(), '身份', neg[IDN].value_counts().to_dict(),
      '负值合计', round(float(neg.ev.sum()), 0))
print('活动赠点合计：保留负值', round(float(a.ev.sum()), 0), '截为 0', round(float(a.ev.clip(lower=0).sum()), 0))
pay = a[a.S > 0].copy()
ok = (np.floor(pay.cz / pay.S) == pay.hk)
print('有储值者', len(pay), '回馈比=floor(充值赠点/总充值金额) 一致', int(ok.sum()), '一致率 %.4f%%' % (ok.mean() * 100))
pay['bonus'] = pay.cz - 100 * pay.S
print('加赠点<0 人数', int((pay.bonus < 0).sum()), '=0', int((pay.bonus == 0).sum()), '>0', int((pay.bonus > 0).sum()))
print('加赠点合计：保留负值', round(float(pay.bonus.sum()), 0), '截为 0', round(float(pay.bonus.clip(lower=0).sum()), 0), '占充值赠点合计 %.2f%%' % (pay.bonus.clip(lower=0).sum() / pay.cz.sum() * 100))
r = a[a.bet > 0]
chk = 100 + r[col['输赢']] / r.bet * 100
d = (r[col['RTP']] - chk).abs()
print('RTP 与 100+输赢/押注 差的绝对值：中位', round(float(d.median()), 4), '≤0.01 占 %.2f%%' % ((d <= 0.01).mean() * 100), '最大', round(float(d.max()), 3), '人数', len(r))
hkp10 = pay.hk.quantile(0.10)
print('有储值者回馈比 P10', hkp10, '中位', pay.hk.median(), '众数', pay.hk.mode().iloc[0])

# ---------- S2 规模与集中度 ----------
a['bonus'] = 0.0
a.loc[a.S > 0, 'bonus'] = (a.cz - 100 * a.S).clip(lower=0)
a['evc'] = a.ev.clip(lower=0)
a['Sc'] = a.S.clip(lower=0)
def grp(c):
    return {1: '普卡', 2: '银卡', 3: '金卡(3)', 4: '白金(4)', 5: '钻石(5)'}.get(c, '黑卡至尊(6–7)')
a['cg'] = a[CARD].map(grp)
TOT = {'ev': a.evc.sum(), 'bonus': a.bonus.sum(), 'S': a.Sc.sum(), 'bet': a.bet.sum(), 'n': len(a)}
def table(keys, minn=30):
    g = a.groupby(keys)
    t = g.apply(lambda x: pd.Series({
        'n': len(x),
        'n占%': len(x) / TOT['n'] * 100,
        '活动赠点占%': x.evc.sum() / TOT['ev'] * 100,
        '加赠点占%': x.bonus.sum() / TOT['bonus'] * 100,
        '累计储值占%': x.Sc.sum() / TOT['S'] * 100,
        '赠点/押注%': x.evc.sum() / x.bet.sum() * 100 if x.bet.sum() > 0 else np.nan,
        '赠点/(100×储值)%': x.evc.sum() / (100 * x.Sc.sum()) * 100 if x.Sc.sum() > 0 else np.nan,
        '月均活动赠点中位': (x.evc / x.months).median(),
        '月均活动赠点占%': (x.evc / x.months).sum() / (a.evc / a.months).sum() * 100,
        '差(赠点占-储值占)': x.evc.sum() / TOT['ev'] * 100 - x.Sc.sum() / TOT['S'] * 100,
    }))
    return t.round(2)
order = ['普卡', '银卡', '金卡(3)', '白金(4)', '钻石(5)', '黑卡至尊(6–7)']
print('\n== S2-a 按卡组')
t1 = table('cg').loc[order]; print(t1)
print('\n== S2-b 按身份')
print(table(IDN))
print('\n== S2-c 卡组 × 身份（n<30 只报人数）')
t2 = table(['cg', IDN])
t2.loc[t2.n < 30, [c for c in t2.columns if c != 'n' and c != 'n占%']] = np.nan
print(t2.reindex(order, level=0))
print('\n== 赠送强度：卡组 赠点/押注 最高/最低', round(t1['赠点/押注%'].max() / t1['赠点/押注%'].min(), 2), '；最高', t1['赠点/押注%'].idxmax(), '最低', t1['赠点/押注%'].idxmin())
# 集中度
def conc(s):
    s = s.sort_values(ascending=False); n = len(s)
    return round(s.head(n // 100).sum() / s.sum() * 100, 1), round(s.head(n // 10).sum() / s.sum() * 100, 1)
print('\n== 集中度（前 1% 人、前 10% 人占合计）：全体', len(a), '人')
print('活动赠点', conc(a.evc), '加赠点', conc(a.bonus), '累计储值', conc(a.Sc), '押注', conc(a.bet.clip(lower=0)))
print('月均活动赠点', conc(a.evc / a.months))
# 全平台
print('\n== 全平台')
print('活动赠点合计 ÷ 押注合计 %.4f%%' % (TOT['ev'] / TOT['bet'] * 100))
print('活动赠点合计', round(TOT['ev']), '折名义新台币（÷100）', round(TOT['ev'] / 100), '占累计储值合计 %.2f%%' % (TOT['ev'] / 100 / TOT['S'] * 100))
print('加赠点合计', round(TOT['bonus']), '折名义新台币（÷100）', round(TOT['bonus'] / 100), '占累计储值合计 %.2f%%' % (TOT['bonus'] / 100 / TOT['S'] * 100))
print('累计储值合计', round(TOT['S']), '押注合计', round(TOT['bet']))
# 大户（R 集合，与 A34 同口径）
a['days'] = (ref - pd.to_datetime(a[col['最後登入']]).dt.normalize()).dt.days
a['R'] = a.Sc / a.months
O1 = a[(a.days <= 7) & (a.S > 0) & ~a[IDN].isin(['VIP', '黑名單'])]
top = O1.nlargest(134, 'R')
print('\n== 大户（R 集合 134 人）占：活动赠点 %.2f%%  加赠点 %.2f%%  累计储值 %.2f%%  押注 %.2f%%' % (
    top.evc.sum() / TOT['ev'] * 100, top.bonus.sum() / TOT['bonus'] * 100, top.Sc.sum() / TOT['S'] * 100, top.bet.sum() / TOT['bet'] * 100))
# ---------- S3 基数：受影响人群 ----------
print('\n== S3 基数')
def base(nm, m):
    x = a[m]
    print(nm, '人数', len(x), '活动赠点占全体 %.2f%%' % (x.evc.sum() / TOT['ev'] * 100), '加赠点占 %.2f%%' % (x.bonus.sum() / TOT['bonus'] * 100), '累计储值占 %.2f%%' % (x.Sc.sum() / TOT['S'] * 100))
base('新增', a[IDN] == '新增')
base('回流', a[IDN] == '回流')
base('新增+回流', a[IDN].isin(['新增', '回流']))
base('金卡以上', a[CARD] >= 3)
base('金卡以上有储值', (a[CARD] >= 3) & (a.S > 0))
base('金卡以上有储值去VIP黑名單', (a[CARD] >= 3) & (a.S > 0) & ~a[IDN].isin(['VIP', '黑名單']))
base('普卡+银卡', a[CARD] <= 2)
base('新增里金卡以上', (a[IDN] == '新增') & (a[CARD] >= 3))
base('回流里金卡以上', (a[IDN] == '回流') & (a[CARD] >= 3))
base('从未储值', a.S <= 0)
base('从未储值且累计押注>1万', (a.S <= 0) & (a.bet > 10000))
# ---------- 反例 ----------
print('\n== 反例 ① 加赠基准改为 P10（%s）' % hkp10)
a['bonus2'] = 0.0
a.loc[a.S > 0, 'bonus2'] = (a.cz - hkp10 * a.S).clip(lower=0)
print('加赠点合计（P10 基准）', round(a.bonus2.sum()), '占充值赠点合计 %.2f%%' % (a.bonus2.sum() / a.loc[a.S > 0, 'cz'].sum() * 100))
g = a.groupby('cg').apply(lambda x: pd.Series({'基准100占%': x.bonus.sum() / TOT['bonus'] * 100, 'P10基准占%': x.bonus2.sum() / a.bonus2.sum() * 100, '累计储值占%': x.Sc.sum() / TOT['S'] * 100})).loc[order].round(2)
g['差(基准100)'] = g['基准100占%'] - g['累计储值占%']; g['差(P10)'] = g['P10基准占%'] - g['累计储值占%']
print(g)
print('排序（基准100）', list(g['基准100占%'].sort_values(ascending=False).index), '排序（P10）', list(g['P10基准占%'].sort_values(ascending=False).index))
print('\n== 反例 ② 去掉 VIP、黑名單后金卡以上一格与集中度')
b = a[~a[IDN].isin(['VIP', '黑名單'])]
hi = b[b[CARD] >= 3]
print('去 VIP/黑名單 金卡以上', len(hi), '活动赠点占（分母：去 VIP 黑名單全体）%.2f%%' % (hi.evc.sum() / b.evc.sum() * 100), '累计储值占 %.2f%%' % (hi.Sc.sum() / b.Sc.sum() * 100), '加赠点占 %.2f%%' % (hi.bonus.sum() / b.bonus.sum() * 100))
print('去 VIP/黑名單 集中度：活动赠点', conc(b.evc), '加赠点', conc(b.bonus), '累计储值', conc(b.Sc))
v = a[a[IDN] == 'VIP']
print('VIP 人数', len(v), '活动赠点占全体 %.2f%%' % (v.evc.sum() / TOT['ev'] * 100), '加赠点占 %.2f%%' % (v.bonus.sum() / TOT['bonus'] * 100), '累计储值占 %.2f%%' % (v.Sc.sum() / TOT['S'] * 100))
