"""A80 第七节检索：对阶段1–8逐词计数，并导出命中所在行供分类。只读，输出到 _versions/a80_hits.txt。"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _textify import textify, BASE

TERMS = ['无数据', '无记载', '缺失', '缺数据', '查不到', '看不到', '不可实现', '推断不可实现', '未留存', '未汇总',
         '发送量', '到达率', '到达量', '召回', '回流', '购买', '关闭事件', '客户端上报', '待数据', '效果查不到',
         '短信', '点击偏低', '没有记录', '有无记录', '各自有记录', '推送数据']
FILES = [f'阶段{i}_' for i in range(1, 9)]
names = {}
for f in sorted(os.listdir(BASE)):
    for pre in FILES:
        if f.startswith(pre) and f.endswith('.html'):
            names[pre] = f

texts = {}
for pre, f in names.items():
    texts[pre] = textify(os.path.join(BASE, f)).splitlines()

out = []
# 计数表
hdr = '词\\文件 ' + ' '.join(f'{p[:3]:>6}' for p in FILES)
out.append(hdr)
for t in TERMS:
    row = []
    for p in FILES:
        n = sum(l.count(t) for l in texts.get(p, []))
        row.append(f'{n:>6}')
    out.append(f'{t:<8} ' + ' '.join(row))
out.append('')
# 命中行
for t in TERMS:
    out.append('=' * 30 + ' ' + t)
    for p in FILES:
        for i, l in enumerate(texts.get(p, []), 1):
            if t in l:
                k = l.index(t)
                a = max(0, k - 30)
                out.append(f'[{p[:3]} L{i}] ' + l[a:k + len(t) + 40].replace('\n', ' '))
open(os.path.join(BASE, '_versions', 'a80_hits.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('done', len(out))
