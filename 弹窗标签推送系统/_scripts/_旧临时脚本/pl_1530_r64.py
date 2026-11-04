import re, os
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
TERMS = ['没有手机推送', '从零建设', '从零建', '没有推送能力', '没有真正的推送', '没有站外推送', '能力为零', '来源冲突', '前提不成立', '触达不到', '通知不到']
FILES = ['决策汇报.html', '环节1_现状盘点.html', '先看这里.md', '过程记录/设计卡.md', '支撑文件/00_推进记录.md']
for d in ['分析', '支撑文件']:
    for f in sorted(os.listdir(B + d)):
        if f.endswith(('.md', '.html')):
            FILES.append(d + '/' + f)
for p in FILES:
    try:
        txt = open(B + p, encoding='utf-8').read()
    except Exception as e:
        continue
    hits = {t: txt.count(t) for t in TERMS if t in txt}
    if hits:
        print(p, hits)
print('---- Q46 mentions')
for p in ['过程记录/迭代记录.md', '支撑文件/00_推进记录.md', '进展日志.md']:
    txt = open(B + p, encoding='utf-8').read()
    for l in txt.splitlines():
        if 'Q46' in l:
            print(p, '|', l[:400])
print('---- 分析 files')
print(sorted(os.listdir(B + '分析')))
