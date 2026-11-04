import os, re, glob
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
terms = ['原样转发', '可以转发', '可转发', '可交研发', '可以交研发', '可以上线', '可上线', '可交数据组', '可以发给数据组', '今天就能发', '直接交', '直接发', '可以发出', '交主管前', '待 Dk 验收', 'Dk 验收']
paths = [B + '决策汇报.html'] + sorted(glob.glob(B + '环节*.html')) + sorted(glob.glob(B + '支撑文件/*')) + sorted(glob.glob(B + '分析/*.md')) + [B + '先看这里.md']
for p in paths:
    if p.endswith('.xlsx'):
        continue
    try:
        t = open(p, encoding='utf-8').read()
    except Exception as e:
        continue
    t2 = re.sub(r'<[^>]+>', '', t)
    hits = {k: t2.count(k) for k in terms if t2.count(k)}
    if hits:
        print(os.path.relpath(p, B), hits)
