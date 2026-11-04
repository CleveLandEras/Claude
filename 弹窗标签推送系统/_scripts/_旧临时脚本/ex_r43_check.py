"""R43：检查汇报、环节1、A8 中旧结论是否还有残留（只读）。不带参数运行。"""
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
keys = ['28–43', '押注解释不了大部分', '多数仍在', '多数比较里仍有', '相当一部分来自押注', '转发数据']
for name in ('决策汇报.html', '环节1_现状盘点.html', '分析/A8_卡别与最后登录.md', '00_推进记录.md'):
    s = open(B + name, encoding='utf-8').read()
    for k in keys:
        i = s.find(k)
        while i != -1:
            print(f'[{name}] [{k}] …{s[max(0, i-60):i+len(k)+40]}…'.replace('\n', ' '))
            i = s.find(k, i + len(k))
