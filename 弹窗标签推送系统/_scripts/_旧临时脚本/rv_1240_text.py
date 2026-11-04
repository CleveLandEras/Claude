# 只读：把决策汇报、环节3 转成纯文本，打印指定关键词附近的行
import re, html, os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
def text_lines(path):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'</(p|div|li|tr|h\d|td|th|summary|section|table)>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    return [l.strip() for l in s.split('\n') if l.strip()]
KEYS = ['保证', '四条', '第 12 件', '护栏判读门槛', '宽窄线', '路 C 下', '只看', '补问', '人均购买人数', '曝光超上限', '全部玩家，排除新增', '分桶·处理', '第 17 件', '方向一致']
for f in ['决策汇报.html', '环节3_方案.html']:
    L = text_lines(BASE + f)
    print('=' * 60, f, len(L))
    for i, l in enumerate(L):
        if any(k in l for k in KEYS):
            print(i, '|', l[:900])
            print('-')
