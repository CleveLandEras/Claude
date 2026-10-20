"""R81 复算：储值恰为 50 元者按最后登录平台（App 类 / 浏览器类）与赠点（15,000 / 16,800）交叉；新增与全体各一张。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
p = _ROOT + '/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
s = d[(d['总充值金额'].round(2) == 50) & (d['充值赠点'].round(0).isin([15000, 16800]))].copy()
plat = s['登入平台'].astype(str).str.lower()
s['platg'] = plat.isin(['web', 'mweb', 'mh5', 'h5']).map({True: '浏览器类', False: '非浏览器'})
for name, g in [('新增', s[s['身份'] == '新增']), ('全体', s)]:
    print(name)
    print(pd.crosstab(g['platg'], g['充值赠点'].round(0)).to_string())
