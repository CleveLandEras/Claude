# 只读：看环节1 缺口表「总充值金额」一行及第 2 句相关处
import re, html
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
s = open(B+'环节1_现状盘点.html', encoding='utf-8').read()
s = re.sub(r'<(script|style)[\s\S]*?</\1>', '', s)
s = re.sub(r'<br\s*/?>|</(p|div|li|tr|td|th|h\d|summary|section)>', '\n', s)
s = re.sub(r'<[^>]+>', '', s)
L = [l.strip() for l in html.unescape(s).split('\n') if l.strip()]
for i in range(940, 952):
    print(i, L[i][:700])
print('---')
for i, l in enumerate(L[:964]):
    if '运营第 2 句' in l or '第 2 句' in l:
        k = l.find('第 2 句')
        print(i, l[max(0, k-120):k+60])
