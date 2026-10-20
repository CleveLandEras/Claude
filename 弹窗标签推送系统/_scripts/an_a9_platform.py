"""A9 登录平台分布（推进计划 Q28）。不带参数运行，只读。
口径：剔除身份为機器人、測試帳號后 62,292 人；「登入平台」去首尾空格，大写 Web 并入 web；缺值单列。
App 类 = android、ios、apk；浏览器类 = mweb、web、h5、mh5。
潜在付费（上限代理）= 累计储值 ≤ 0 且累计押注 > 10,000（25,972 人）。
最后登录天数 = 9/16 与最后登录日期（字符串前 10 位）相减。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
raw = pd.read_csv(P, encoding='utf-8-sig')
print('原始行数', len(raw))

# ---- bo 等取值在剔除前后的分布 ----
rp = raw['登入平台'].astype('string').str.strip()
print('\n== 剔除前「登入平台」取值 × 身份（只列非主要平台与机器人、测试）==')
print(pd.crosstab(rp.fillna('缺值'), raw['身份'], margins=True).to_string())

d = raw[~raw['身份'].isin(['機器人', '測試帳號'])].copy()
print('\n剔除后', len(d))
pf = d['登入平台'].astype('string').str.strip().fillna('缺值')
print('大写 Web 人数', int((pf == 'Web').sum()), '缺值人数', int((pf == '缺值').sum()))
# 注意：先 fillna 再替换；若先用 where(pf != 'Web')，缺值的比较结果为 NA，会被误并入 web
pf = pf.mask(pf == 'Web', 'web')
d['平台'] = pf
APP = ['android', 'ios', 'apk']
BRW = ['mweb', 'web', 'h5', 'mh5']
d['类'] = d['平台'].map(lambda x: 'App 类' if x in APP else ('浏览器类' if x in BRW else ('缺值' if x == '缺值' else '其他')))
d['卡组'] = pd.cut(d['卡别'], [0, 1, 2, 7], labels=['普卡', '银卡', '金卡以上']).astype(str)
d['身份4'] = d['身份'].map({'新增': '新增', '回流': '回流', '持續': '持續'}).fillna('其他（VIP、黑名單）')
d['储值'] = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
d['押注'] = pd.to_numeric(d['游戏总押注'], errors='coerce').fillna(0)
d['潜在付费'] = (d['储值'] <= 0) & (d['押注'] > 10000)
d['天'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間'].astype(str).str[:10])).dt.days
N = len(d)
TOT = d['储值'].sum()
print('全部累计储值', int(TOT), '潜在付费', int(d['潜在付费'].sum()))


def summ(g):
    n = len(g)
    pay = g[g['储值'] > 0]
    return pd.Series({
        '人数': n,
        '占全部%': round(n / N * 100, 2),
        '储值占全部%': round(g['储值'].sum() / TOT * 100, 2),
        '储值率%': round(len(pay) / n * 100, 2) if n else None,
        '有储值者中位数': pay['储值'].median() if len(pay) else None,
        '人均储值': round(g['储值'].sum() / n, 1) if n else None,
        '金卡以上人数': int((g['卡组'] == '金卡以上').sum()),
        '金卡以上%': round((g['卡组'] == '金卡以上').mean() * 100, 2),
        '0–7天%': round((g['天'] <= 7).mean() * 100, 2),
        '潜在付费人数': int(g['潜在付费'].sum()),
    })


pd.set_option('display.width', 250)
print('\n== 表 1 按平台 ==')
t1 = d.groupby('平台')[list(d.columns)].apply(summ).sort_values('人数', ascending=False)
print(t1.to_string())
print('\n== 表 1b 按两类 ==')
t1b = d.groupby('类')[list(d.columns)].apply(summ)
print(t1b.to_string())
print('合计', summ(d).to_dict())

for dim in ['卡组', '身份4']:
    print(f'\n== 表 2 类 × {dim}：人数 ==')
    ct = pd.crosstab(d['类'], d[dim], margins=True)
    print(ct.to_string())
    print(f'-- 列内占比（该{dim}里各类的占比，%）--')
    print((pd.crosstab(d['类'], d[dim], normalize='columns') * 100).round(2).to_string())
    print(f'-- 储值占全部%（按格）--')
    print((d.pivot_table(index='类', columns=dim, values='储值', aggfunc='sum') / TOT * 100).round(2).to_string())
    print(f'-- 列内储值占比（该{dim}储值里各类的占比，%）--')
    pv = d.pivot_table(index='类', columns=dim, values='储值', aggfunc='sum')
    print((pv / pv.sum() * 100).round(2).to_string())

print('\n== 表 3 类 × 潜在付费（上限）==')
ct = pd.crosstab(d['类'], d['潜在付费'], margins=True)
print(ct.to_string())
print((pd.crosstab(d['类'], d['潜在付费'], normalize='columns') * 100).round(2).to_string())

print('\n== 平台 × 身份4 人数（核对回流中 mweb）==')
print(pd.crosstab(d['平台'], d['身份4'], margins=True).to_string())
print('\n== 平台 × 卡组 人数 ==')
print(pd.crosstab(d['平台'], d['卡组'], margins=True).to_string())

# ---- 反例检查：web 储值占比高是否少数大户造成 ----
print('\n== 反例检查：各平台储值集中度 ==')
for p in ['web', 'android', 'ios', 'mweb', 'apk']:
    g = d[d['平台'] == p]
    s = g['储值'].sort_values(ascending=False)
    tot = s.sum()
    top10 = s.head(10).sum()
    top1p = s.head(max(1, int(round(len(s) * 0.01)))).sum()
    print(f'[{p}] 人数 {len(g)}，储值 {int(tot)}（占全部 {tot / TOT * 100:.2f}%）；前 10 名 {int(top10)}（占本平台 {top10 / tot * 100:.2f}%，占全部 {top10 / TOT * 100:.2f}%）；'
          f'前 1%（{max(1, int(round(len(s) * 0.01)))} 人）占本平台 {top1p / tot * 100:.2f}%；去掉前 10 名后占全部 {(tot - top10) / (TOT - 0) * 100:.2f}%')
print('\n全体储值前 10 名的平台：')
print(d.sort_values('储值', ascending=False).head(10)[['平台', '卡组']].value_counts().to_string())
print('全体储值前 100 名的平台：')
print(d.sort_values('储值', ascending=False).head(100)['平台'].value_counts().to_string())
print('全体储值前 1%（623 人）的平台：')
print(d.sort_values('储值', ascending=False).head(623)['平台'].value_counts().to_string())

print('\n== 金卡以上内部：平台分布与储值 ==')
g = d[d['卡组'] == '金卡以上']
gt = g['储值'].sum()
x = g.groupby('平台').agg(人数=('储值', 'size'), 储值=('储值', 'sum'), 中位数=('储值', 'median'))
x['人数%'] = (x['人数'] / len(g) * 100).round(2)
x['储值占金卡以上%'] = (x['储值'] / gt * 100).round(2)
print(x.sort_values('人数', ascending=False).to_string())
print('金卡以上内部按类：')
y = g.groupby('类').agg(人数=('储值', 'size'), 储值=('储值', 'sum'))
y['人数%'] = (y['人数'] / len(g) * 100).round(2)
y['储值%'] = (y['储值'] / gt * 100).round(2)
print(y.to_string())

print('\n== 卡别 3–7 × 平台 web 占比 ==')
for c in range(1, 8):
    g = d[d['卡别'] == c]
    print(c, len(g), 'web', int((g['平台'] == 'web').sum()), f"{(g['平台'] == 'web').mean() * 100:.2f}%",
          '浏览器类', f"{(g['类'] == '浏览器类').mean() * 100:.2f}%")
