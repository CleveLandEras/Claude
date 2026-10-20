"""把交付物转成可比对的纯文本。供 review_diff.py、mark_reviewed.py、dump_xlsx.py 共用。"""
import os, re, html, glob
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUDE = {'claude_弹窗标签推送_盘点.html', '任务清单.md', '目标脑图.md', '监督记录.md',
           '迭代记录.md', '审查记录.md', '晨间验收.html', '02_弹窗分人群定制方案_Cowork原版.html', '汇报_成果与待你回答.html', '工作原则.md'}

def deliverables():
    out = []
    main = os.path.join(BASE, '决策汇报.html')
    if os.path.exists(main):
        out.append(main)
    out += sorted(glob.glob(os.path.join(BASE, '环节*.html')))
    out += sorted(glob.glob(os.path.join(BASE, '阶段[0-9]*.html')))
    sub = os.path.join(BASE, '弹窗标签推送方案_V1.html')   # 呈交版，Dk 10/9 同意写入阶段产出规划表
    if os.path.exists(sub):
        out.append(sub)
    for p in sorted(glob.glob(os.path.join(BASE, '支撑文件', '*'))):
        n = os.path.basename(p)
        if n in EXCLUDE or not os.path.isfile(p):
            continue
        if re.match(r'^(\d\d_|C\d+_)', n) and n.endswith(('.md', '.html', '.xlsx')):
            out.append(p)
    out += sorted(glob.glob(os.path.join(BASE, '分析', '*.md')))
    return out

def textify(p):
    if p.endswith('.xlsx'):
        import openpyxl
        wb = openpyxl.load_workbook(p)
        lines = []
        for ws in wb:
            lines.append(f'## 工作表 {ws.title}')
            for row in ws.iter_rows():
                for c in row:
                    if c.value is not None:
                        lines.append(f'{c.coordinate}: {c.value}')
        return '\n'.join(lines) + '\n'
    s = open(p, encoding='utf-8').read()
    if p.endswith('.html'):
        s = re.sub(r'<(style|script)\b.*?</\1>', '', s, flags=re.S)
        s = re.sub(r'<(br|/p|/li|/tr|/h\d|/div|/summary|/td|/th|/text)[^>]*>', '\n', s)
        s = re.sub(r'<[^>]+>', '', s)
        s = html.unescape(s)
        s = '\n'.join(l.strip() for l in s.splitlines() if l.strip()) + '\n'
    return s
