"""审查 09-30 11:19 只读：工作原则 v3 生效后，计划与交付物是否按 v3 核过。只打印。"""
import os
from _textify import BASE, textify
def T(f):
    return textify(os.path.join(BASE, f)).replace('\n', ' ⏎ ')
def ctx(label, s, t, w=140, k=6):
    i = s.find(t); n = 0
    print('==', label, '|', t)
    while i != -1 and n < k:
        n += 1
        print(f'   …{s[max(0, i-w):i+len(t)+w]}…')
        i = s.find(t, i + len(t))
    if n == 0: print('   无命中')
log = T('进展日志.md')
print('== 进展日志末 3000 字'); print(log[-3000:])
plan = T('过程记录/推进计划.md')
for t in ['v3', '方案线', '能力线', '旧结论清点']:
    ctx('推进计划', plan, t, 120, 4)
for f in ['决策汇报.html', '环节3_方案.html', '支撑文件/02_弹窗分人群定制方案.html', '支撑文件/08_弹窗效果评估方案.md']:
    s = T(f)
    for t in ['v3', '下一版', '能力线', '判读规则']:
        ctx(f, s, t, 100, 3)
for f in ['支撑文件/04_弹窗功能缺口需求.md', '支撑文件/07_推送需求.md']:
    s = T(f)
    i = s.find('## 提案')
    print('==', f, '提案节'); print(s[i:i+1500] if i != -1 else '   无提案节')
    ctx(f, s, '测不出', 100, 3)
