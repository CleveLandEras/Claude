"""只读：列出迭代记录.md 中环节2 一节下全部 ### 版本条目（行号）。"""
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/迭代记录.md'
lines = open(p, encoding='utf-8').read().split('\n')
cur = None
for i, l in enumerate(lines, 1):
    if l.startswith('## '):
        cur = l
    elif l.startswith('### ') and cur == '## 环节2_问题诊断.html':
        print(i, '|', l[:120])
print('总行数', len(lines))
