# 只读：列出任务清单「## 」节标题与行号、总行数，便于在第六节末尾追加日志
p = '/Users/decheng.huang/claude/弹窗标签推送系统/任务清单.md'
lines = open(p, encoding='utf-8').read().split('\n')
for i, s in enumerate(lines, 1):
    if s.startswith('## '):
        print(i, s[:60])
print('总行数', len(lines))
