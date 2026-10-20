# Q316 / A83：阶段 2 按定稿人群口径重算重叠、未覆盖、离线成员、破产范围构成、画像（口径同 A81）
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd
import numpy as np

P = _ROOT + '/数据/近一月活跃_20260916.csv'
df = pd.read_csv(P, encoding='utf-8-sig')
df = df[~df['身份'].isin(['機器人', '測試帳號'])].copy()
snap = pd.Timestamp('2026-09-16 23:59:59')
df['reg'] = pd.to_datetime(df['注册时间'], errors='coerce')
df['last'] = pd.to_datetime(df['最後登入時間'], errors='coerce')
df['regd'] = (snap.normalize() - df['reg'].dt.normalize()).dt.days
df['lastd'] = (snap.normalize() - df['last'].dt.normalize()).dt.days
bet = df['游戏总押注']
never = df['总充值金额'] <= 0
N = len(df)
last7 = df['lastd'] <= 7
NEW = df['身份'] == '新增'
RET = df['身份'] == '回流'
PP_up = never & (bet >= 20000) & (df['lastd'] <= 14)
PP_lo = never & (bet >= 20000) & (df['regd'] <= 13)
PL_up = last7 & (df['regd'] >= 17)
RET7 = RET & last7


def pct(a, b):
    return f'{a}（{a / b:.2%}）' if b else f'{a}'


print('N', N, 'NEW', NEW.sum(), 'RET', RET.sum(), 'RET7', RET7.sum(), 'PP_up', PP_up.sum(), 'PP_lo', PP_lo.sum(), 'PL_up', PL_up.sum(), 'last7', last7.sum())

print('\n== 一、重叠矩阵 ==')
bases = {
    '宽口径(上界)': dict(NEW=NEW, RET=RET, PP=PP_up, PL=PL_up),
    '窄口径(下界)': dict(NEW=NEW, RET=RET7, PP=PP_lo, PL=pd.Series(False, index=df.index)),
    '近7天登录口径': dict(NEW=NEW & last7, RET=RET & last7, PP=PP_up & last7, PL=PL_up & last7),
}
for name, b in bases.items():
    print('--', name, {k: int(v.sum()) for k, v in b.items()})
    pairs = [('NEW', 'RET'), ('NEW', 'PP'), ('NEW', 'PL'), ('RET', 'PP'), ('RET', 'PL'), ('PP', 'PL')]
    for a, c in pairs:
        n = int((b[a] & b[c]).sum())
        print(f'   {a}∩{c} = {n}  占{a} {n / max(b[a].sum(), 1):.2%}  占{c} {n / max(b[c].sum(), 1):.2%}')
    cnt = sum(v.astype(int) for v in b.values())
    print('   命中恰 2 类', int((cnt == 2).sum()), f'占全体 {(cnt == 2).sum() / N:.2%}', '；命中 3 类', int((cnt == 3).sum()), '；命中>=1类', int((cnt >= 1).sum()))
    if name == '近7天登录口径':
        print('   占近7天登录', f'{(cnt == 2).sum() / last7.sum():.2%}')

print('\n== 二、若每人只归一类 ==')
print('新增优先 -> 潜在付费被占 上界', int((NEW & PP_up).sum()), f'占PP上界 {(NEW & PP_up).sum() / PP_up.sum():.2%}', '；下界', int((NEW & PP_lo).sum()), f'占PP下界 {(NEW & PP_lo).sum() / PP_lo.sum():.2%}')
print('新增优先 -> 潜在流失被占（上界）', int((NEW & PL_up).sum()), f'占PL候选池 {(NEW & PL_up).sum() / PL_up.sum():.2%}')
print('回流优先 -> 潜在付费被占（上界）', int((RET & PP_up).sum()), f'占PP上界 {(RET & PP_up).sum() / PP_up.sum():.2%}', '；回流优先 -> 潜在流失被占', int((RET & PL_up).sum()), f'占PL候选池 {(RET & PL_up).sum() / PL_up.sum():.2%}')
print('潜在付费优先 -> 回流被占', int((PP_up & RET).sum()), f'占回流存量 {(PP_up & RET).sum() / RET.sum():.2%}', '；-> 新增被占', int((PP_up & NEW).sum()), f'占新增 {(PP_up & NEW).sum() / NEW.sum():.2%}')
print('新增或回流优先 -> 潜在流失被占', int(((NEW | RET) & PL_up).sum()), f'占PL候选池 {((NEW | RET) & PL_up).sum() / PL_up.sum():.2%}')

