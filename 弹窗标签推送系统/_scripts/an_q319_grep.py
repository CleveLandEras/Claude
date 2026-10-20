# Q319：V2 独立审查采纳项里的事实出处核查（只读）
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _textify import textify, BASE
srcs = ['来源资料/claude_弹窗标签推送_盘点.html', '来源资料/Cowork汇总_背景信息_v2_20260928.md', '过程记录/任务清单.md', '_scripts/an_呈交版V2_生成.py']
keys = ['Android', '安卓', 'android', '到达率', '总控', '排期前', '核实']
for rel in srcs:
    p = os.path.join(BASE, rel)
    if not os.path.exists(p):
        print('缺', rel); continue
    t = textify(p).splitlines() if rel.endswith('.html') else open(p, encoding='utf-8').read().splitlines()
    print('==', rel)
    for i, l in enumerate(t, 1):
        if any(k in l for k in ['Android', '安卓', 'android']):
            print(f'  [{i}] {l[:220]}')
    n_check = [i for i, l in enumerate(t, 1) if ('总控' in l)]
    print('  总控 行', n_check[:8])
    if rel.endswith('.py'):
        for i, l in enumerate(t, 1):
            if '排期前' in l or '检验' in l or '触达' in l and '离线' in l:
                print(f'  [{i}] {l[:200]}')
