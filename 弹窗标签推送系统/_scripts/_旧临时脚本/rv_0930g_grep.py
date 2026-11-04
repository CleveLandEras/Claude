# 审查 2026-09-30：在现行文件纯文本里检索关键说法并打印上下文（只读，不写文件）
import re
R = '/Users/decheng.huang/claude/弹窗标签推送系统/'
FILES = ['决策汇报.html', '环节2_问题诊断.html', '环节3_方案.html', '支撑文件/02_弹窗分人群定制方案.html',
         '支撑文件/05_标签需求.md', '支撑文件/07_推送需求.md', '支撑文件/04_弹窗功能缺口需求.md', '支撑文件/08_弹窗效果评估方案.md',
         '分析/A34_大户落位与缺席大户.md', '分析/A35_赠点规模与02成本影响.md', '分析/A32_问题空间扫描.md']
TERMS = ['原样转发', '可以转发', '可转发', '可交研发', '可交数据组', '可以上线', '今天就能发', '可以直接交',
         '9.4', '1.27%', '押注相同', '25 人买过', '几乎没有确定', '看不到', '次线', '主线推荐', '第 2 位参与']
def text(p):
    s = open(R + p, encoding='utf-8').read()
    if p.endswith('.html'):
        s = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', s, flags=re.S)
        s = re.sub(r'<[^>]+>', ' ', s)
        s = re.sub(r'&nbsp;', ' ', s)
    return re.sub(r'\s+', ' ', s)
for f in FILES:
    t = text(f)
    for w in TERMS:
        for m in re.finditer(re.escape(w), t):
            a = max(0, m.start() - 70); b = min(len(t), m.end() + 50)
            print(f'[{f}]〈{w}〉…{t[a:b]}…')