print('\n== 三、未覆盖 ==')
for name, u in [('宽口径', NEW | RET | PP_up | PL_up), ('窄口径', NEW | RET7 | PP_lo)]:
    un = ~u
    print(name, '并集', int(u.sum()), '；五类以外', int(un.sum()), f'占{N} {un.mean():.2%}', '；其中近7天登录', int((un & last7).sum()), f'占近7天登录 {(un & last7).sum() / last7.sum():.2%}', '；其中有储值', int((un & ~never).sum()), '；其中近7天登录且有储值', int((un & last7 & ~never).sum()))
    print('   五类以外 累计储值占比', f'{df.loc[un, "总充值金额"].clip(lower=0).sum() / df["总充值金额"].clip(lower=0).sum():.2%}')
    print('   五类以外 身份', df.loc[un, '身份'].value_counts().to_dict())
wide = NEW | RET | PP_up | PL_up
nar = NEW | RET7 | PP_lo
diff = wide & ~nar
print('宽窄差额', int(diff.sum()), '；其中近7天登录', int((diff & last7).sum()))
print('  差额被潜在付费上界覆盖', int((diff & PP_up).sum()), '；被潜在流失候选池覆盖', int((diff & PL_up).sum()), '；被回流覆盖', int((diff & RET).sum()))
print('  近7天登录差额：潜在流失', int((diff & last7 & PL_up).sum()), '；潜在付费', int((diff & last7 & PP_up).sum()), '；回流', int((diff & last7 & RET).sum()))
g = last7 & (df['身份'] == '持續')
print('分组：近7天登录 持續 无储值 押注<20000', int((g & never & (bet < 20000)).sum()), ' 其中不在窄口径五类内', int((g & never & (bet < 20000) & ~nar).sum()), '；在宽口径五类外', int((g & never & (bet < 20000) & ~wide).sum()))
print('分组：近7天登录 持續 有储值', int((g & ~never).sum()), ' 窄口径未覆盖', int((g & ~never & ~nar).sum()), '；宽口径未覆盖', int((g & ~never & ~wide).sum()))
print('分组：近7天登录 持續 有储值 窄口径未覆盖 占累计储值', f'{df.loc[g & ~never & ~nar, "总充值金额"].clip(lower=0).sum() / df["总充值金额"].clip(lower=0).sum():.2%}')
print('VIP/黑名單', int(df['身份'].isin(['VIP', '黑名單']).sum()))
print('宽口径未覆盖的近7天登录：身份', df.loc[~wide & last7, '身份'].value_counts().to_dict(), '；regd 分布 <17:', int((~wide & last7 & (df['regd'] < 17)).sum()), '；regd缺失', int((~wide & last7 & df['regd'].isna()).sum()))

print('\n== 四、离线（最后登录>=8天）中的五类成员 ==')
off = df['lastd'] >= 8
print('离线', int(off.sum()), '；新增', int((off & NEW).sum()), '；回流', int((off & RET).sum()), '；潜在付费上界(8-14天)', int((off & PP_up).sum()), '；潜在流失(定义要求近7天有登录)', int((off & PL_up).sum()))

print('\n== 五、破产可能触发范围（近7天登录且累计押注>0）构成 ==')
bk = last7 & (bet > 0)
print('范围', int(bk.sum()), '；潜在付费上界', f'{(bk & PP_up).sum() / bk.sum():.2%}', '；潜在流失候选池', f'{(bk & PL_up).sum() / bk.sum():.2%}', '；回流', f'{(bk & RET).sum() / bk.sum():.2%}', '；新增', f'{(bk & NEW).sum() / bk.sum():.2%}')

print('\n== 六、潜在付费上界画像 ==')
U = PP_up
for card in [1, 2, 3]:
    a = (df['卡别'] == card) & U
    b = (df['卡别'] == card) & ~U
    print(f'卡别{card}: U {int(a.sum())} 其余 {int(b.sum())}；注册天数中位 {df.loc[a, "regd"].median():.0f}/{df.loc[b, "regd"].median():.0f}；活动赠点中位 {df.loc[a, "活动赠点"].median():.0f}/{df.loc[b, "活动赠点"].median():.0f}；近7天登录率 {(df.loc[a, "lastd"] <= 7).mean():.2%}/{(df.loc[b, "lastd"] <= 7).mean():.2%}；回流占比 {RET[a].mean():.2%}/{RET[b].mean():.2%}；新增占比 {NEW[a].mean():.2%}/{NEW[b].mean():.2%}')
print('整体 注册天数中位比', f'{df.loc[U, "regd"].median() / df.loc[~U, "regd"].median():.2f}', '；活动赠点中位比', f'{df.loc[U, "活动赠点"].median() / df.loc[~U, "活动赠点"].median():.2f}')
print('上界 占累计储值', f'{df.loc[U, "总充值金额"].clip(lower=0).sum() / df["总充值金额"].clip(lower=0).sum():.2%}', '（按定义应为 0 或接近 0）')
old = U & (df['身份'] == '持續') & (df['regd'] >= 365) & last7
print('上界中 持續、注册>=365天、近7天登录', int(old.sum()))
print('上界 普卡占比', f'{(df.loc[U, "卡别"] == 1).mean():.2%}')
print('\n注册时间缺失者在 last7 的数', int((last7 & df['regd'].isna()).sum()))
