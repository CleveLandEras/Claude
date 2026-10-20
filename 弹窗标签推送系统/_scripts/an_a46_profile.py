# A46 人群画像：读 an_a45_members.load()，按 A45 口径给每类的规模、储值占比、特征区分度、集中度
import numpy as np
import pandas as pd
from an_a45_members import load

df, m = load()
pay, bet, idn, card, rtp, act, plat = m['pay'], m['bet'], m['idn'], m['card'], m['rtp'], m['act'], m['plat']
N = len(df)
TOT = df[pay].sum()
print('N', N, '累计储值总额', int(TOT))
print('登入平台取值', df[plat].value_counts().to_dict())
APP = ['android', 'ios', 'apk']
df['app'] = df[plat].astype(str).str.lower().isin(APP)
df['tier'] = np.where(df[card] == 1, '普卡', np.where(df[card] == 2, '银卡', '金卡以上'))
df['today'] = df['dsl'] == 0

groups = {
    '新增': df['is_new'],
    '回流（存量）': df['is_back'],
    '回流（在场）': df['back_present'],
    '潜在付费（上界）': df['pp_wide'],
    '潜在付费（可核实）': df['pp_verified'],
    '潜在流失（有储值，上界）': df['churn_ub'],
    '潜在流失（替代甲：有储值且在场）': df['churn_alt_a'],
    '破产（暴露上界：在场全体）': df['bk_ub_present'],
}

print('\n=== 一、画像总表 ===')
rows = []
for k, g in groups.items():
    s = df[g]
    rows.append(dict(类=k, 人数=len(s), 占比=round(len(s) / N * 100, 2),
                     储值占比=round(s[pay].sum() / TOT * 100, 2),
                     有储值率=round((s[pay] > 0).mean() * 100, 2),
                     普卡=round((s[card] == 1).mean() * 100, 1),
                     银卡=round((s[card] == 2).mean() * 100, 1),
                     金卡以上=round((s[card] >= 3).mean() * 100, 1),
                     在场率=round(s['present'].mean() * 100, 1),
                     当天登录=round(s['today'].mean() * 100, 1),
                     App=round(s['app'].mean() * 100, 1),
                     注册天数中位=s['age'].median(),
                     押注中位=s[bet].median(),
                     RTP中位=round(s[rtp].median(), 2),
                     活动赠点中位=s[act].median()))
pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 30)
print(pd.DataFrame(rows).to_string(index=False))
rest = df
print('全体基准：有储值率', round((df[pay] > 0).mean() * 100, 2), '在场率', round(df['present'].mean() * 100, 1),
      'App', round(df['app'].mean() * 100, 1), '注册天数中位', df['age'].median(), '押注中位', df[bet].median(),
      'RTP中位', round(df[rtp].median(), 2), '活动赠点中位', df[act].median(),
      '普卡', round((df[card] == 1).mean() * 100, 1), '银卡', round((df[card] == 2).mean() * 100, 1), '金卡以上', round((df[card] >= 3).mean() * 100, 1))

print('\n=== 二、区分度检验（本类 vs 非本类；整体 + 卡别内）===')
feats_pct = {'在场率': 'present', '当天登录率': 'today', 'App占比': 'app', '有储值率': 'has_paid'}
feats_med = {'注册天数': 'age', '累计押注': bet, 'RTP': rtp, '活动赠点': act}
# 各类的定义字段，不计
defn = {
    '新增': {'注册天数'},
    '回流（存量）': set(),
    '回流（在场）': {'在场率'},
    '潜在付费（上界）': {'有储值率', '累计押注'},
    '潜在流失（替代甲：有储值且在场）': {'有储值率', '在场率'},
}


def cmp(g, f, kind, sub=None):
    a = df[g] if sub is None else df[g & sub]
    b = df[~g] if sub is None else df[~g & sub]
    if len(a) < 50 or len(b) < 50:
        return None
    if kind == 'pct':
        return round(a[f].mean() * 100 - b[f].mean() * 100, 1), len(a), len(b)
    am, bm = a[f].median(), b[f].median()
    ratio = round(am / bm, 2) if bm not in (0, 0.0) else (np.inf if am > 0 else 1.0)
    return ratio, am, bm


for k, skip in defn.items():
    g = groups[k]
    print(f'\n--- {k}（n={g.sum():,}）---')
    for fname, f in feats_pct.items():
        if fname in skip:
            print(f'  {fname}: 定义字段，不计')
            continue
        o = cmp(g, f, 'pct')
        sub = {t: cmp(g, f, 'pct', df['tier'] == t) for t in ['普卡', '银卡', '金卡以上']}
        print(f'  {fname}: 整体差 {o[0]} 个百分点（本类{o[1]:,}/非本类{o[2]:,}）；卡别内', {t: (v[0] if v else 'n<50') for t, v in sub.items()})
    for fname, f in feats_med.items():
        if fname in skip:
            print(f'  {fname}: 定义字段，不计')
            continue
        o = cmp(g, f, 'med')
        sub = {t: cmp(g, f, 'med', df['tier'] == t) for t in ['普卡', '银卡', '金卡以上']}
        print(f'  {fname}: 中位数 本类{o[1]} / 非本类{o[2]} = {o[0]}倍；卡别内', {t: (v[0] if v else 'n<50') for t, v in sub.items()})

