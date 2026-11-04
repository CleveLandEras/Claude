# 只读：在决策汇报、环节3、A36、08 里找旧合同残留写法
import re, html
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
def text_lines(path):
    s = open(path, encoding='utf-8').read()
    if path.endswith('.html'):
        s = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.S)
        s = re.sub(r'<br\s*/?>', '\n', s)
        s = re.sub(r'</(p|div|li|tr|h\d|td|th|summary|section|table)>', '\n', s)
        s = re.sub(r'<[^>]+>', '', s)
        s = html.unescape(s)
    return [l.strip() for l in s.split('\n') if l.strip()]
KEYS = ['有人买', '几乎没人买', '护栏：M7', '÷ 曝光', '÷ 破产位曝光', '兼护栏', '兼按护栏', '同时是护栏', '95% 判', '每期以 95%']
for f in ['决策汇报.html', '环节3_方案.html', '分析/A36_验证计划.md', '支撑文件/08_弹窗效果评估方案.md', '支撑文件/02_弹窗分人群定制方案.html']:
    L = text_lines(BASE + f)
    print('=' * 60, f)
    for i, l in enumerate(L):
        hit = [k for k in KEYS if k in l]
        if hit:
            print(i, hit, '|', l[:500])
