"""现状盘点：用户结构与表现（近一月活跃明细）。不带参数运行。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd, numpy as np, os
B=_ROOT + ''
df=pd.read_csv(os.path.join(B,'数据','近一月活跃_20260916.csv'),encoding='utf-8-sig')
raw=len(df); df=df[~df['身份'].isin(['機器人','測試帳號'])].copy(); N=len(df)
print('原始',raw,'剔除后',N)
idmap={'持續':'持续','回流':'回流','新增':'新增','VIP':'VIP','黑名單':'黑名单'}
df['身份2']=df['身份'].map(idmap)
df['身份3']=df['身份2'].replace({'VIP':'持续','黑名单':'持续'})  # 其余并入
card={1:'普卡',2:'银卡',3:'金卡',4:'白金卡',5:'钻石卡',6:'黑卡',7:'至尊卡'}
df['卡别名']=df['卡别'].map(card)
df['卡组']=np.where(df['卡别']==1,'普卡',np.where(df['卡别']==2,'银卡','金卡以上'))
df['付费']=df['总充值金额']>0
ref=pd.Timestamp('2026-09-16')
df['注册']=pd.to_datetime(df['注册时间'],errors='coerce'); df['末登']=pd.to_datetime(df['最後登入時間'],errors='coerce')
# 用日期相减（先去掉时分秒），避免 9/16 当天注册或登录算成 -1 天被当作空值（R21）
df['注册天数']=(ref-df['注册'].dt.normalize()).dt.days
df['距末登天数']=(ref-df['末登'].dt.normalize()).dt.days
print('注册时间为空',df['注册'].isna().sum(),'其中身份',df.loc[df['注册'].isna(),'身份3'].value_counts().to_dict())
print('注册天数<0',(df['注册天数']<0).sum(),'距末登<0',(df['距末登天数']<0).sum())
print('持续注册≤30天最小天数',df.loc[(df['身份3']=='持续')&(df['注册天数']<=30),'注册天数'].min(),'人数',((df['身份3']=='持续')&(df['注册天数']<=30)).sum())
def pct(a,b): return f'{a/b*100:.2f}%'
print('\n## 身份'); print(df['身份2'].value_counts().to_string())
print('\n## 卡别'); print(df['卡别名'].value_counts().to_string())
print('\n## 身份x卡组 人数'); print(pd.crosstab(df['身份3'],df['卡组'],margins=True).to_string())
print('\n## 储值率 by 身份3'); print(df.groupby('身份3')['付费'].agg(['sum','count','mean']).to_string())
print('\n## 储值率 by 卡组'); print(df.groupby('卡组')['付费'].agg(['sum','count','mean']).to_string())
print('\n## 储值率 身份x卡组'); print(pd.crosstab(df['身份3'],df['卡组'],values=df['付费'],aggfunc='mean').round(4).to_string())
pay=df[df['付费']]
bins=[0,50,200,500,1000,3000,10000,1e12]; lab=['1–50','51–200','201–500','501–1,000','1,001–3,000','3,001–10,000','10,001以上']
pay=pay.assign(档=pd.cut(pay['总充值金额'],bins=bins,labels=lab,right=True))
print('\n## 付费者累计储值档 by 身份3 (列内占比)'); print(pd.crosstab(pay['档'],pay['身份3'],normalize='columns').round(4).to_string())
print(pay.groupby('身份3')['总充值金额'].median().to_string())
print('\n## 注册天数档 x 身份3')
# 30 天内 = 注册日 8/18–9/16（日差 0–29），与身份「新增」的注册日范围一致
tb=[-1,29,90,365,1095,1e6]; tl=['30天内','30–90天','91–365天','1–3年','>3年']
df['注册档']=pd.cut(df['注册天数'],bins=tb,labels=tl)
print(pd.crosstab(df['注册档'],df['身份3'],margins=True).to_string())
print('\n## 距末登天数档 x 身份3（行=档）')
rb=[-1,1,7,14,31]; rl=['0–1天','2–7天','8–14天','15–31天']
df['末登档']=pd.cut(df['距末登天数'],bins=rb,labels=rl)
print(pd.crosstab(df['末登档'],df['身份3'],normalize='columns').round(4).to_string())
print('\n## 押注≥10000 by 身份3'); print(df.assign(b=df['游戏总押注']>=10000).groupby('身份3')['b'].mean().round(4).to_string())
print('押注=0', (df['游戏总押注']==0).sum())
print('\n## 从未储值且押注≥10000（累计口径）', ((~df['付费'])&(df['游戏总押注']>10000)).sum())
print(df[~df['付费']].groupby('身份3').size().to_string())
print(((~df['付费'])&(df['游戏总押注']>10000)).groupby(df['身份3']).sum().to_string())
print('\n## 平台'); print(df['登入平台'].value_counts().to_string())
print('\n## 活动赠点>0 比例 by 身份3'); print(df.assign(a=df['活动赠点']>0).groupby('身份3')['a'].mean().round(4).to_string())
print('\n## RTP 中位 by 身份3'); print(df.groupby('身份3')['RTP'].median().round(4).to_string())
print('\n## 回流身份的注册天数分布'); print(df[df['身份3']=='回流']['注册档'].value_counts().sort_index().to_string())
