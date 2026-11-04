import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
t = open(base + '决策汇报.html', encoding='utf-8').read()
t = re.sub(r'<[^>]+>', ' ', t)
t = re.sub(r'\s+', ' ', t)
for w in ['② 07 现版本只含手机推播', '其中只有 2 项要新写 SQL']:
    i = t.find(w)
    print('=====', w, i)
    print(t[max(0, i-500):i+250])
