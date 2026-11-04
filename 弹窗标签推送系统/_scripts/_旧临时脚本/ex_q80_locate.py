"""Q80：定位汇报、环节2、A14、设计卡里要改的句子行号。只读。"""
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
FILES = ['决策汇报.html', '环节2_问题诊断.html', '分析/A14_问题清单与影响规模.md', '过程记录/设计卡.md']
TERMS = ['不能说它比', '也有依据', '都取决于尺子', '比老用户低', '同一批人）', '13% / 22%', '13–22%', '12.9%', '最大的机会', '更正记录', '<h2', 'O4', '回来那几天']
for f in FILES:
    lines = open(B + f, encoding='utf-8').read().split('\n')
    print('=====', f, len(lines), '行')
    for i, l in enumerate(lines, 1):
        for t in TERMS:
            if t in l:
                print(f'  L{i} [{t}] {l.strip()[:160]}')
                break
