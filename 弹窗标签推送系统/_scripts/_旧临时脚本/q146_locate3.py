import re, os
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
s = open(base + '决策汇报.html', encoding='utf-8').read()
for t in ['11③', '11 ③', '实验分流', '为了留住高卡']:
    for m in re.finditer(t, s):
        print('##', t, m.start(), s[max(0, m.start()-200):m.end()+300].replace('\n', ' '))
        print()
i = s.find('<h2', s.rfind('更正记录') - 2000)
print('更正记录 heads', [m.start() for m in re.finditer('更正记录', s)][-6:])
print(s[-3500:])
print('-----files')
for d in ['支撑文件', '分析']:
    print(d, sorted(os.listdir(base + d)))
