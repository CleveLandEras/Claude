import re, os
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
files = ['02_弹窗分人群定制方案_迭代稿.html', 'claude_弹窗标签推送_盘点.html', 'C2_新标签脚本草稿.md', '09_取数需求_上线前基线.xlsx']
pats = ['ID11', 'ID10', '衰退']
for f in files[:3]:
    txt = open(base + f, encoding='utf-8').read()
    txt = re.sub(r'<[^>]+>', ' ', txt)
    txt = re.sub(r'\s+', ' ', txt)
    print('=====', f)
    for p in pats:
        for m in re.finditer(p, txt):
            s = max(0, m.start() - 120); e = min(len(txt), m.end() + 160)
            print('[' + p + ']', txt[s:e])
            print('--')
