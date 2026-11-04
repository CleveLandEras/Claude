p='/Users/decheng.huang/claude/弹窗标签推送系统/分析/A36_验证计划.md'
t=open(p,encoding='utf-8').read()
for w in ['有效','证明','提升','不承诺','推后','理由弱','无效','没有效果','可以上线','可以直接']:
    for i,l in enumerate(t.split('\n'),1):
        if w in l:
            k=l.find(w)
            print(w,i,l[max(0,k-30):k+30].replace('\n',' '))
