"""审查 09-30 11:19 只读：08、02、环节3 第五节里有没有判读、迭代（下一版）写法。只打印。"""
import os
from _textify import BASE, textify
def T(f):
    return textify(os.path.join(BASE, f)).replace('\n', ' ⏎ ')
for f in ['支撑文件/08_弹窗效果评估方案.md', '支撑文件/02_弹窗分人群定制方案.html', '环节3_方案.html']:
    s = T(f)
    for t in ['判读', '迭代', '下一步', '若结果', '结果怎么', '回滚', '停用', '改回']:
        i = s.find(t); n = 0
        while i != -1 and n < 3:
            n += 1
            print(f'[{f}] {t} …{s[max(0, i-90):i+len(t)+90]}…')
            i = s.find(t, i + len(t))
        if n == 0: print(f'[{f}] {t} 无命中')
