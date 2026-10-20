"""审查者用：写完「过审审核：通过」后运行，不带参数。
读审查记录.md 最后一节；这一节有「过审审核：通过」时，把这一节标题与过审审核结论里提到的文件（「阶段 N」「呈交版」）
按当前内容记下哈希。之后这些文件只要内容一改，status.py 就显示「待复核」。没有「通过」就什么都不记。"""
import os, re
from state_lib import BASE, load, save, digest, files_in, now

rec = open(os.path.join(BASE, '过程记录', '审查记录.md'), encoding='utf-8').read()
secs = re.split(r'\n(?=## )', rec)
last = secs[-1] if secs else ''
head = last.splitlines()[0] if last else ''
verdict = re.findall(r'过审审核[：:]\s*\**\s*通过[^\n]*', last)
if not verdict:
    print('结论：最后一节没有「过审审核：通过」，不记录')
else:
    names = files_in(head + '\n' + '\n'.join(verdict))
    if not names:
        print('结论：找不到涉及的文件（标题或过审审核结论里要写「阶段 N」「呈交版」），不记录')
    else:
        store = load()
        for n in names:
            store[n] = {'sha256': digest(n), 'at': now(), 'by': head.lstrip('# ').strip()[:80]}
        save(store)
        print('已记录过审：', '、'.join(names))
