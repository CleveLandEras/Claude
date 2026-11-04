import pandas as pd
p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])]
print('N', len(d))
print(d[['会员等级', '总充值金额', '游戏总押注', '活动赠点', '充值赠点', '储值回馈比', '活动咬分比']].describe().T)
print('\n会员等级 x 卡别')
print(pd.crosstab(d['会员等级'], d['卡别']).iloc[:40])
print('\n会员等级 相关', d[['会员等级', '卡别', '总充值金额', '游戏总押注']].corr(method='spearman'))
pay = d[d['总充值金额'] > 0].copy()
print('\npayers', len(pay))
pay['ratio_calc'] = pay['充值赠点'] / pay['总充值金额']
print(pay[['储值回馈比', 'ratio_calc']].head(10))
print('corr', pay[['储值回馈比', 'ratio_calc']].corr())
pay['grp'] = pd.cut(pay['卡别'], [0, 1, 2, 7], labels=['普卡', '银卡', '金卡以上'])
g = pay.groupby('grp', observed=True)
print(g.apply(lambda x: pd.Series({
    'n': len(x),
    '充值赠点>0占比': (x['充值赠点'] > 0).mean(),
    '回馈比中位': x['储值回馈比'].median(),
    '充值赠点合计/充值合计': x['充值赠点'].sum() / x['总充值金额'].sum(),
    '活动赠点合计/充值合计': x['活动赠点'].sum() / x['总充值金额'].sum(),
})))
print(g.apply(lambda x: x['储值回馈比'].quantile([.1, .25, .5, .75, .9])).T)
