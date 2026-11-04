"""只读：定位环节2、环节3 两份文件的首屏（body 起到第一个 section 前）与各节 h2 行号。"""
import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['环节2_问题诊断.html', '环节3_方案.html']:
    lines = open(base + f, encoding='utf-8').read().split('\n')
    print('=' * 20, f, '总行数', len(lines))
    for i, l in enumerate(lines, 1):
        if re.search(r'<body|<h1|<h2|<section|class="verdict|class="key|<style|</style>|<details', l):
            print(i, '|', l.strip()[:150])
