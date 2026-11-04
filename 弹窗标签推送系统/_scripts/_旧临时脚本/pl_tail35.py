import os
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
def tail_from(path, marker_count=2, marker='\n## '):
    t = open(B + path, encoding='utf-8').read()
    idx = [i for i in range(len(t)) if t.startswith(marker, i)]
    start = idx[-marker_count] if len(idx) >= marker_count else 0
    return t[start:]
print('=====审查记录 最近两节=====')
print(tail_from('过程记录/审查记录.md', 2))
print('=====设计卡 最后一节=====')
print(tail_from('过程记录/设计卡.md', 1)[:12000])
t = open(B + '进展日志.md', encoding='utf-8').read().splitlines()
print('=====进展日志 末 12 行=====')
print('\n'.join(t[-12:]))
print('=====分析目录=====')
print(sorted(os.listdir(B + '分析')))
