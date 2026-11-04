import os
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
p = base + '过程记录/审查记录.md'
lines = open(p, encoding='utf-8').read().split('\n')
heads = [i for i, l in enumerate(lines) if l.startswith('## ')]
print('总行数', len(lines), '最后三节标题：')
for i in heads[-3:]:
    print(i + 1, lines[i])
# 未处理退回：状态为退回且其后没有已处理/有异议
start = heads[-1] if heads else 0
print('--- 最后一节全文 ---')
print('\n'.join(lines[start:])[:6000])
print('--- 进展日志末 5 行 ---')
pl = open(base + '进展日志.md', encoding='utf-8').read().strip().split('\n')
print('\n'.join(pl[-5:]))
print('暂停存在:', os.path.exists(base + '暂停.txt'))
