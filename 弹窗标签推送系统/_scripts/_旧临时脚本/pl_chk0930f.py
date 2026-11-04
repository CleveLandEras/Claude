import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
t = open(base + '过程记录/设计卡.md', encoding='utf-8').read()
for key in ['## Q130', '## Q131']:
    i = t.find(key)
    j = t.find('\n## ', i + 5)
    sec = t[i: j if j > 0 else len(t)]
    print('=====', key)
    for w in ['档内', '十等份', '更细', '回归', '平衡', '咬分', '执行结果']:
        print('--', w, sec.count(w))
        for m in list(re.finditer(w, sec))[:2]:
            print('     ', sec[max(0, m.start()-80):m.end()+80].replace('\n', ' '))
