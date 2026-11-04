"""设计卡 Q160 试算（只代公式，不读 数据/）：第四张卡按「不过 → 过 → 挪量 → 看不出」判，
看不出只在合并 3 期终判时分两格。比较两种分格指标：
  旧：破产礼包购买率 处理组 > 对照组（被新排序机械抬高，用「纯挪量」情景的位移近似）
  新：主指标点估计 > 0 且 两礼包（破产 + 独享）合计人均金额点估计 ≥ 对照
统计量：m = 主指标（破产者人均储值，全部渠道），e = 独享礼包人均金额，s = 两礼包合计人均金额，
p = 破产礼包购买率；护栏 g 独立。两个时点：第 1 期末（99%）、合并 3 期（主 95%、护栏 99%），
合并统计量与第 1 期相关 ρ = 1/√3；各统计量之间的相关按情景取（未知，给范围）。
情景效果以「合并 3 期的 z 值」表示，第 1 期的均值 = 该值 ÷ √3。"""
import numpy as np

rng = np.random.default_rng(160)
N = 1_000_000
rho = 1 / np.sqrt(3)
Z99, Z95 = 2.5758, 1.9600


def run(r_ms, r_es, r_me=0.5, r_mp=0.2, r_ep=-0.3, r_sp=0.3, n_guard=1,
        eff=(0.0, 0.0, 0.0, 0.0)):
    C = np.array([[1, r_me, r_ms, r_mp],
                  [r_me, 1, r_es, r_ep],
                  [r_ms, r_es, 1, r_sp],
                  [r_mp, r_ep, r_sp, 1]], float)
    if np.linalg.eigvalsh(C).min() <= 0:
        return None
    L = np.linalg.cholesky(C)
    d3 = np.array(eff)
    x1 = rng.standard_normal((N, 4)) @ L.T + d3 / np.sqrt(3)
    xn = rng.standard_normal((N, 4)) @ L.T
    x3 = rho * (x1 - d3 / np.sqrt(3)) + np.sqrt(1 - rho ** 2) * xn + d3
    g1 = rng.standard_normal((N, n_guard)); g3 = rho * g1 + np.sqrt(1 - rho ** 2) * rng.standard_normal((N, n_guard))
    m1, e1 = x1[:, 0], x1[:, 1]
    m3, e3, s3, p3 = x3[:, 0], x3[:, 1], x3[:, 2], x3[:, 3]
    bad1 = (m1 < -Z99) | (g1 < -Z99).any(1)
    good1 = ~bad1 & (m1 > Z99)
    nl1 = ~bad1 & ~good1 & (e1 < -Z99) & (m1 <= 0)
    cont = ~bad1 & ~good1 & ~nl1                     # 第 1 期末看不出 → 一律延长（不分格）
    bad3 = cont & ((m3 < -Z95) | (g3 < -Z99).any(1))
    good3 = cont & ~bad3 & (m3 > Z95)
    nl3 = cont & ~bad3 & ~good3 & (e3 < -Z95) & (m3 <= 0)
    unk = cont & ~bad3 & ~good3 & ~nl3
    keep_new = unk & (m3 > 0) & (s3 >= 0)
    keep_old = unk & (p3 > 0)
    return dict(撤=(bad1 | nl1 | bad3 | nl3).mean(), 过=(good1 | good3).mean(), 看不出=unk.mean(),
                新_保留=keep_new.mean(), 新_改内容=(unk & ~((m3 > 0) & (s3 >= 0))).mean(),
                旧_保留=keep_old.mean())


def show(tag, **kw):
    r = run(**kw)
    if r is None:
        print(f'  {tag}: 相关矩阵不正定，跳过'); return
    u = r['看不出']
    print(f"  {tag}: 撤 {r['撤']:.1%} 过 {r['过']:.1%} 看不出 {u:.1%}｜"
          f"新规则 保留 {r['新_保留']:.1%}（占看不出 {r['新_保留']/u:.0%}） 改内容 {r['新_改内容']:.1%}｜"
          f"旧规则 保留 {r['旧_保留']:.1%}（占看不出 {r['旧_保留']/u:.0%}）")


for label, eff in [
    ('A 真实无效果（四项都 0）', (0, 0, 0, 0)),
    ('B 纯挪量（主指标 0、两礼包合计 0；独享 −2、破产礼包购买率 +4，z 值）', (0, -2, 0, 4)),
    ('C 纯挪量且独享降得更多（主 0、合计 0；独享 −3、购买率 +6）', (0, -3, 0, 6)),
    ('D 机制起作用但不够大（主 +1、合计 +1.5、独享 −1、购买率 +4）', (1, -1, 1.5, 4)),
    ('E 挪量有净损失（主 −1、合计 −1.5、独享 −3、购买率 +4）', (-1, -3, -1.5, 4)),
]:
    print(label)
    for r_ms in (0.4, 0.6, 0.8):
        for r_es in (0.3, 0.6):
            for ng in (1, 2):
                show(f'r(主,合计)={r_ms} r(独享,合计)={r_es} 护栏{ng}项', r_ms=r_ms, r_es=r_es, n_guard=ng, eff=eff)
