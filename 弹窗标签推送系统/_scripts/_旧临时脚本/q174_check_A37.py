import re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
t = open(BASE + '分析/A37_能力线现有能力.md', encoding='utf-8').read()
for w in ['最关键', '优先', '首要', '重要', '值得做', '不值得', '必须做', '应该做', '本方案', '待确认', '可以上线', '可原样转发', '可直接交']:
    hits = [m.start() for m in re.finditer(w, t)]
    print(w, len(hits))
    for h in hits[:6]:
        print('   ', repr(t[max(0, h - 40):h + 40]))
print(len(t))
# 表格列数检查
bad = 0
for i, line in enumerate(t.split('\n'), 1):
    if line.startswith('| ') and set(line) != {'|', '-'} :
        pass
rows = [l for l in t.split('\n') if l.startswith('|')]
print('表格行', len(rows))
