# A45 共用脚本：把五类人群的口径一次写死，Q209/Q210/Q211 都从这里取数
# 用法：python3 an_a45_members.py 直接打印口径与人数；其他脚本 import load() 取带布尔列的 DataFrame
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pandas as pd

BASE = _ROOT + '/数据/'
REF = pd.Timestamp('2026-09-16')  # 9/16 记第 0 天


def _read(name):
    df = pd.read_csv(BASE + name, encoding='utf-8-sig')
    cols = list(df.columns)
    m = {
        'id': cols[0], 'reg': cols[1], 'plat': cols[2], 'last': cols[3],
        'card': [c for c in cols if '卡' in c][0],
        'idn': [c for c in cols if '身份' in c][0],
        'pay': [c for c in cols if '总充值' in c or '總充值' in c][0],
        'bet': [c for c in cols if '总押注' in c or '總押注' in c][0],
        'win': [c for c in cols if '输赢' in c or '輸贏' in c][0],
        'rtp': [c for c in cols if 'RTP' in c][0],
        'act': [c for c in cols if '活动赠点' in c or '活動贈點' in c][0],
        'dep': [c for c in cols if '充值赠点' in c or '充值贈點' in c][0],
    }
    df = df[~df[m['idn']].isin(['機器人', '測試帳號'])].copy()
    df['rd'] = pd.to_datetime(df[m['reg']], errors='coerce').dt.normalize()
    df['ld'] = pd.to_datetime(df[m['last']], errors='coerce').dt.normalize()
    df['dsl'] = (REF - df['ld']).dt.days   # 最后登录距 9/16 天数
    df['age'] = (REF - df['rd']).dt.days   # 注册距 9/16 天数
    return df, m


def load():
    df, m = _read('近一月活跃_20260916.csv')
    pay, bet, idn, card = m['pay'], m['bet'], m['idn'], m['card']
    df['present'] = df['dsl'] <= 7                      # 在场：0–7 天
    df['is_new'] = df[idn] == '新增'
    df['is_back'] = df[idn] == '回流'
    df['back_present'] = df['is_back'] & df['present']
    df['never_paid'] = df[pay] <= 0                     # 含 11 个负值账号
    df['has_paid'] = df[pay] > 0
    df['pp_wide'] = df['never_paid'] & (df[bet] > 10000)   # 潜在付费上界（读法甲）
    df['pp_verified'] = df['pp_wide'] & (df['age'] <= 120)  # 注册不满 4 个月，累计押注=近 4 个月押注
    df['pp_only_upper'] = df['pp_wide'] & (df['age'] > 120)
    df['churn_ub'] = df['has_paid']                     # 潜在流失上界：有储值
    df['churn_alt_a'] = df['has_paid'] & df['present']  # 替代甲：有储值且在场
    df['churn_alt_b'] = df['has_paid'] & (df['dsl'] >= 8)  # 替代乙：有储值且 ≥8 天没来
    df['bk_ub_present'] = df['present']                 # 破产暴露范围上界：在场全体
    df['bk_ub_bet'] = df['present'] & (df[bet] > 0)
    return df, m


