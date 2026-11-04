# 只读检索：09 与本机 md/html 中与快照、身份相关的文字
import glob, os
import openpyxl

base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
wb = openpyxl.load_workbook(base + '09_取数需求_上线前基线.xlsx')
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and ('快照' in c.value or '名单来源' in c.value):
                print('09', ws.title, c.coordinate, c.value)

for p in glob.glob(base + '*.md') + glob.glob(base + '02_*迭代稿.html'):
    name = os.path.basename(p)
    if name in ('迭代记录.md', '任务清单.md', '监督记录.md'):
        continue
    with open(p, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if ('月末' in line and '快照' in line) or 'snapshot_month' in line or '身份的字段类型' in line:
                print(name, i, line.strip()[:200])
