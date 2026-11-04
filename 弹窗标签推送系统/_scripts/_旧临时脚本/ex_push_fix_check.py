"""问题 9 更正版回归：交付文件里「没有手机推送」「从零建设」「没有站外推送」等误读残留的上下文。只读。"""
import html, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
FILES = ['决策汇报.html', '环节1_现状盘点.html', '分析/A9_登录平台分布.md', '分析/A13_八月离开的用户.md', '支撑文件/00_推进记录.md', '过程记录/设计卡.md']
KEYS = ['没有手机推送', '从零建', '没有站外推送', '没有推送能力', '没有真正的推送', '都触达不到', '将来新建推送', '前提不成立', '来源冲突', '9-2、9-3 作废', '问题 24']
for f in FILES:
    t = re.sub('<[^>]+>', '', html.unescape(open(BASE + f, encoding='utf-8').read()))
    for k in KEYS:
        for m in re.finditer(re.escape(k), t):
            print(f'[{f}] {k}: …{t[max(0, m.start() - 60):m.end() + 25]}…'.replace('\n', ' '))
