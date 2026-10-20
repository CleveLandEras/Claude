"""Q15：标签线诊断的本地检验部分（S3 新增口径、S5 机器人与测试账号、潜在流失上限）。照设计卡 Q15。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

B = _ROOT + '/数据/'
T0 = pd.Timestamp('2026-09-16')
EX = ['機器人', '測試帳號']

raw = pd.read_csv(B + '近一月活跃_20260916.csv', encoding='utf-8-sig')
raw['last'] = pd.to_datetime(raw['最後登入時間']).dt.normalize()
raw['reg'] = pd.to_datetime(raw['注册时间'], errors='coerce').dt.normalize()
raw['days'] = (T0 - raw['last']).dt.days
raw['tenure'] = (T0 - raw['reg']).dt.days
raw['dep'] = pd.to_numeric(raw['总充值金额'], errors='coerce').fillna(0)
raw['bet'] = pd.to_numeric(raw['游戏总押注'], errors='coerce').fillna(0)
print('原始行数', len(raw), '身份', raw['身份'].value_counts().to_dict())
a = raw[~raw['身份'].isin(EX)].copy()
print('剔除后', len(a))

print('\n===== S3 新增口径：身份「新增」 vs 注册距 9/16 ≤ 30 天')
nw = a['身份'] == '新增'
for lim in (29, 30):
    r = a['tenure'] <= lim
    print(f'  注册 ≤ {lim} 天：{int(r.sum()):,}；身份新增 {int(nw.sum()):,}；交集 {int((nw & r).sum()):,}；新增不在内 {int((nw & ~r).sum()):,}；在内非新增 {int((~nw & r).sum()):,}')
    d = a[~nw & r]
    if len(d):
        print('    在内非新增的注册天数分布', d['tenure'].value_counts().sort_index().to_dict(), '身份', d['身份'].value_counts().to_dict())
print('  新增的注册天数范围', a.loc[nw, 'tenure'].min(), a.loc[nw, 'tenure'].max(), '；注册时间缺值（全体）', int(a['reg'].isna().sum()))

print('\n===== 潜在流失标签口径风险的上限（有储值者）')
pay = a[a['dep'] > 0]
print('  有储值', len(pay), '；普卡+银卡', int(pay['卡别'].isin([1, 2]).sum()), '；金卡以上', int((pay['卡别'] >= 3).sum()))
print('  有储值且 0–7 天登录（月初会被圈入且会看到弹窗的上限）', int((pay['days'] <= 7).sum()))

print('\n===== S5 机器人与测试账号（原始 63,032 行）')
w7 = raw['days'] <= 7
print('  0–7 天登录的全部行（含机器人）', int(w7.sum()))
for idn in EX:
    g = raw[raw['身份'] == idn]
    print(f'  {idn}: {len(g)} 行｜0–7 天登录 {int((g["days"] <= 7).sum())}｜登入平台缺值 {int(g["登入平台"].isna().sum())}｜储值>0 {int((g["dep"] > 0).sum())}（合计 {g["dep"].sum():,.0f}）｜押注>0 {int((g["bet"] > 0).sum())}｜注册≤29天 {int((g["tenure"] <= 29).sum())}｜注册缺值 {int(g["reg"].isna().sum())}')
    print(f'    卡别', g['卡别'].value_counts().sort_index().to_dict(), '平台', g['登入平台'].fillna('缺值').value_counts().head(5).to_dict())
bt = raw['身份'].isin(EX)
print(f'  机器人+测试 0–7 天 {int((bt & w7).sum())} / 0–7 天全部 {int(w7.sum())} = {(bt & w7).sum() / w7.sum() * 100:.2f}%')
print(f'  机器人+测试 全部 {int(bt.sum())} / 63,032 = {bt.sum() / len(raw) * 100:.2f}%')