def main():
    df, m = load()
    pay, bet, idn, card = m['pay'], m['bet'], m['idn'], m['card']
    N = len(df)
    P = lambda k: f'{k:,}（{k / N * 100:.2f}%）'
    print('分母 N =', N)
    print('身份分布', df[idn].value_counts().to_dict())
    print('注册时间缺失', df['rd'].isna().sum(), '最后登录缺失', df['ld'].isna().sum())
    print('累计储值总额', int(df[pay].sum()), '负值账号', (df[pay] < 0).sum(), '储值=0', (df[pay] == 0).sum())

    print('\n=== ① 新增 ===')
    new = df[df['is_new']]
    print('新增', P(len(new)), '注册天数 min/max', new['age'].min(), new['age'].max())
    print('全体 age≤29', P((df['age'] <= 29).sum()), '其中非新增', ((df['age'] <= 29) & ~df['is_new']).sum())
    print('新增中 age≥30', (new['age'] >= 30).sum())
    print('age≤30 非新增（含第 30 天）', ((df['age'] <= 30) & ~df['is_new']).sum(), '身份', df[(df['age'] == 30) & ~df['is_new']][idn].value_counts().to_dict())
    print('新增 在场', new['present'].sum(), '新增 储值>0', (new[pay] > 0).sum(), '新增 押注>0', (new[bet] > 0).sum())

    print('\n=== ② 回流 ===')
    back = df[df['is_back']]
    print('回流存量', P(len(back)), '注册 age<30', (back['age'] < 30).sum(), 'age 中位', back['age'].median(), 'min', back['age'].min())
    bins = [(0, 0), (1, 7), (8, 14), (15, 31)]
    for a, b in bins:
        k = ((back['dsl'] >= a) & (back['dsl'] <= b)).sum()
        print(f'  最后登录 {a}-{b} 天', k, f'{k / len(back) * 100:.2f}%')
    print('  最后登录 >31 天', (back['dsl'] > 31).sum())
    print('回流在场（0–7 天）', P(back['present'].sum()), '≥8 天', (back['dsl'] >= 8).sum(), f"{(back['dsl'] >= 8).mean() * 100:.2f}%")
    print('回流 当天登录(dsl=0)', (back['dsl'] == 0).sum())
    print('回流 储值>0', (back[pay] > 0).sum(), '押注=0', (back[bet] == 0).sum())

    # 八月流失名单
    dfa, ma = _read('八月登录流失名单_20260916.csv')
    ida = set(dfa[ma['id']])
    only = dfa[~dfa[ma['id']].isin(set(df[m['id']]))]
    both = dfa[dfa[ma['id']].isin(set(df[m['id']]))]
    print('八月名单（剔除后）', len(dfa), '两边都有', len(both), '独有', len(only))
    print('  名单身份', dfa[ma['idn']].value_counts().to_dict())
    print('  独有身份', only[ma['idn']].value_counts().to_dict())
    print('  名单中身份=回流', (dfa[ma['idn']] == '回流').sum(), '其中独有', (only[ma['idn']] == '回流').sum())
    print('  独有 最后登录距 9/16 天数 min/max', only['dsl'].min(), only['dsl'].max())

    print('\n=== ③ 潜在付费 ===')
    print('从未储值（≤0）', P(df['never_paid'].sum()), '其中近一周在场', (df['never_paid'] & df['present']).sum())
    print('潜在付费宽（≤0 且押注>10,000）', P(df['pp_wide'].sum()), '在场', (df['pp_wide'] & df['present']).sum())
    print('  可核实（age≤120）', df['pp_verified'].sum(), '仅上界（age>120）', df['pp_only_upper'].sum())
    print('  负值账号在内', (df['pp_wide'] & (df[pay] < 0)).sum())
    print('  身份分布', df[df['pp_wide']][idn].value_counts().to_dict())
    print('  卡别', df[df['pp_wide']][card].value_counts().sort_index().to_dict())
    for t in [1000, 5000, 10000, 50000, 100000]:
        s = df['never_paid'] & (df[bet] > t)
        print(f'  阈值 {t:>7,}: 全部 {s.sum():,}  在场 {(s & df["present"]).sum():,}')
    big = df['pp_wide'] & (df[bet] > 1_000_000)
    print('  押注>100 万者', big.sum(), '剔除后', df['pp_wide'].sum() - big.sum())
    # 读法乙参照：有储值（>0）但没买首储——以充值赠点 < 15,000 代理（A19 口径）
    paid_nofirst = df['has_paid'] & (df[m['dep']] < 15000)
    print('  读法乙参照：有储值且充值赠点<15,000', paid_nofirst.sum(), '（A19 引用 3,677 为能确定的子集，口径见 A19）')

    print('\n=== ④ 潜在流失 ===')
    print('有储值（>0）', P(df['churn_ub'].sum()), '其中在场', df['churn_alt_a'].sum(), '≥8天', df['churn_alt_b'].sum())
    ex = ~df[idn].isin(['VIP', 'VIP玩家', '黑名單'])
    for nm, mask in [('普卡', df[card] == 1), ('银卡', df[card] == 2), ('金卡以上', df[card] >= 3)]:
        a = (df['churn_alt_a'] & mask).sum()
        b = (df['churn_alt_a'] & mask & ex).sum()
        print(f'  {nm} 有储值且在场 含VIP黑名單 {a:,}  剔除后 {b:,}')
    print('  VIP/黑名單 人数', df[idn].isin(['VIP', 'VIP玩家', '黑名單']).sum(), df[idn].value_counts().to_dict())

    print('\n=== ⑤ 破产（暴露范围）===')
    print('在场全体', P(df['bk_ub_present'].sum()), '在场且累计押注>0', df['bk_ub_bet'].sum())
    print('在场且 当天登录', (df['dsl'] == 0).sum())
    print('活动赠点分布(在场) 众数', df[df['present']][m['act']].value_counts().head(3).to_dict())

    print('\n=== 身份分布全表 ===')
    print(df[idn].value_counts())


if __name__ == '__main__':
    main()
