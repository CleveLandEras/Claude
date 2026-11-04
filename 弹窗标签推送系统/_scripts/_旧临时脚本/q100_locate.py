"""Q100：列出相关句在汇报、环节3、02 的行号（只读）。不带参数运行。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = ['决策汇报.html', '环节3_方案.html', '支撑文件/02_弹窗分人群定制方案.html']
terms = ('300 元以内', '160 元', '160–300', '47 条', '更正记录（', '17 条')
for f in files:
    p = os.path.join(BASE, f)
    if not os.path.exists(p):
        print('不存在：', f); continue
    with open(p, encoding='utf-8') as fh:
        for i, line in enumerate(fh, 1):
            for t in terms:
                if t in line:
                    print(f'{f}:{i} [{t}] {line.strip()[:220]}')
                    break
