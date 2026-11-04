"""审查 20:44：D4b 参照组口径差异排查。只读。"""
import pandas as pd

B = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
T0 = pd.Timestamp('2026-09-16')
a = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
a = a[~a['身份'].isin(['機器人', '測試帳號'])].copy()
a['regd'] = pd.to_datetime(a['注册时间'], errors='coerce').dt.normalize()
a['age'] = (T0 - a['regd']).dt.days
a['money'] = pd.to_numeric(a['总充值金额'], errors='coerce').fillna(0)
p = a[a.money > 0]
for nm, mk in [('age<=30', p.age <= 30), ('age<30', p.age < 30), ('reg>=8/18', p.regd >= pd.Timestamp('2026-08-18')),
               ('身份新增', p['身份'] == '新增'), ('身份新增&age<=30', (p['身份'] == '新增') & (p.age <= 30)),
               ('age<=30 非VIP黑名单', (p.age <= 30) & (~p['身份'].isin(['VIP', '黑名單'])))]:
    x = p[mk]
    print(nm, len(x), '均值 %.1f 中位 %.0f' % (x.money.mean(), x.money.median()))
print('身份新增 全体', int((a['身份'] == '新增').sum()), '新增中 age 范围', a.loc[a['身份'] == '新增', 'age'].min(), a.loc[a['身份'] == '新增', 'age'].max())
