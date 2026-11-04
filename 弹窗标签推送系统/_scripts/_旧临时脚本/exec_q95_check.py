"""执行者用（Q95 完成标准）：统计决策汇报、环节3 中若干措辞的出现次数，并标出是否位于更正记录表内。只读，不带参数。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERMS = ['才有依据估', '22–26%', '能圈到', '为了钱」的理由不成立', '末位奇偶', '就测得出', '需要几周']
for fn in ['决策汇报.html', '环节3_方案.html']:
    L = open(os.path.join(BASE, fn), encoding='utf-8').read().split('\n')
    corr_start = next((i for i, l in enumerate(L) if '更正记录' in l and '<summary>' in l), len(L))
    for t in TERMS:
        hits = [i + 1 for i, l in enumerate(L) if t in l]
        body = [h for h in hits if h - 1 < corr_start]
        print(f'{fn}｜{t}：全部 {len(hits)} 处 {hits}；更正记录之前 {len(body)} 处 {body}')
