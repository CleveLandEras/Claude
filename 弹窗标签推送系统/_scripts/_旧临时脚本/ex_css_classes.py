"""检查环节1 样式里是否定义了 .small、.take（只读）。不带参数运行。"""
s = open('/Users/decheng.huang/claude/弹窗标签推送系统/环节1_现状盘点.html', encoding='utf-8').read()
head = s.split('</style>')[0]
for k in ['.small', '.take', 'p.small', '.note']:
    print(k, k in head)
