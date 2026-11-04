"""R137/R138 辅助：按 _versions/search_terms.txt 检索，只看交付物（排除 过程记录/、来源资料/、归档/），输出文件与短上下文。不带参数运行。"""
import os, glob
from _textify import BASE, textify
terms = [t.strip() for t in open(os.path.join(BASE, '_versions', 'search_terms.txt'), encoding='utf-8') if t.strip()]
files = sorted(p for p in glob.glob(os.path.join(BASE, '**', '*'), recursive=True)
               if p.endswith(('.md', '.html', '.xlsx')) and not any(x in p for x in ('/_scripts/', '/_versions/', '/数据/', '/归档/', '/过程记录/', '/来源资料/', '进展日志', '/简报/')))
for t in terms:
    print('=' * 40 + f' {t}')
    for p in files:
        s = textify(p).replace('\n', ' ⏎ ')
        i = s.find(t)
        while i != -1:
            print(f'  [{os.path.relpath(p, BASE)}] …{s[max(0,i-60):i+len(t)+60]}…')
            i = s.find(t, i + len(t))
