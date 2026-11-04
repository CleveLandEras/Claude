"""定位迭代记录中各文件节与最新版本行号（只读）。"""
import os
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/迭代记录.md'
for i, line in enumerate(open(p, encoding='utf-8'), 1):
    s = line.strip()
    if s.startswith('## ') or s.startswith('### v92') or s.startswith('### v12') or s.startswith('### v4（') or s.startswith('### v93') or s.startswith('### v13') or s.startswith('### v5（'):
        print(i, s[:90])
