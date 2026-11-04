"""Q46 定位：汇报、环节1、A11、A12 中关键词的上下文。只读。"""
import html, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
FILES = ['决策汇报.html', '环节1_现状盘点.html', '分析/A11_会员等级.md', '分析/A12_活动赠点与新增参与.md']
KEYS = ['25 d', '问题 7', '9-2', '问题 24', 'VIP 名单', '问题 25']
for f in FILES:
    t = re.sub('<[^>]+>', '', html.unescape(open(BASE + f, encoding='utf-8').read()))
    for k in KEYS:
        for m in re.finditer(re.escape(k), t):
            print(f'[{f}] {k}: …{t[max(0, m.start() - 50):m.end() + 30]}…'.replace('\n', ' '))
