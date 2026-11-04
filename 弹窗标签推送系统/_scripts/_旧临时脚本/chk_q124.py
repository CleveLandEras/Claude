"""Q124 自查：04 正文检索「首期」「推后」「A26」（提案之前）；汇报「改写中」残留与标签配对。只读，不带参数。"""
import re
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
t = open(B + '支撑文件/04_弹窗功能缺口需求.md', encoding='utf-8').read()
i = t.index('## 提案')
body, prop = t[:i], t[i:]
for w in ['首期', '推后', 'A26']:
    print(f'{w}: 正文 {body.count(w)}；提案 {prop.count(w)}')
    for m in re.finditer(w, body):
        print('   …', body[max(0, m.start() - 30): m.start() + 40].replace('\n', ' '))
g = open(B + '决策汇报.html', encoding='utf-8').read()
print('汇报「改写中」:', g.count('改写中'))
for m in re.finditer('改写中', g):
    print('   …', re.sub(r'<[^>]+>', '', g[max(0, m.start() - 40): m.start() + 30]))
for tag in ['div', 'details', 'summary', 'table', 'tr', 'p']:
    o = len(re.findall(rf'<{tag}[\s>]', g)); c = len(re.findall(rf'</{tag}>', g))
    print(tag, o, c, '' if o == c else '<-- 不平衡')
