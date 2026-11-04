"""只读：定位决策汇报.html 中第五节与第 4 条所在行号。"""
import os
p = '/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html'
lines = open(p, encoding='utf-8').read().split('\n')
print('总行数', len(lines))
keys = ['<h2', 'N1 写几档', 'class="dec', 'class="opt', '<style', '</style>', 'prefers-color-scheme', '<details']
for i, l in enumerate(lines, 1):
    for k in keys:
        if k in l:
            print(i, k, '|', l.strip()[:160])
            break
