"""设计卡 Q155 试算（只代公式，不读数据）：真实效果为 0 时，按候选判读规则，
一张卡被误判「不过」（误撤）与误判「过」的概率。
两个判读时点：第 1 期末、合并 3 期末；合并统计量与第 1 期统计量相关 ρ = 1/√3。
各检验之间按独立近似（正相关时误撤会更低，是上界式估算）。"""
import numpy as np

rng = np.random.default_rng(155)
N = 2_000_000
rho = 1 / np.sqrt(3)
Z99, Z95 = 2.5758, 1.9600


def draw(k):
    a = rng.standard_normal((N, k))
    b = rng.standard_normal((N, k))
    return a, rho * a + np.sqrt(1 - rho ** 2) * b   # Z1, Z3（正 = 好方向）


def card(n_main, n_guard, guard_z1, guard_z3, nuoliang=False):
    """n_main 个主指标（过：任一？——按卡：所有主指标都需不为负；这里取「任一主指标显著为正且无显著为负」为过），
    n_guard 个统计型护栏。返回 (误撤, 误过)。"""
    m1, m3 = draw(n_main)
    g1, g3 = draw(n_guard) if n_guard else (np.zeros((N, 0)), np.zeros((N, 0)))
    # 第 1 期末
    bad1 = (m1 < -Z99).any(1) | (g1 < -guard_z1).any(1)
    good1 = (m1 > Z99).any(1) & ~bad1
    if nuoliang:  # 挪量：独享礼包差显著为负（同主指标时点与区间）且主指标点估计 ≤ 0；独享与主指标相关取 0.5
        x1a = rng.standard_normal(N); x3b = rng.standard_normal(N)
        r = 0.5
        e1 = r * m1[:, 0] + np.sqrt(1 - r ** 2) * x1a
        e3 = rho * e1 + np.sqrt(1 - rho ** 2) * (r * (m3[:, 0] - rho * m1[:, 0]) / np.sqrt(1 - rho ** 2) + np.sqrt(1 - r ** 2) * x3b)
        nl1 = (e1 < -Z99) & (m1[:, 0] <= 0) & ~bad1 & ~good1
    else:
        nl1 = np.zeros(N, bool)
    cont = ~bad1 & ~good1 & ~nl1
    bad3 = cont & ((m3 < -Z95).any(1) | (g3 < -guard_z3).any(1))
    good3 = cont & ~bad3 & (m3 > Z95).any(1)
    nl3 = np.zeros(N, bool)
    if nuoliang:
        nl3 = cont & ~bad3 & ~good3 & (e3 < -Z95) & (m3[:, 0] <= 0)
    revert = bad1 | nl1 | bad3 | nl3
    return revert.mean(), (good1 | good3).mean()


print('候选规则 A（选定）：护栏只在两个时点判，两个时点都用 99% 区间；主指标 99% → 95%')
cases = [
    ('第一张卡（有埋点：M2、M3 主；M8、储值护栏）', 2, 2, False),
    ('第一张卡（无埋点：M2、M3 主；储值护栏）', 2, 1, False),
    ('第二张卡（有埋点：主；M8、M9、普银 A/A）', 1, 3, False),
    ('第二张卡（无埋点：主；M9、普银 A/A）', 1, 2, False),
    ('第四张卡（有埋点：主；M8、M9；含挪量）', 1, 2, True),
    ('第四张卡（无埋点：主；M9；含挪量）', 1, 1, True),
    ('提案乙（有埋点：主；M8、M9）', 1, 2, False),
    ('提案乙（无埋点：主；M9）', 1, 1, False),
]
for name, nm, ng, nl in cases:
    rv, gd = card(nm, ng, Z99, Z99, nl)
    print(f'  {name}: 误撤 {rv:.1%}  误过 {gd:.1%}')

print('\n对照：候选规则 B（护栏两个时点同主指标 99% → 95%）')
for name, nm, ng, nl in cases:
    rv, gd = card(nm, ng, Z99, Z95, nl)
    print(f'  {name}: 误撤 {rv:.1%}  误过 {gd:.1%}')

print('\n单项：')
a1, a3 = draw(1)
print('  护栏单项（99%/99%）', ((a1 < -Z99) | (a3 < -Z99)).mean().round(4))
print('  主指标单侧（99%/95%）', ((a1 < -Z99) | (a3 < -Z95)).mean().round(4))
