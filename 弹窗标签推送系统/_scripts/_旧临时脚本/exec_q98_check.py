"""执行者用（Q98 完成标准）：检索「多留住几十人以内」「9–28 人」在汇报、环节3 更正记录之前的出现；以及流失一面句子里是否带「真实只会更难」「真实可能更难」。只读，不带参数。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for fn in ['决策汇报.html', '环节3_方案.html']:
    L = open(os.path.join(BASE, fn), encoding='utf-8').read().split('\n')
    corr = next((i for i, l in enumerate(L) if '更正记录' in l and '<summary>' in l), len(L))
    rules = next((i for i, l in enumerate(L) if '口径约束（1–' in l), len(L))
    stop = min(corr, rules)
    for t in ['几十人以内', '9–28 人', '9 / 28']:
        print(fn, t, [i + 1 for i, l in enumerate(L[:stop]) if t in l])
    for i, l in enumerate(L[:stop]):
        if ('流失' in l or '85 人' in l or '回来率' in l) and ('真实只会更难' in l or '真实可能更难' in l):
            print(fn, '可能混写的行', i + 1, l.strip()[:200])
