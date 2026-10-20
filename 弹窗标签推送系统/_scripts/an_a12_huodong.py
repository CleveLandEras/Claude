"""A12 活动赠点与新增参与（Q33）。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import numpy as np
import pandas as pd

P = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
N = len(d)
d['tenure'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['注册时间']).dt.normalize()).dt.days
d['days'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間']).dt.normalize()).dt.days
d['plat'] = d['登入平台'].fillna('缺值').astype(str).str.strip().replace({'Web': 'web'})
d['pcls'] = np.where(d['plat'].isin(['android', 'ios', 'apk']), 'App', np.where(d['plat'] == '缺值', '缺值', '浏览器'))
H = d['活动赠点']
print('N', N, ' 活动赠点缺值', H.isna().sum(), ' <0', (H < 0).sum(), ' min/max', H.min(), H.max())
IDS = ['新增', '回流', '持續', 'VIP', '黑名單']

# ---- ① 注册赠送 ----
print('\n== 表1 注册当天（注册天数 0）的新增')
z = d[(d['身份'] == '新增') & (d['tenure'] == 0)]
print('人数', len(z), ' 赠点>0 %.2f%%' % ((z['活动赠点'] > 0).mean() * 100), ' 恰为1000 %d（%.2f%%）' % ((z['活动赠点'] == 1000).sum(), (z['活动赠点'] == 1000).mean() * 100))
print('取值前 8', z['活动赠点'].value_counts().head(8).to_dict())
print('赠点=0 的人数', (z['活动赠点'] == 0).sum(), ' 押注中位', z['游戏总押注'].median())
for t in [1, 2, 3, 7]:
    y = d[(d['身份'] == '新增') & (d['tenure'] == t)]
    print('注册天数 %d 的新增 %d 人：赠点>0 %.2f%%，=1000 %.2f%%，>1000 %.2f%%' % (t, len(y), (y['活动赠点'] > 0).mean() * 100, (y['活动赠点'] == 1000).mean() * 100, (y['活动赠点'] > 1000).mean() * 100))

print('\n== 表2 各身份：活动赠点 =0 / 0–1000 / =1000 / >1000（行%）')
rows = []
for s in IDS + ['全部']:
    x = d if s == '全部' else d[d['身份'] == s]
    h = x['活动赠点']
    rows.append([s, len(x), (h == 0).mean() * 100, ((h > 0) & (h < 1000)).mean() * 100, (h == 1000).mean() * 100,
                 (h > 1000).mean() * 100, (h > 0).mean() * 100, (h <= 1000).mean() * 100, (h == 1000).sum()])
t2 = pd.DataFrame(rows, columns=['身份', 'n', '=0', '0–1000', '=1000', '>1000', '>0（原口径）', '≤1000', '=1000人数']).round(2)
print(t2.to_string(index=False))

print('\n== 表3 活动赠点高频取值（全体前 15）；新增前 10；回流前 10')
print(H.value_counts().head(15).to_dict())
print(d.loc[d['身份'] == '新增', '活动赠点'].value_counts().head(10).to_dict())
print(d.loc[d['身份'] == '回流', '活动赠点'].value_counts().head(10).to_dict())
# 1000 附近的取值
near = H[(H > 1000) & (H <= 1200)]
print('1000<赠点≤1200 人数', len(near), ' 前 8 值', near.value_counts().head(8).to_dict())

# 注册年份 × 是否 ≥1000（老账号是否也拿过 1000）
d['ry'] = pd.to_datetime(d['注册时间']).dt.year
print('\n== 注册年份：人数、赠点≥1000 比例、=1000 比例、赠点中位')
print(d.groupby('ry').agg(n=('活动赠点', 'size'), ge1000=('活动赠点', lambda h: round((h >= 1000).mean() * 100, 2)),
      eq1000=('活动赠点', lambda h: round((h == 1000).mean() * 100, 2)), med=('活动赠点', 'median')).to_string())

# ---- ② 参与口径与门槛敏感性 ----
print('\n== 表4 「活动赠点超过注册赠送」口径的门槛敏感性（按身份，行%）')
ths = [0, 1000, 1100, 1500, 2000, 5000]
rows = []
for s in IDS + ['全部']:
    x = d if s == '全部' else d[d['身份'] == s]
    rows.append([s, len(x)] + [round((x['活动赠点'] > t).mean() * 100, 2) for t in ths])
print(pd.DataFrame(rows, columns=['身份', 'n'] + ['>%d' % t for t in ths]).to_string(index=False))
# 对照原表「得到过活动赠点」：持续 97.91、回流 89.07、新增 97.02（原口径 >0）

# ---- ③ 新增：=1000 vs 其余 ----
def prof(x, name):
    b = x['游戏总押注']
    return pd.Series({
        '人群': name, 'n': len(x),
        '押注中位': b.median(), '押注=0%': (b == 0).mean() * 100, '押注≤100%': (b <= 100).mean() * 100,
        '押注≤1000%': (b <= 1000).mean() * 100, '押注>1万%': (b > 1e4).mean() * 100,
        '注册≤7天%': (x['tenure'] <= 7).mean() * 100, '注册天数中位': x['tenure'].median(),
        '最后登录0天%': (x['days'] == 0).mean() * 100, '最后登录0–7天%': (x['days'] <= 7).mean() * 100,
        '最后登录≥15天%': (x['days'] >= 15).mean() * 100,
        '浏览器类%': (x['pcls'] == '浏览器').mean() * 100, '有储值%': (x['总充值金额'] > 0).mean() * 100,
        '会员等级中位': x['会员等级'].median(),
    })

new = d[d['身份'] == '新增']
ret = d[d['身份'] == '回流']
print('\n== 表5 新增：赠点=1000 / <1000 / >1000 / 全部新增')
t5 = pd.DataFrame([prof(new[new['活动赠点'] == 1000], '新增·=1000'), prof(new[new['活动赠点'] < 1000], '新增·<1000'),
                   prof(new[new['活动赠点'] > 1000], '新增·>1000'), prof(new, '新增全部')])
print(t5.round(2).T.to_string())

# 新增 =1000 按注册天数分段：排除「刚注册、还没来得及玩」
print('\n== 表6 新增按注册天数分段：人数、=1000 的比例、=1000 者押注中位、=1000 者最后登录 = 注册日的比例')
tb = [-1, 0, 3, 7, 14, 21, 31]
tl = ['0', '1–3', '4–7', '8–14', '15–21', '22–31']
new = new.copy()
new['tb'] = pd.cut(new['tenure'], tb, labels=tl)
new['same'] = new['tenure'] == new['days']  # 最后登录日 = 注册日
for t in tl:
    x = new[new['tb'] == t]
    e = x[x['活动赠点'] == 1000]
    print(t, len(x), '=1000 %d（%.2f%%）' % (len(e), len(e) / len(x) * 100 if len(x) else 0),
          '押注中位 %.0f' % e['游戏总押注'].median(), '最后登录=注册日 %.2f%%' % (e['same'].mean() * 100))
print('新增注册天数范围', new['tenure'].min(), new['tenure'].max(), ' 缺值', new['tenure'].isna().sum())
e = new[new['活动赠点'] == 1000]
print('新增 =1000 共 %d：最后登录=注册日 %d（%.2f%%）' % (len(e), e['same'].sum(), e['same'].mean() * 100))
print('新增 =1000 且注册 ≥8 天 %d 人，其中最后登录距今 ≥7 天 %d' % ((e['tenure'] >= 8).sum(), ((e['tenure'] >= 8) & (e['days'] >= 7)).sum()))
print('登录平台（=1000 新增）', e['plat'].value_counts().to_dict())
print('登录平台（其余新增）', new[new['活动赠点'] != 1000]['plat'].value_counts().to_dict())

# ---- ④ 回流同样一行 ----
print('\n== 表7 回流：赠点≤1000 / =1000 / >1000')
t7 = pd.DataFrame([prof(ret[ret['活动赠点'] <= 1000], '回流·≤1000'), prof(ret[ret['活动赠点'] == 1000], '回流·=1000'),
                   prof(ret[ret['活动赠点'] > 1000], '回流·>1000'), prof(ret, '回流全部')])
print(t7.round(2).T.to_string())
r0 = ret[ret['活动赠点'] <= 1000]
print('回流 ≤1000：赠点=0 %d，0<赠点<1000 %d，=1000 %d' % ((r0['活动赠点'] == 0).sum(), ((r0['活动赠点'] > 0) & (r0['活动赠点'] < 1000)).sum(), (r0['活动赠点'] == 1000).sum()))
print('回流 ≤1000 的注册年份分布', r0['ry'].value_counts().sort_index().to_dict())

# 持續 对照
cont = d[d['身份'] == '持續']
print('\n== 持續 对照：=0 %.2f%%，≤1000 %.2f%%，押注中位（≤1000 者）%.0f' % ((cont['活动赠点'] == 0).mean() * 100, (cont['活动赠点'] <= 1000).mean() * 100, cont.loc[cont['活动赠点'] <= 1000, '游戏总押注'].median()))

# 环节1 第一节表的「持续」列 = 持續 + VIP + 黑名單（34,979 人）
oth = d[d['身份'].isin(['持續', 'VIP', '黑名單'])]
print('\n环节1 表口径「持续」%d 人：>0 %.2f%%（%d），>1000 %.2f%%（%d），>2000 %.2f%%' % (
    len(oth), (oth['活动赠点'] > 0).mean() * 100, (oth['活动赠点'] > 0).sum(), (oth['活动赠点'] > 1000).mean() * 100, (oth['活动赠点'] > 1000).sum(), (oth['活动赠点'] > 2000).mean() * 100))
for s in ['回流', '新增']:
    x = d[d['身份'] == s]
    print(s, '>1000 人数 %d，>2000 人数 %d' % ((x['活动赠点'] > 1000).sum(), (x['活动赠点'] > 2000).sum()))

# 潜在付费代理（从未储值且押注>1万）中的参与率，供 A3 脚注
pp = d[(d['总充值金额'] <= 0) & (d['游戏总押注'] > 1e4)]
print('\n潜在付费代理 %d 人：赠点>0 %.2f%%，>1000 %.2f%%' % (len(pp), (pp['活动赠点'] > 0).mean() * 100, (pp['活动赠点'] > 1000).mean() * 100))
