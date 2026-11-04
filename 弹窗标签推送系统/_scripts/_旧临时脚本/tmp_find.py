# -*- coding: utf-8 -*-
b='/Users/decheng.huang/claude/弹窗标签推送系统/'
ls=open(b+'过程记录/推进计划.md',encoding='utf-8').read().split('\n')
for i,l in enumerate(ls,1):
    if l.startswith('- [ ] Q157'):
        print(i,l)
