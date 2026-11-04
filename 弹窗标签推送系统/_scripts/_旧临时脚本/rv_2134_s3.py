# 只读：看汇报第三、四、五节标题与首段，检查与新总结论是否冲突
import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
rep = open(base + '决策汇报.html', encoding='utf-8').read()
for sid in ['s3', 's4', 's5']:
    i = rep.find(f'<section id="{sid}">')
    seg = rep[i:i+2500]
    print('=====', sid)
    print(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', seg))[:1200])
for kw in ['不需要开发', '五类人群', '不用开发']:
    for m in re.finditer(kw, rep):
        print(kw, '…', re.sub(r'<[^>]+>', '', rep[max(0,m.start()-100):m.end()+60]).replace('\n',' '))
