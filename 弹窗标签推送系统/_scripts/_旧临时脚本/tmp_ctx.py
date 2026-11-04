# -*- coding: utf-8 -*-
import re
b='/Users/decheng.huang/claude/弹窗标签推送系统/'
for f,cutkeys in [('决策汇报.html',['更正记录（顶部总结论']),('环节3_方案.html',['更正记录（30 条']),('支撑文件/08_弹窗效果评估方案.md',['## 更正记录'])]:
    t=open(b+f,encoding='utf-8').read()
    cut=len(t)
    for k in cutkeys:
        i=t.find(k)
        if i>0: cut=i
    print('=====',f,'cut',cut)
    for k in ['8.7%','4.0','3.2 ','约 9%','10.6%','5.0']:
        for m in re.finditer(re.escape(k),t):
            if m.start()<cut:
                print(' ',k,m.start(),t[max(0,m.start()-70):m.start()+70].replace('\n',' '))
