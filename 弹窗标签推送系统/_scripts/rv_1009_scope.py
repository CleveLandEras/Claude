# 只读：抽取阶段8中本期范围相关文字；列出呈交版中 .ev / .pbk 规则的出现顺序与所在媒体查询
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
base = _ROOT + '/'
s8 = open(base + '阶段8_结论汇总.html', encoding='utf-8').read()
txt = re.sub(r'<[^>]+>', '\n', s8)
lines = [l.strip() for l in txt.split('\n') if l.strip()]
for i, l in enumerate(lines):
    if any(k in l for k in ['本期', '建议本期', '中期之后', '根因', '先做到中期', '依据不足']):
        print(i, l[:260])
print('=' * 40)
v1 = open(base + '弹窗标签推送方案_V1.html', encoding='utf-8').read()
css = v1.split('<style>')[1].split('</style>')[0]
# 逐字符跟踪媒体查询深度
depth = 0
media_stack = []
i = 0
cur = ''
pos = 0
for m in re.finditer(r'(@media[^{]*\{)|([^{}]+\{[^{}]*\})|(\})', css):
    if m.group(1):
        media_stack.append(m.group(1).strip())
    elif m.group(2):
        rule = m.group(2).strip()
        sel = rule.split('{')[0]
        if re.search(r'(^|[ ,])\.(ev|pbk)([ ,{]|$)', sel + ' '):
            line = css[:m.start()].count('\n') + 4
            print('line~', line, '|', media_stack[-1] if media_stack else '(无媒体查询)', '|', rule[:120])
    elif m.group(3):
        if media_stack:
            media_stack.pop()
for k in ['读法', '阅读时间', 'class="guide"', 'class="rt"']:
    print(k, v1.count(k))
