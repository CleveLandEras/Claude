"""Q49 / R65 回归：交付文件里「236」的上下文；复算基线扣除。只读。"""
import html, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['决策汇报.html', '环节1_现状盘点.html', '分析/A13_八月离开的用户.md']:
    t = re.sub('<[^>]+>', '', html.unescape(open(BASE + f, encoding='utf-8').read()))
    for m in re.finditer('236', t):
        print(f'[{f}] …{t[max(0, m.start() - 70):m.end() + 30]}…'.replace('\n', ' '))
n = 12015
for name, hit, den in [('15–31', 53, 17523), ('8–14', 40, 9649)]:
    r = hit / den
    print(name, f'基线 {r*100:.3f}%', f'应有 {n*r:.1f}', f'超出 {63 - n*r:.1f}')
