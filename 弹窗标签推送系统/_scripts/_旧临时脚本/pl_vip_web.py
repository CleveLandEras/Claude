"""规划者试算（只读）：A9 web 高储值占比里 VIP 的贡献；VIP 的卡别、平台、最后登录。"""
import pandas as pd

P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
raw = pd.read_csv(P, encoding='utf-8-sig')
d = raw[~raw['身份'].isin(['機器人', '測試帳號'])].copy()
pf = d['登入平台'].astype('string').str.strip().fillna('缺值')
d['平台'] = pf.mask(pf == 'Web', 'web')
BRW = ['mweb', 'web', 'h5', 'mh5']
d['浏览器'] = d['平台'].isin(BRW)
d['储值'] = pd.to_numeric(d['总充值金额'], errors='coerce').fillna(0)
d['VIP'] = d['身份'] == 'VIP'
d['卡组'] = pd.cut(d['卡别'], [0, 1, 2, 7], labels=['普卡', '银卡', '金卡以上']).astype(str)
d['天'] = (pd.Timestamp('2026-09-16') - pd.to_datetime(d['最後登入時間'].astype(str).str[:10])).dt.days
TOT = d['储值'].sum()
print('身份取值', d['身份'].value_counts().to_dict())
v = d[d['VIP']]
print('VIP 人数', len(v), '储值占全部%', round(v['储值'].sum() / TOT * 100, 2))
print('VIP 卡别分布', v['卡别'].value_counts().sort_index().to_dict())
print('VIP 平台分布', v['平台'].value_counts().to_dict())
print('VIP 各平台储值占全部%', (v.groupby('平台')['储值'].sum() / TOT * 100).round(2).to_dict())
print('VIP 0-7天%', round((v['天'] <= 7).mean() * 100, 2))
print('VIP 有储值者中位数', v.loc[v['储值'] > 0, '储值'].median(), '储值>0 人数', int((v['储值'] > 0).sum()))

for name, g in [('全部', d), ('不含 VIP、黑名單', d[~d['身份'].isin(['VIP', '黑名單'])])]:
    t = g['储值'].sum()
    w = g[g['平台'] == 'web']
    b = g[g['浏览器']]
    print(f'\n== {name}：人数 {len(g)}，储值 {int(t)}')
    print(' web 人数', len(w), '占人数%', round(len(w) / len(g) * 100, 2), 'web 储值占本口径%', round(w['储值'].sum() / t * 100, 2))
    print(' 浏览器类 人数', len(b), '占人数%', round(len(b) / len(g) * 100, 2), '储值占本口径%', round(b['储值'].sum() / t * 100, 2))
    print(' web 储值占全部 62,292 储值%', round(w['储值'].sum() / TOT * 100, 2))
    gk = g[g['卡组'] == '金卡以上']
    print(' 金卡以上人数', len(gk), '其中浏览器类储值占金卡以上储值%', round(gk.loc[gk['浏览器'], '储值'].sum() / gk['储值'].sum() * 100, 2),
          'web 占金卡以上人数%', round((gk['平台'] == 'web').mean() * 100, 2))
    print(' 各卡别 web 占比%', g.groupby('卡别').apply(lambda x: round((x['平台'] == 'web').mean() * 100, 2)).to_dict())
    # 储值前 10 名里 VIP
    top = g.nlargest(100, '储值')
    print(' 储值前100名 平台', top['平台'].value_counts().to_dict(), '其中 VIP', int(top['VIP'].sum()))
    print(' 储值前10名 平台', g.nlargest(10, '储值')['平台'].tolist(), 'VIP', g.nlargest(10, '储值')['VIP'].tolist())
