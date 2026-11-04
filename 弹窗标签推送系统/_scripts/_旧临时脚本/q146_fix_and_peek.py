import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
p = base + '决策汇报.html'
s = open(p, encoding='utf-8').read()
old1 = '改写前不作推荐，也不写条件式推荐；定之前按主管范围交研发。原条件式推荐移入页末存档框。'
new1 = '改写前不作推荐，也不再写按通路条件选乙或丙的推荐；定之前按主管范围交研发。原写法移入页末存档框。'
assert s.count(old1) == 1
s = s.replace(old1, new1)
open(p, 'w', encoding='utf-8').write(s)
print('fixed')

# 审查记录 R200
t = open(base + '过程记录/审查记录.md', encoding='utf-8').read()
i = t.find('### R200')
print('R200 at', i, 'len', len(t))
j = t.find('\n### ', i + 5)
print(t[i:j if j > 0 else i + 3000][:3500])
# 迭代记录结构
it = open(base + '过程记录/迭代记录.md', encoding='utf-8').read()
print('迭代记录 len', len(it))
for m in re.finditer(r'^#{1,3} .*$', it, re.M):
    print(m.start(), m.group(0)[:80])
print('TAIL', it[-800:])
# 任务清单第六节尾、进展日志尾
tl = open(base + '过程记录/任务清单.md', encoding='utf-8').read()
print('任务清单 tail', tl[-900:])
pg = open(base + '进展日志.md', encoding='utf-8').read()
print('进展日志 head', pg[:600])
print('进展日志 tail', pg[-1200:])
