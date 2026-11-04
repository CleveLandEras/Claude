import os, re
root = '/Users/decheng.huang/claude/弹窗标签推送系统/'
lines = open(root + '进展日志.md', encoding='utf-8').read().splitlines()
print('\n'.join(lines[-12:]))
print('\n==== 设计卡 ⚠ ====')
d = open(root + '过程记录/设计卡.md', encoding='utf-8').read()
for m in re.finditer(r'⚠[^\n]*', d):
    print(m.group(0)[:200])
print('\n==== 简报 目录 ====')
b = '/Users/decheng.huang/claude/简报/'
for p in [b, root + '简报/']:
    if os.path.isdir(p):
        for f in sorted(os.listdir(p)):
            fp = os.path.join(p, f)
            print(p, f, os.path.getmtime(fp))
