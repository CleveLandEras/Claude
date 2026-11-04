import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
t = open(base + '过程记录/迭代记录.md', encoding='utf-8').read()
parts = re.split(r'\n(?=## )', t)
for p in parts[1:]:
    head = p.split('\n', 1)[0]
    vs = re.findall(r'^(v\d+(?:\.\d+)?)[（(]([^）)]*)[）)]', p, flags=re.M)
    print(head, '| 版本数', len(vs), '| 最后', vs[-1] if vs else None, '| 长度', len(p))
    last = [l for l in p.split('\n') if l.strip()][-1]
    print('    末行:', last[:160])
