import re, html
p='/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html'
t=open(p,encoding='utf-8').read()
t=re.sub(r'<style.*?</style>','',t,flags=re.S)
t=re.sub(r'<script.*?</script>','',t,flags=re.S)
t=re.sub(r'<details[^>]*>','\n[[D]]\n',t)
t=re.sub(r'</details>','\n[[/D]]\n',t)
t=re.sub(r'<br\s*/?>','\n',t)
t=re.sub(r'</(p|li|tr|h\d|div|summary)>','\n',t)
t=re.sub(r'</t[dh]>',' | ',t)
t=re.sub(r'<[^>]+>','',t)
t=html.unescape(t)
lines=[l.strip() for l in t.split('\n') if l.strip()]
depth=0
for i,l in enumerate(lines):
    if l=='[[D]]':
        depth+=1; continue
    if l=='[[/D]]':
        depth-=1; continue
    if depth==0 and ('第五节' in l or l.startswith('五') or '件' in l[:12]):
        print(i, l[:260])
