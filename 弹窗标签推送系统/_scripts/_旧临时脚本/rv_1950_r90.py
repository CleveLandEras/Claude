import re, os
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
files = ['决策汇报.html', '环节1_现状盘点.html', '支撑文件/00_推进记录.md', '过程记录/推进计划.md']
terms = ['怎么保级', '分得开', '就能分清', '升级部分已确认', '累计周期', '71 条', '70 条', '8 条', '7 条', '主要是哪']
for f in files:
    p = B + f
    if not os.path.exists(p):
        print('缺文件', f); continue
    t = open(p, encoding='utf-8').read()
    if f.endswith('.html'):
        t = re.sub(r'<[^>]+>', '\n', t)
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    print('=====', f)
    for term in terms:
        for i, l in enumerate(lines):
            if term in l:
                k = l.find(term)
                print(f'[{term}] L{i}: ...{l[max(0,k-80):k+80]}...')
