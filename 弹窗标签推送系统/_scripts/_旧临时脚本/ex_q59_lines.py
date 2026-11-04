import re
# 列出交付物中含关键词的行号（只读），供 Q59/Q60 定位与收尾核对
ROOT = '/Users/decheng.huang/claude/弹窗标签推送系统/'
FILES = ['环节1_现状盘点.html', '决策汇报.html', '分析/A8_卡别与最后登录.md', '分析/A11_会员等级.md',
         '分析/A3_回流与潜在付费画像.md', '分析/A13_八月离开的用户.md', '支撑文件/00_推进记录.md']
TERMS = ['副产品', '没有会员等级', '升卡门槛', '近两个月', '某两个月', '既有资料 ②', '卡别怎么升',
         '以既有资料为准', '触发时机', '当天不再弹', '约 100 个', '自查 ④', '身份（国家）', '标签群组']
for f in FILES:
    with open(ROOT + f, encoding='utf-8') as fh:
        lines = fh.read().split('\n')
    for i, ln in enumerate(lines, 1):
        for t in TERMS:
            for m in re.finditer(re.escape(t), ln):
                s = max(0, m.start() - 40)
                e = min(len(ln), m.end() + 40)
                seg = ln[s:e]
                # 标出是否位于更正括注附近（前 60 字内含「原写」「更正」）
                ctx = ln[max(0, m.start() - 60):m.start()]
                flag = '括注?' if ('原写' in ctx or '更正' in ctx) else '★'
                print(f'{f}:{i} [{t}] {flag} …{seg}…')
