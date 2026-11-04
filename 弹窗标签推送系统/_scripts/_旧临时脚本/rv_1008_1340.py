import pandas as pd
p = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/近一月活跃_20260916.csv'
d = pd.read_csv(p, encoding='utf-8-sig')
d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
print('分母', len(d))
d['reg'] = pd.to_datetime(d['注册时间'], errors='coerce')
d['last'] = pd.to_datetime(d['最後登入時間'], errors='coerce')
ref = pd.Timestamp('2026-09-16')
d['gap'] = (ref.normalize() - d['last'].dt.normalize()).dt.days
pay = '总充值金额(账号累计)' if '总充值金额(账号累计)' in d.columns else [c for c in d.columns if '总充值' in c][0]
bet = [c for c in d.columns if '总押注' in c][0]
act = [c for c in d.columns if '活动赠点' in c][0]
cz = [c for c in d.columns if '充值赠点' in c][0]
print(pay, bet, act, cz)
print(d['身份'].value_counts().to_dict())
new = d[d['身份'] == '新增']; ret = d[d['身份'] == '回流']
print('新增', len(new), round(len(new)/len(d)*100, 2), '回流', len(ret), round(len(ret)/len(d)*100, 2))
print('金卡以上', (d['卡别'] >= 3).sum(), round((d['卡别'] >= 3).sum()/len(d)*100, 2),
      '储值占比', round(d.loc[d['卡别'] >= 3, pay].sum()/d[pay].sum()*100, 2))
# 新增注册满8天: 注册 8/18–9/8
n8 = new[(new['reg'] >= '2026-08-18') & (new['reg'] < '2026-09-09')]
print('新增注册8/18-9/8', len(n8))
same = n8[n8['last'].dt.normalize() == n8['reg'].dt.normalize()]
print('只来当天', len(same), round(len(same)/len(n8)*100, 2))
z = same[same[bet] == 0]; lo = same[(same[bet] > 0) & (same[bet] <= 1000)]
print('押注0', len(z), '1-1000', len(lo), '合计占', round((len(z)+len(lo))/len(same)*100, 2))
print('押注0且赠点=1000', (z[act] == 1000).sum(), round((z[act] == 1000).sum()/len(z)*100, 2))
# 回流
rp = ret[ret['卡别'] == 1]
print('回流普卡', len(rp), round(len(rp)/len(ret)*100, 2), '>=8天', round((rp['gap'] >= 8).mean()*100, 2), (rp['gap'] >= 8).sum(), '全部回流>=8', (ret['gap'] >= 8).sum())
cp = d[(d['身份'] == '持續') & (d['卡别'] == 1)]
print('持續普卡', len(cp), round((cp['gap'] >= 8).mean()*100, 2))
rz = rp[(rp[pay] == 0) & (rp[bet] == 0)]
print('普卡回流 未储值且押注0', len(rz), round(len(rz)/len(rp)*100, 2), '其中>=8天', (rz['gap'] >= 8).sum())
# 潜在付费
pp = d[(d[pay] == 0) & (d[bet] > 10000)]
print('潜在付费上界', len(pp), round(len(pp)/len(d)*100, 2), '普卡占', round((pp['卡别'] == 1).mean()*100, 2))
print('与新增回流重叠', pp['身份'].isin(['新增', '回流']).sum())
# 近一周从未储值, 剔除VIP/黑名單
dd = d[~d['身份'].isin(['VIP', '黑名單'])]
nv = dd[(dd[pay] == 0) & (dd['gap'] <= 7)]
print('近一周从未储值', len(nv))
nreg = (nv['reg'] > ref - pd.Timedelta(days=30)).sum()
print('新注册<30天', nreg, round(nreg/len(nv)*100, 2))
old = nv[nv['reg'] <= ref - pd.Timedelta(days=365)]
print('一年以上老账号', len(old), '持續', (old['身份'] == '持續').sum(), '回流', (old['身份'] == '回流').sum())
# 破产影响面
h = dd[(dd[pay] > 0) & (dd[cz] >= 15000)]
print('调序影响上界', len(h), '金卡以上', (h['卡别'] >= 3).sum(), round(h.loc[h['卡别'] >= 3, pay].sum()/dd.loc[dd[pay] > 0, pay].sum()*100, 2))
# 潜在流失
for lab, m in [('普', dd['卡别'] == 1), ('银', dd['卡别'] == 2), ('金+', dd['卡别'] >= 3)]:
    s = dd[m & (dd[pay] > 0)]
    print(lab, len(s), (s['gap'] <= 7).sum())
