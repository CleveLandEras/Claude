"""R122–R124：定位决策汇报、环节2 中待改句子的行号（只读）。"""
import os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
targets = {
    '决策汇报.html': ['id="s3"', 'id="s4"', 'id="s5"', 'id="fix"', '更正记录', '<h2>', '都是按上面的诊断', '怎么回复', '统一后台（07）要开发', '可提交', '已可交研发'],
    '环节2_问题诊断.html': ['class="meta"', '各节一句话', '核对表', '更正记录', '<h2', 'id="'],
}
for f, keys in targets.items():
    p = os.path.join(BASE, f)
    lines = open(p, encoding='utf-8').read().split('\n')
    print('=' * 50, f, len(lines), '行')
    for i, l in enumerate(lines, 1):
        for k in keys:
            if k in l:
                print(f'{i}\t[{k}]\t{l[:160]}')
                break
