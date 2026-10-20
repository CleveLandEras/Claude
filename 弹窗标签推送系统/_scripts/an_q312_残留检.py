"""Q312 后残留检查：阶段 5、6 里旧数字与旧说法。只读。"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _textify import textify, BASE

TERMS = ['14 个场景', '5 个根因', '10 个缺口', '12 项', '短期 12', '长期 10', '缺失 6', '6 项缺数据', '13 个为推断', '待数据', '关闭事件', '回流衡量', '各通路补记录', '推送数据']
for f in ['阶段5_方案选型.html', '阶段6_方案设计.html']:
    lines = textify(os.path.join(BASE, f)).splitlines()
    print('=====', f)
    for t in TERMS:
        for i, l in enumerate(lines, 1):
            if t in l:
                k = l.index(t)
                print(f'[{t}] L{i}: ' + l[max(0, k - 25):k + len(t) + 35])
