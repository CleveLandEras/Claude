"""R21/R24 复核：注册时长、距末登天数新旧算法对比；持续与回流人均累计储值。不带参数运行。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd, numpy as np, os
B=_ROOT + ''
df=pd.read_csv(os.path.join(B,'数据','近一月活跃_20260916.csv'),encoding='utf-8-sig')
df=df[~df['身份'].isin(['機器人','測試帳號'])].copy(); N=len(df); print('N',N)
df['身份3']=df['身份'].replace({'持續':'持续','黑名單':'持续','VIP':'持续'})
ref=pd.Timestamp('2026-09-16')
reg=pd.to_datetime(df['注册时间'],errors='coerce'); last=pd.to_datetime(df['最後登入時間'],errors='coerce')
old_r=(ref-reg).dt.days; new_r=(ref-reg.dt.normalize()).dt.days
old_l=(ref-last).dt.days; new_l=(ref-last.dt.normalize()).dt.days
print('旧算法 注册天数<0（被当空）',(old_r<0).sum(),'身份',df.loc[old_r<0,'身份3'].value_counts().to_dict())
print('旧算法 距末登<0（被丢弃）',(old_l<0).sum(),'身份',df.loc[old_l<0,'身份3'].value_counts().to_dict())
print('新增注册日期范围',reg[df['身份3']=='新增'].dt.date.min(),reg[df['身份3']=='新增'].dt.date.max())
m=(df['身份3']=='持续')&(new_r<=30)
print('持续 注册≤30天(日期口径)',m.sum(),'注册日期',reg[m].dt.date.value_counts().to_dict())
m2=(df['身份3']=='持续')&(old_r>=0)&(old_r<=30)
print('持续 注册≤30天(旧时间戳口径)',m2.sum(),'最小天数',old_r[m2].min(),'注册日期',reg[m2].dt.date.value_counts().to_dict())
for lab,s in [('旧',old_l),('新',new_l)]:
    b=pd.cut(s,bins=[-1,1,7,14,31],labels=['0–1','2–7','8–14','15–31'])
    t=pd.crosstab(b,df['身份3'],normalize='columns')
    print(lab,'7天内',(t.loc['0–1']+t.loc['2–7']).round(4).to_dict(),'15–31',t.loc['15–31'].round(4).to_dict())
    print(lab,'分母',b.notna().groupby(df['身份3']).sum().to_dict())
print('最后登录日期分布首尾',last.dt.date.min(),last.dt.date.max(),'9/16 当天登录',(last.dt.date==pd.Timestamp('2026-09-16').date()).sum())
# R24：人均累计储值（分母为该组全部人数），持续不含 VIP、黑名单
tot=df['总充值金额']
for name,mask in [('持续不含VIP黑名单',df['身份']=='持續'),('回流',df['身份']=='回流'),('新增',df['身份']=='新增')]:
    s=tot[mask]; p=s[s>0]
    print(name,'人数',mask.sum(),'总额',s.sum(),'人均',round(s.sum()/mask.sum(),1),'有储值者中位数',p.median())
r=df['身份3']=='回流'
print('回流注册>1年(日期口径)',((new_r>365)&r).sum(),'>3年',((new_r>1095)&r).sum(),'分母',r.sum())
