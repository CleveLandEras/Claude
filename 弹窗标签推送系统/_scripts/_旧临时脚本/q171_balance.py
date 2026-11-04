import re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['支撑文件/02_弹窗分人群定制方案.html', '决策汇报.html', '环节3_方案.html']:
    t = open(BASE + f, encoding='utf-8').read()
    print(f)
    for tag in ['details', 'section', 'table', 'div', 'ul', 'ol', 'article', 'tr', 'td']:
        o = len(re.findall(r'<%s[\s>]' % tag, t)); c = len(re.findall(r'</%s>' % tag, t))
        print('  ', tag, o, c, '' if o == c else '  <-- 不平衡')
t = open(BASE + '支撑文件/02_弹窗分人群定制方案.html', encoding='utf-8').read()
heads = re.findall(r'<h2 class="sec">(.*?)</h2>', t)
print(heads)
for w in ['本方案', '待确认', '可以上线']:
    body = t.split('<h2 class="sec">按玩家看</h2>')[1].split('<h2 class="sec">决策项</h2>')[0]
    print('新增部分含「%s」：' % w, w in body)
