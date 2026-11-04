"""只读：决策汇报.html 中「5.6 万」出现处（标出是否在折叠块内）与更正记录表最后三行。"""
import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html'
s = open(p, encoding='utf-8').read()
lines = s.split('\n')
depth = 0
for i, l in enumerate(lines, 1):
    for tk in re.findall(r'<details[^>]*>|</details>|5\.6 万', l):
        if tk.startswith('<details'): depth += 1
        elif tk == '</details>': depth -= 1
        else:
            k = l.find('5.6 万')
            print(i, '折叠' if depth > 0 else '正文', '|', l[max(0, k-80):k+20].strip())
k = s.find('更正记录（顶部总结论')
seg = s[k:]
rows = re.findall(r'<tr>.*?</tr>', seg, flags=re.S)
print('更正记录行数', len(rows))
for r in rows[:2] + rows[-3:]:
    print(r[:500]); print('---')
