import os, re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for name, n in [('进展日志.md', 12), ('过程记录/审查记录.md', 0), ('过程记录/监督记录.md', 0)]:
    p = base + name
    if not os.path.exists(p):
        print('== missing', name); continue
    lines = open(p, encoding='utf-8').read().splitlines()
    print('==', name, 'lines', len(lines))
    if n:
        for l in lines[-n:]:
            print(l[:600])
    else:
        heads = [(i, l) for i, l in enumerate(lines) if l.startswith('## ')]
        for i, l in heads[-4:]:
            print(i + 1, l[:200])
        if heads:
            start = heads[-1][0]
            for l in lines[start:start + 60]:
                print(l[:500])
