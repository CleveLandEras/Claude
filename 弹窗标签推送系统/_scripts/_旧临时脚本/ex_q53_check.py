"""Q53 核对：旧卡别读法词只允许出现在「原写 / 更正」括注里。列出不在括注语境里的命中（★）。只读，不带参数。"""
import os, re
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ['决策汇报.html', '环节1_现状盘点.html', '分析/A8_卡别与最后登录.md', '分析/A11_会员等级.md',
         '分析/A3_回流与潜在付费画像.md', '分析/A13_八月离开的用户.md']
TERMS = ['跟储值走', '卡别主要按储值', '问题 25 c', '问题 25 d', '升卡门槛', '门槛之一', '不是只按累计值评', '卡别怎么升降', '玩得多才升卡']
for f in FILES:
    s = re.sub(r'<[^>]+>', '', open(os.path.join(B, f), encoding='utf-8').read())
    flagged = 0
    for t in TERMS:
        for m in re.finditer(re.escape(t), s):
            pre = s[max(0, m.start() - 200):m.start()]
            # 括注语境：前文最近的「原写 / 原 / 更正 / 原并入 / 原问题」之后没有闭合「）」
            k = max(pre.rfind('原写'), pre.rfind('原「'), pre.rfind('原并入'), pre.rfind('原问题'), pre.rfind('原标题'), pre.rfind('原判断'))
            inside = k != -1 and pre[k:].count('）') == 0
            if not inside:
                flagged += 1
                print(f'★ [{f}] {t}：…' + s[max(0, m.start() - 60):m.end() + 40].replace('\n', ' ') + '…')
    print(f'[{f}] 正文命中 {flagged}')
