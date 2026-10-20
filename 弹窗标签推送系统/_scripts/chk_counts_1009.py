# 核对阶段 5–8 与呈交版的计数是否统一（34＝12＋12＋10；快速提升 8 条）
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, glob
BASE = _ROOT + '/'
files = ['阶段5_方案选型.html', '阶段6_方案设计.html', '阶段7_方案验证.html', '阶段8_结论汇总.html', '弹窗标签推送方案_V1.html']
terms = ['35 项', '35 个', '短期 13', '配置 13', '13 项', '9 条', '快速提升第 7', '6,064', '高卡', '先看覆盖', '先看能否验证', '互斥方案', '需要 Dk 定', '待 Dk 或上级确认', '8 项缺', '7／10']
for f in files:
    s = open(BASE + f, encoding='utf-8').read()
    print('==', f)
    for t in terms:
        for m in re.finditer(re.escape(t), s):
            a = max(0, m.start() - 28)
            b = min(len(s), m.end() + 28)
            ctx = re.sub(r'<[^>]+>', '', s[a:b]).replace('\n', ' ')
            print('  [%s] …%s…' % (t, ctx))
