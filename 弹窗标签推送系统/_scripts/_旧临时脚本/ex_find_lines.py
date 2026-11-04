"""只读：在决策汇报、环节1、A8、A11 中找含 _versions/search_terms.txt 各词的行号（原始文本，不转写）。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = ['决策汇报.html', '环节1_现状盘点.html', '分析/A8_卡别与最后登录.md', '分析/A11_会员等级.md']
terms = [t.strip() for t in open(os.path.join(BASE, '_versions', 'search_terms.txt'), encoding='utf-8') if t.strip()]
for f in files:
    lines = open(os.path.join(BASE, f), encoding='utf-8').read().split('\n')
    print('==', f, '行数', len(lines))
    for t in terms:
        for i, l in enumerate(lines):
            if t in l:
                j = l.find(t)
                print(f'  [{t}] 行 {i+1}（长 {len(l)}）：…{l[max(0,j-60):j+80]}…')
