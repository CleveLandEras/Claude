"""通用检索：先用 Write 把要查的词写进 _versions/search_terms.txt（每行一个），再运行本脚本。不带参数运行。
在工作目录所有 .md / .html / .xlsx 文件（含盘点、任务清单、各记录）中检索，输出每处命中的前后文。"""
import os, glob
from _textify import BASE, textify
tp = os.path.join(BASE, '_versions', 'search_terms.txt')
if not os.path.exists(tp):
    print('请先把检索词写进 _versions/search_terms.txt（每行一个）'); raise SystemExit
terms = [t.strip() for t in open(tp, encoding='utf-8') if t.strip()]
files = sorted(p for p in glob.glob(os.path.join(BASE, '**', '*'), recursive=True)
               if p.endswith(('.md', '.html', '.xlsx')) and not any(x in p for x in ('/_scripts/', '/_versions/', '/数据/', '/归档/')))
for t in terms:
    print('=' * 60 + f'\n检索词：{t}')
    hits = 0
    for p in files:
        try: s = textify(p)
        except Exception as e: print(f'  {os.path.basename(p)}：读取失败 {e}'); continue
        flat = s.replace('\n', ' ⏎ ')
        i = flat.find(t)
        while i != -1 and hits < 40:
            hits += 1
            print(f'  [{os.path.relpath(p, BASE)}] …{flat[max(0,i-90):i+len(t)+90]}…')
            i = flat.find(t, i + len(t))
    if hits == 0: print('  无命中')
