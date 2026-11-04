# 只读复算：A33 S1 引用人数（卡别分布、身份、从未储值）
import pandas as pd
P = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(P, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])]
print('分母', len(d))
card = d['卡别'].astype(int)
print('普卡+银卡', int((card <= 2).sum()), '金卡以上', int((card >= 3).sum()))
print('身份', d['身份'].value_counts().to_dict())
pay = pd.to_numeric(d['总充值金额（账号累计）'] if '总充值金额（账号累计）' in d.columns else d.iloc[:, 6], errors='coerce').fillna(0)
print('从未储值(<=0)', int((pay <= 0).sum()), '==0', int((pay == 0).sum()))
hi = card >= 3
print('金卡以上有储值', int((hi & (pay > 0)).sum()),
      '剔除VIP黑名单', int((hi & (pay > 0) & ~d['身份'].isin(['VIP', '黑名單'])).sum()))
print('列', list(d.columns))
