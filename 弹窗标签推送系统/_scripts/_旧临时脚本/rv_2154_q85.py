import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/环节3_方案.html'
s = open(p, encoding='utf-8').read()
print('prefers-color-scheme:', s.count('prefers-color-scheme'))
print('data-theme:', s.count('data-theme'))
ids = re.findall(r'id="([^"]+)"', s)
hrefs = re.findall(r'href="#([^"]+)"', s)
print('ids:', ids)
print('hrefs:', hrefs)
print('missing anchors:', [h for h in hrefs if h not in ids])
print('external links:', re.findall(r'href="([^#"][^"]*)"', s))
# 口径约束编号
plan = open('/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/推进计划.md', encoding='utf-8').read()
sec = plan.split('环节3 必须遵守的口径约束')[1].split('## 一、')[0]
items = re.findall(r'^(\d+(?:、\d+)?)\. (.+)$', sec, re.M)
print('plan items:', len(items))
txt = re.sub(r'<[^>]+>', '', s)
txt = txt.replace('&amp;', '&')
miss = []
for n, t in items:
    t2 = t.replace('**', '')
    if t2 not in txt:
        miss.append((n, t2[:40]))
print('not found verbatim:', miss)
