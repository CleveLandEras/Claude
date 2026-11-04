import os
base = '/Users/decheng.huang/claude/弹窗标签推送系统'
for rel, n in [('过程记录/审查记录.md', 40), ('进展日志.md', 8)]:
    p = os.path.join(base, rel)
    with open(p, encoding='utf-8') as f:
        lines = f.readlines()
    print('=====', rel, '共', len(lines), '行')
    for i, l in enumerate(lines[-n:], start=len(lines) - n + 1):
        print(i, l.rstrip()[:400])
print('暂停.txt 存在：', os.path.exists(os.path.join(base, '暂停.txt')))
