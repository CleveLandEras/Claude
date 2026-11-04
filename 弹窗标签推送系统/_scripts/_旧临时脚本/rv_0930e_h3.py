import re, html
p='/Users/decheng.huang/claude/弹窗标签推送系统/环节3_方案.html'
t=open(p,encoding='utf-8').read()
t=re.sub(r'<style.*?</style>','',t,flags=re.S)
t=re.sub(r'<script.*?</script>','',t,flags=re.S)
t=re.sub(r'<details[^>]*>','\n[[DETAILS]]\n',t)
t=re.sub(r'</details>','\n[[/DETAILS]]\n',t)
t=re.sub(r'<br\s*/?>','\n',t)
t=re.sub(r'</(p|li|tr|h\d|div|summary)>','\n',t)
t=re.sub(r'</t[dh]>',' | ',t)
t=re.sub(r'<[^>]+>','',t)
t=html.unescape(t)
lines=[l.strip() for l in t.split('\n') if l.strip()]
depth=0
out=[]
for i,l in enumerate(lines):
    if l=='[[DETAILS]]':
        depth+=1; out.append(f'{i} >>>折叠开始 depth={depth}'); continue
    if l=='[[/DETAILS]]':
        out.append(f'{i} <<<折叠结束 depth={depth}'); depth-=1; continue
    out.append(f'{i} {"  "*depth}{l}')
open('/Users/decheng.huang/claude/弹窗标签推送系统/_versions/rv_h3.txt','w',encoding='utf-8').write('\n'.join(out))
print(len(out))
