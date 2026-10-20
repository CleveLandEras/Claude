# 抽出材料里读者最先看、看得最多的文字：首屏、各级标题、标题下第一行、页头、结尾。
# 用法：python3 _scripts/an_读者要读的.py 文件.html [输出.md]
# 用途：交付前给无上下文读者审读、主对话自己读（见 规则与交接/交付前必查.md 第 7 条）；比读全文便宜得多。
import re, html, sys

src = sys.argv[1]
t = open(src, encoding='utf-8').read()
t = re.sub(r'<(style|script)[\s\S]*?</\1>', '', t)
t = re.sub(r'src="data:[^"]+"', '', t)


def txt(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


out = []
body = txt(t)
out.append('## 首屏（正文前 400 字）\n' + body[:400])

out.append('\n## 各级标题与紧跟的第一行')
for m in re.finditer(r'<(h[1-4])[^>]*>([\s\S]*?)</\1>', t):
    title = txt(m.group(2))
    nxt = re.search(r'<(p|div|ul|li|span)[^>]*>([\s\S]*?)</\1>', t[m.end():m.end() + 600])
    first = txt(nxt.group(2))[:120] if nxt else ''
    out.append(f'- [{m.group(1)}] {title}' + (f'\n    ↳ {first}' if first else ''))

heads = re.findall(r'class="[^"]*(?:crumb|pghead|page-head|top)[^"]*"[^>]*>([\s\S]*?)</', t)
if heads:
    out.append('\n## 页头（前 5 个）')
    out += ['- ' + txt(h)[:120] for h in heads[:5]]

out.append('\n## 结尾（正文最后 300 字）\n' + body[-300:])
res = '\n'.join(out)
if len(sys.argv) > 2:
    open(sys.argv[2], 'w', encoding='utf-8').write(res)
print(res if len(sys.argv) <= 2 else f'已写入 {sys.argv[2]}，{len(res)} 字')
