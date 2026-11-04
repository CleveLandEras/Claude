import re, html
base='/Users/decheng.huang/claude/弹窗标签推送系统/'
def lines_of(p):
    t=open(base+p,encoding='utf-8').read()
    t=re.sub(r'<style.*?</style>','',t,flags=re.S)
    t=re.sub(r'<script.*?</script>','',t,flags=re.S)
    t=re.sub(r'<details[^>]*>','\n[[D]]\n',t)
    t=re.sub(r'</details>','\n[[/D]]\n',t)
    t=re.sub(r'<br\s*/?>','\n',t)
    t=re.sub(r'</(p|li|tr|h\d|div|summary)>','\n',t)
    t=re.sub(r'</t[dh]>',' | ',t)
    t=re.sub(r'<[^>]+>','',t)
    t=html.unescape(t)
    ls=[l.strip() for l in t.split('\n') if l.strip()]
    out=[];d=0
    for l in ls:
        if l=='[[D]]': d+=1; continue
        if l=='[[/D]]': d-=1; continue
        out.append((d,l))
    return out
keys=['只有 2 项','推送条','按 A29 重核','已上线','依据：','第 2–7 行','有条件才建','新写 SQL','次线','主线','停用','非金卡以上','储值未下滑','还在改']
for p in ['决策汇报.html','环节3_方案.html']:
    print('=====',p)
    for i,(d,l) in enumerate(lines_of(p)):
        if d==0 and any(k in l for k in keys) and '更正' not in l[:10]:
            print(i,'D%d'%d,l[:400])
