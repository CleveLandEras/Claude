"""只读检索：04 首次评估（Q3）所需的 02、00、盘点、目标脑图相关片段。"""
import os
from _textify import BASE, textify
targets = ['02_弹窗分人群定制方案.html', '00_推进记录.md', 'claude_弹窗标签推送_盘点.html', '目标脑图.md']
terms = ['总量', '负反馈', '分流', '新手挑战', '新手通行证', '关闭', '客户端', '问题 6', '分组', '上限']
for f in targets:
    p = os.path.join(BASE, f)
    s = textify(p).replace('\n', ' ⏎ ')
    print('=' * 60 + '\n' + f)
    for t in terms:
        i = s.find(t); n = 0
        while i != -1 and n < 8:
            n += 1
            print(f'  [{t}] …{s[max(0, i-120):i+len(t)+120]}…')
            i = s.find(t, i + len(t) + 200)
