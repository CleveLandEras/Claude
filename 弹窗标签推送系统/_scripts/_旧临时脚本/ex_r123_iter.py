"""定位迭代记录各文件节与最新版本号（只读）。"""
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/迭代记录.md'
ls = open(p, encoding='utf-8').read().split('\n')
print(len(ls), '行')
for i, l in enumerate(ls, 1):
    if l.startswith('## ') or l.startswith('### v78') or l.startswith('### v21') or ('v78' in l[:20]) or ('v21' in l[:20]):
        print(i, l[:120])
