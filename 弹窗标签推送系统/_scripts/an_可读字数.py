# 统计文件里人要读的字数（不计网页标签、样式、脚本、图形与空白、Markdown 符号）
# 用法：python3 _scripts/an_可读字数.py 文件 [文件 ...]；html 另报折叠块（<details>）内的字数
import re, html, sys


def count_html(t):
    t = re.sub(r'<(style|script|svg)[\s\S]*?</\1>', '', t)
    det = sum(len(re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', ' ', x)))) for x in re.findall(r'<details[\s\S]*?</details>', t))
    return len(re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', ' ', t)))), det


def count_md(t):
    t = re.sub(r'\]\([^)]*\)', ']', t)
    return len(re.sub(r'[\s|#*`>\-:=_~\[\]]+', '', t))


for p in sys.argv[1:]:
    t = open(p, encoding='utf-8').read()
    if p.endswith(('.html', '.htm')):
        n, d = count_html(t)
        print(f'{p}\t可读 {n} 字\t其中折叠 {d} 字')
    else:
        print(f'{p}\t可读 {count_md(t)} 字')
