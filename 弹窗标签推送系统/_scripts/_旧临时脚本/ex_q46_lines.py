"""Q46 定位：列出 00_推进记录.md 的标题行与含关键词的行号。只读。"""
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
lines = open(BASE + '支撑文件/00_推进记录.md', encoding='utf-8').read().split('\n')
KEYS = ['发给研发', '发给运营', '发给数据', '发给标签', '9-2', '9-3', '```', '<pre', '总览']
for i, l in enumerate(lines, 1):
    if l.startswith('#') or any(k in l for k in KEYS):
        print(i, l[:110])
print('总行数', len(lines))
