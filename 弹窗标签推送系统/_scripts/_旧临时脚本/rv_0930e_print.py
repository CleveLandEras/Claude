import re, html
p='/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/02_弹窗分人群定制方案.html'
t=open(p,encoding='utf-8').read()
t=re.sub(r'<style.*?</style>','',t,flags=re.S)
t=re.sub(r'<br\s*/?>','\n',t)
t=re.sub(r'</(p|li|tr|h\d|div|td|th|summary)>','\n',t)
t=re.sub(r'<[^>]+>','',t)
t=html.unescape(t)
lines=[l.strip() for l in t.split('\n') if l.strip()]
# print second card area
start=None
for i,l in enumerate(lines):
    if '潜在流失' in l and start is None and i>20:
        start=i
for i,l in enumerate(lines[:200]):
    print(i,l)
