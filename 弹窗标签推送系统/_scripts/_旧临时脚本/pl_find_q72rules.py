"""只读：在 _versions/ 与 过程记录/ 下找含 Q72 规则原文（「规则 10」或「10.」附近含 Q72）的文件，打印文件名与首处命中位置。"""
import os, glob
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cands = sorted(glob.glob(os.path.join(BASE, '_versions', '**', '*'), recursive=True)) + \
        sorted(glob.glob(os.path.join(BASE, '过程记录', '*')))
for p in cands:
    if not os.path.isfile(p) or not p.endswith(('.md', '.txt', '.html')):
        continue
    try:
        s = open(p, encoding='utf-8').read()
    except Exception:
        continue
    if 'Q72' in s and ('规则 1–10' in s or 'Q72 规则' in s):
        i = s.find('Q72 规则')
        print(os.path.relpath(p, BASE), len(s), 'pos', i, '|', s[max(0, i-40):i+120].replace('\n', ' ⏎ '))