print('\n=== 三、集中度（类内按累计储值排序）===')
for k in ['新增', '回流（存量）', '回流（在场）', '潜在流失（有储值，上界）', '潜在流失（替代甲：有储值且在场）']:
    s = df[groups[k]]
    s = s[s[pay] > 0].sort_values(pay, ascending=False)
    tot = s[pay].sum()
    n = len(s)
    t1 = s.head(max(1, int(round(n * 0.01))))[pay].sum() / tot * 100
    t10 = s.head(max(1, int(round(n * 0.10))))[pay].sum() / tot * 100
    hi = s[s[card] >= 3]
    print(f'{k}: 有储值者 {n:,}，类内储值合计 {int(tot):,}，头部1% {t1:.1f}%，头部10% {t10:.1f}%，金卡以上 {len(hi):,}人 占类内储值 {hi[pay].sum() / tot * 100:.2f}%')

# R291：全体有储值者基准
s = df[df[pay] > 0].sort_values(pay, ascending=False)
tot = s[pay].sum()
n = len(s)
hi = s[s[card] >= 3]
print(f"全体有储值者（基准）: {n:,}，储值合计 {int(tot):,}，头部1% {s.head(int(round(n*0.01)))[pay].sum()/tot*100:.1f}%，头部10% {s.head(int(round(n*0.10)))[pay].sum()/tot*100:.1f}%，金卡以上 {len(hi):,}人（占活跃 {len(hi)/N*100:.2f}%）占储值 {hi[pay].sum()/tot*100:.2f}%")

# R293：回流存量卡别内是否达线（比例类差>=10点；连续类>=1.5倍或<=2/3）
print('\n=== 回流（存量）卡别内是否达线 ===')
g = groups['回流（存量）']
for fname, f, kind in [('当天登录率', 'today', 'pct'), ('有储值率', 'has_paid', 'pct'), ('累计押注', bet, 'med'), ('活动赠点', act, 'med'), ('在场率', 'present', 'pct')]:
    hit = []
    for t in ['普卡', '银卡', '金卡以上']:
        r = cmp(g, f, kind, df['tier'] == t)
        if r is None:
            hit.append('n<50')
        elif kind == 'pct':
            hit.append(f'{r[0]}:{"达线" if abs(r[0]) >= 10 else "未达"}')
        else:
            hit.append(f'{r[0]}:{"达线" if (r[0] >= 1.5 or r[0] <= 2/3) else "未达"}')
    print(' ', fname, hit)

# R292：潜在付费上界内持續在场老账号
pp = df[df['pp_wide']]
print('\n潜在付费上界 ∩ 持續 ∩ 在场 ∩ 注册≥365:', len(pp[(pp[idn] == '持續') & pp['present'] & (pp['age'] >= 365)]))
print('从未储值 持續 在场 注册≥365（不限押注）:', len(df[(df[idn] == '持續') & df['never_paid'] & df['present'] & (df['age'] >= 365)]))

print('\n=== 四、继承 A40 的反例复算 ===')
new = df[df['is_new']]
z = new[new[bet] == 0]
print('新增押注=0', len(z), f'{len(z) / len(new) * 100:.2f}%', '其中活动赠点恰1000', (z[act] == 1000).sum(), f'{(z[act] == 1000).mean() * 100:.2f}%')
print('新增 只来当天（注册后最后登录=注册当天附近）：在场且 age≤7?')
back = df[df['is_back']]
r0 = back[(back[pay] <= 0) & (back[bet] == 0)]
print('回流 从未储值且押注=0', len(r0), f'{len(r0) / len(back) * 100:.2f}%', '注册天数 min/中位', r0['age'].min(), r0['age'].median(), '满一年', (r0['age'] >= 365).sum())
print('回流 押注=0（不限储值）', (back[bet] == 0).sum())
old = df[(df[idn] == '持續') & df['never_paid'] & df['present'] & (df['age'] >= 365)]
print('持續 老账号（≥365 天）从未储值且在场', len(old), '（含VIP黑名單口径：身份=持續已排除）')
pp = df[df['pp_wide']]
print('潜在付费上界 在场', pp['present'].sum(), '注册≥365', (pp['age'] >= 365).sum(), f"{(pp['age'] >= 365).mean() * 100:.1f}%", '在场且≥365', (pp['present'] & (pp['age'] >= 365)).sum())

print('\n=== 五、替代口径（潜在流失）按卡别构成（不是目标人群画像）===')
a = df[df['churn_alt_a']]
print(a['tier'].value_counts().to_dict(), '累计储值中位按卡别', a.groupby('tier')[pay].median().to_dict())
print('替代乙（有储值且≥8天没来）卡别', df[df['churn_alt_b']]['tier'].value_counts().to_dict())
print('破产暴露上界（在场）按卡别', df[df['bk_ub_present']]['tier'].value_counts().to_dict())
