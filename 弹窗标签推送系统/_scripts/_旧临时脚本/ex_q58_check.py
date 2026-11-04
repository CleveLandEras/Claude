"""Q58 核对：汇报附录与 00 现行版「Dk 自查」表逐行一致；R79 旧标题只在更正括注；A13 旧写法只在更正括注。只读，不带参数。"""
import os, re
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rep = open(os.path.join(B, '决策汇报.html'), encoding='utf-8').read()
z = open(os.path.join(B, '支撑文件/00_推进记录.md'), encoding='utf-8').read()
blk = rep[rep.find('你自己查的'):]
blk = blk[:blk.find('</table>')]
a = [[re.sub(r'<[^>]+>', '', c).strip() for c in re.findall(r'<td>(.*?)</td>', r)] for r in re.findall(r'<tr>(.*?)</tr>', blk) if '<td>' in r]
zb = z[z.find('**Dk 自查 6 件**'):]  # Q64 起 5 件，Q66 起 6 件
zb = zb[:zb.find('**按推断推进')]
b = [[c.strip() for c in l.strip().strip('|').split('|')] for l in zb.split('\n') if re.match(r'^\| [①②③④⑤⑥] ', l)]
print('汇报行数', len(a), ' 00 行数', len(b), ' 逐行一致', a == b)
for x, y in zip(a, b):
    if x != y:
        print('不一致：', x, y)
for f, t in [('环节1_现状盘点.html', '盘点记载的时机都已被占用'), ('分析/A13_八月离开的用户.md', '因近期不活跃没升上去')]:
    s = open(os.path.join(B, f), encoding='utf-8').read()
    for m in re.finditer(t, s):
        print(f, t, '…' + s[max(0, m.start() - 40):m.end() + 20].replace('\n', ' ') + '…')
    print(f, t, '出现', s.count(t))
