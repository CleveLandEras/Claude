# 审查只读脚本：① 打印决策汇报第 12 件判读线表附近行；② 蒙特卡洛复算 Q155 误判率（独立近似）
import re
import numpy as np

p = '/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html'
lines = open(p, encoding='utf-8').read().split('\n')
for i, l in enumerate(lines):
    if '护栏变差的容差' in l:
        for j in range(max(0, i - 8), min(len(lines), i + 10)):
            t = re.sub(r'<[^>]+>', ' | ', lines[j])
            t = re.sub(r'(\s*\|\s*)+', ' | ', t).strip()
            print(j + 1, t[:400])
        print('-----')
        break

import sys
sys.exit(0)
rng = np.random.default_rng(1)
N = 2_000_000
r = np.sqrt(1 / 3)  # 第 1 期统计量与合并 3 期统计量的相关
z99, z95 = 2.5758, 1.96


def two_look(n):
    a = rng.standard_normal((N, n))
    b = r * a + np.sqrt(1 - r * r) * rng.standard_normal((N, n))
    return a, b


def card(n_prim, n_guard, shift=False):
    pa, pb = two_look(n_prim)
    ga, gb = two_look(n_guard)
    # look 1
    fail1 = (pa < -z99).any(1) | (ga < -z99).any(1)
    pass1 = ~fail1 & (pa > z99).any(1)
    if shift:  # 挪量：独享显著降（与主指标相关 0.5）且主指标点估计 <= 0（仅单主指标）
        rho = 0.5
        sa, sb = two_look(1)
        sa = rho * pa + np.sqrt(1 - rho ** 2) * sa
        sb = rho * pb + np.sqrt(1 - rho ** 2) * sb
        sh1 = ~fail1 & ~pass1 & (sa[:, 0] < -z99) & (pa[:, 0] <= 0)
    else:
        sh1 = np.zeros(N, bool)
    done1 = fail1 | pass1 | sh1
    fail2 = ~done1 & ((pb < -z95).any(1) | (gb < -z99).any(1))
    pass2 = ~done1 & ~fail2 & (pb > z95).any(1)
    if shift:
        sh2 = ~done1 & ~fail2 & ~pass2 & (sb[:, 0] < -z95) & (pb[:, 0] <= 0)
    else:
        sh2 = np.zeros(N, bool)
    withdraw = (fail1 | fail2 | sh1 | sh2).mean()
    passed = (pass1 | pass2).mean()
    return withdraw, passed


for name, args in [('第一张卡 无M8', (2, 1)), ('第一张卡 有M8', (2, 2)),
                   ('第二张卡 无M8', (1, 2)), ('第二张卡 有M8', (1, 3)),
                   ('第四张卡 无M8', (1, 1, True)), ('第四张卡 有M8', (1, 2, True)),
                   ('提案乙 无M8', (1, 1)), ('提案乙 有M8', (1, 2))]:
    w, pz = card(*args)
    print(f'{name}: 误撤 {w:.2%}  误判过 {pz:.2%}')
