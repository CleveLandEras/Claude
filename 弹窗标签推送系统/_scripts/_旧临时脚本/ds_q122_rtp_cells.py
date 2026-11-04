# 设计者试算（Q122）：只看列名、缺值、RTP 与押注的关系、切分格子人数；不算流失率，不作结论
import pandas as pd

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/数据/'
a = pd.read_csv(BASE + '近一月活跃_20260916.csv', encoding='utf-8-sig')
l = pd.read_csv(BASE + '八月登录流失名单_20260916.csv', encoding='utf-8-sig')
print('活跃列数', len(a.columns), list(a.columns))
print('流失名单列数', len(l.columns), list(l.columns))

def clean(d):
    d = d[~d['身份'].isin(['機器人', '測試帳號'])].copy()
    return d

a = clean(a)
print('剔除后活跃', len(a))
print('身份分布', a['身份'].value_counts().to_dict())

hc = a[(a['卡别'] >= 3) & (~a['身份'].isin(['VIP', '黑名單']))].copy()
print('高卡（去VIP黑名单）', len(hc))
for c in ['RTP', '游戏总押注', '游戏总输赢', '活动赠点', '充值赠点', '储值回馈比', '活动咬分比']:
    if c in hc.columns:
        s = pd.to_numeric(hc[c], errors='coerce')
        print(c, '缺值', int(s.isna().sum()), '为0', int((s == 0).sum()),
              '分位', [round(x, 2) for x in s.quantile([0, .1, .25, .5, .75, .9, 1]).tolist()])

hc['RTP'] = pd.to_numeric(hc['RTP'], errors='coerce')
hc['押注'] = pd.to_numeric(hc['游戏总押注'], errors='coerce')
print('RTP 与 押注 的秩相关', round(hc['RTP'].rank().corr(hc['押注'].rank()), 3))
hc['rq'] = pd.qcut(hc['RTP'].rank(method='first'), 4, labels=['R1', 'R2', 'R3', 'R4'])
hc['bq'] = pd.qcut(hc['押注'].rank(method='first'), 4, labels=['B1', 'B2', 'B3', 'B4'])
print('RTP四分位 × 押注四分位 人数')
print(pd.crosstab(hc['rq'], hc['bq']))
print('各押注四分位内 RTP 的 P10/P90（看离散度随押注变化）')
for b, g in hc.groupby('bq', observed=True):
    print(b, round(g['押注'].median()), [round(x, 2) for x in g['RTP'].quantile([.1, .5, .9]).tolist()])
print('卡别 × RTP 四分位 人数')
print(pd.crosstab(hc['卡别'], hc['rq']))
