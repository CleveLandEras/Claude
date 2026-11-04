import re

base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for name in ('环节3_方案.html', '决策汇报.html'):
    t = open(base + name, encoding='utf-8').read()
    print('==', name, len(t))
    for tag in ('div', 'details', 'table', 'tr', 'td', 'th', 'p', 'section', 'ol', 'ul', 'li', 'summary', 'pre'):
        o = len(re.findall(r'<%s[\s>]' % tag, t))
        c = len(re.findall(r'</%s>' % tag, t))
        print(f'  {tag}: 开 {o} 闭 {c}', '' if o == c else '  <-- 不配对')

# 约束 102、110–112 原句仍在
t3 = open(base + '环节3_方案.html', encoding='utf-8').read()
for k in ('误撤约 4%–7%', '只算一个截尾值', '队列最后一日 + 13 日', '保留为现行版', '判读期结束，不再延长判读'):
    print('环节3', k, t3.count(k))
th = open(base + '决策汇报.html', encoding='utf-8').read()
for k in ('误撤约 4%–7%', '只算一个截尾值', '队列最后一日 + 13 日', '保留为现行版', '判读期结束，不再延长判读'):
    print('汇报', k, th.count(k))

# 约束 106 残留词（正文，去掉 更正记录、存档 之外无法自动区分，只报次数）
for k in ('Q166 定稿中', '还在定', '待 Q166', 'D+26', '保留并延长', '放掉对照', '等设计者 Q160', '四条判读线'):
    print('残留', k, '环节3', t3.count(k), '汇报', th.count(k))
# 合并标签四处仍在
print('环节3 合并标签', t3.count('合并标签'), '汇报 合并标签', th.count('合并标签'))
