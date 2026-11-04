import re, os
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
keys = ['潜在付费沿用', '活动位按玩家身份拆分', '潜在流失定向覆盖', '上限 3', '34,979', '44,027',
        '首储购买率', '回升率', '人均每日弹窗曝光', '按日留存', '快照', '从未储值', '未首储', '23:30', '当月 1 日']
for fn in ['02_弹窗分人群定制方案_迭代稿.html', '08_弹窗效果评估方案.md']:
    txt = open(base + fn, encoding='utf-8').read()
    txt = re.sub(r'<[^>]+>', '', txt)
    print('=====', fn)
    for k in keys:
        for m in re.finditer(re.escape(k), txt):
            s = txt[max(0, m.start()-60):m.end()+80].replace('\n', ' ')
            print('[' + k + ']', s)
