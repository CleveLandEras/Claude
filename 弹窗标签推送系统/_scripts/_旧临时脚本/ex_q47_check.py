"""Q47 核对：R60 相关措辞在交付文件正文的残留（上下文，判断是否只在更正括注）。只读。"""
import html, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
FILES = ['决策汇报.html', '环节1_现状盘点.html', '分析/A1_用户价值结构.md', '分析/A9_登录平台分布.md', '分析/A11_会员等级.md']
KEYS = ['从不押注', '确实没有押注', '个个大额', '待问题 24', '待问题 25 d', '待确认（问题 24', '只储值不押注', '按推断单列']
for f in FILES:
    t = re.sub('<[^>]+>', '', html.unescape(open(BASE + f, encoding='utf-8').read()))
    for k in KEYS:
        for m in re.finditer(re.escape(k), t):
            print(f'[{f}] {k}: …{t[max(0, m.start() - 45):m.end() + 25]}…'.replace('\n', ' '))
