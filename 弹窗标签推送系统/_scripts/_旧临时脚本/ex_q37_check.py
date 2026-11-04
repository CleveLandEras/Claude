"""Q37 回归检查：00 与汇报附录问题 25 原话（HTML 反转义后）是否逐字一致；列出「6,000」相关句。只读。"""
import html, difflib
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
a = open(BASE + '支撑文件/00_推进记录.md', encoding='utf-8').read()
b = html.unescape(open(BASE + '决策汇报.html', encoding='utf-8').read())
def q25(t):
    i = t.index('25. 有几件事想确认')
    j = t.index('\n', t.index('  d. ', i))
    return t[i:j]
x, y = q25(a), q25(b)
print('问题 25 逐字一致（反转义后）:', x == y, len(x), len(y))
for l in difflib.unified_diff(x.split('\n'), y.split('\n'), lineterm=''):
    if l.startswith(('+', '-')):
        print(l)
for name, t in (('00', a), ('汇报', b)):
    k = t.find('押注恰好')
    print(name, '押注恰好 所在句:', t[max(0, k - 60):k + 60] if k >= 0 else '无')
raw = open(BASE + '决策汇报.html', encoding='utf-8').read()
print('汇报原始 HTML 中 25 d 附近的实体：', sorted(set(e for e in __import__('re').findall(r'&[a-z#0-9]+;', q25(raw)))))
