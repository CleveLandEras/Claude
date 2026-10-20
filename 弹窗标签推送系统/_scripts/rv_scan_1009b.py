import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, os
B = _ROOT + '/'
files = ['阶段1_需求分析.html','阶段5_方案选型.html','阶段6_方案设计.html','阶段7_方案验证.html','阶段8_结论汇总.html','弹窗标签推送方案_V1.html',
         '分析/A65_推荐方案.md','分析/A69_实施分层与短期提升.md','分析/A73_根因验证与边界.md','分析/A74_假设汇总.md','分析/A75_待决事项.md','分析/A68_推送与指标体系.md']
terms = ['购买','35 ','35个','35 项','13 项','短期 13','9 条','第 7 条','高卡误伤','对高卡','互斥在哪','两项取舍','改由统一后台承担','待 Dk 确认','按层推进']
def text(p):
    s = open(B+p, encoding='utf-8').read()
    if p.endswith('.html'):
        s = re.sub(r'<style.*?</style>', '', s, flags=re.S)
        s = re.sub(r'<[^>]+>', ' ', s)
    return s
for f in files:
    if not os.path.exists(B+f):
        print('MISSING', f); continue
    s = text(f)
    for t in terms:
        for m in re.finditer(re.escape(t), s):
            a = max(0, m.start()-40); b = min(len(s), m.end()+40)
            print(f'[{f}] {t} :: ' + re.sub(r'\s+', ' ', s[a:b]))
