# Q175：只读，独立重数 A37 第三部分的状态，并核对与第二部分的 K 编号一一对应
import re
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
txt = open(B + '分析/A37_能力线现有能力.md', encoding='utf-8').read()
p2 = txt.split('## 第二部分')[1].split('**名字里仍带并列词')[0]
p3 = txt.split('## 第三部分')[1].split('### 与 04、05、07')[0]
k2 = [l.split('|')[1].strip() for l in p2.split('\n') if re.match(r'\| K\d+ \|', l)]
rows = [[c.strip() for c in l.strip().strip('|').split('|')] for l in p3.split('\n') if re.match(r'\| K\d+ \|', l)]
k3 = [r[0] for r in rows]
print('第二部分 K 项', len(k2), '第三部分行', len(k3), '集合相同', set(k2) == set(k3), '无重复', len(set(k3)) == len(k3))
print('列数', {len(r) for r in rows})
from collections import Counter
st = Counter(r[2] for r in rows)
dr = Counter(r[3] for r in rows if r[2] == '未知')
print('状态', dict(st), '未知方向', dict(dr))
print('有/没有 的方向列都是 —', all(r[3] == '—' for r in rows if r[2] in ('有', '没有')))
print('有', [r[0] for r in rows if r[2] == '有'])
print('没有', [r[0] for r in rows if r[2] == '没有'])
# 分块
blk = {}
cur = None
for l in p3.split('\n'):
    if l.startswith('#### '):
        cur = l[5:].strip()
    if re.match(r'\| K\d+ \|', l):
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        blk.setdefault(cur, Counter())[c[2]] += 1
print('分块', {k: dict(v) for k, v in blk.items()})
print('「→有」', txt.count('→有'), '「待 Q175」', txt.count('（待 Q175）'))
# 禁用出处文件检索（出处位置、出处类型两列）
ban = re.compile(r'(?<![0-9A-Za-z])0[2-9](?![0-9])|C1|C2|A\d{2}|汇报|同事草稿|设计卡')
print('禁用出处', [(r[0], r[5], r[6]) for r in rows if ban.search(r[5] + r[6])])
