import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
t = open(base + '决策汇报.html', encoding='utf-8').read()
m = re.search(r'<div class="verdict">(.*?)</div>', t, re.S)
print('VERDICT:', re.sub('<[^>]+>', '', m.group(1))[:1500] if m else None)
i = t.find('id="s2"')
seg = t[i:i + 9000]
print('\nS2 HEAD:', re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ', seg))[:3500])
print('\nverdict occurrences of 五类:', t.count('五类'))
rv = open(base + '过程记录/审查记录.md', encoding='utf-8').read()
heads = re.findall(r'^## .*$', rv, re.M)
print('\nREVIEW LAST HEADS:', heads[-4:])
print('\nREVIEW TAIL:', rv[-2500:])
