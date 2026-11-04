"""Q112 定位：在环节3、A26、A28、A31、02、03 中列出「12 → 32」「增到 32」「12 → 30」的全部命中（只读）。"""
import os
import openpyxl
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
files = ['环节3_方案.html', '分析/A26_方案池.md', '分析/A28_标签取舍.md', '分析/A31_决策点选项.md',
         '支撑文件/02_弹窗分人群定制方案.html']
terms = ['12 → 32', '增到 32', '12 → 30', '每天多弹 20', '每日多弹 20']
for f in files:
    p = os.path.join(BASE, f)
    lines = open(p, encoding='utf-8').read().split('\n')
    print('=' * 50, f, '共', len(lines), '行')
    for t in terms:
        for i, l in enumerate(lines, 1):
            j = l.find(t)
            while j != -1:
                print(f'  [{t}] L{i} c{j}: …{l[max(0, j-110):j+len(t)+50]}…')
                j = l.find(t, j + len(t))
p = os.path.join(BASE, '支撑文件/03_弹窗配置单.xlsx')
wb = openpyxl.load_workbook(p)
print('=' * 50, '03 sheets:', wb.sheetnames)
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            v = c.value
            if isinstance(v, str) and any(t in v for t in terms):
                print(f'  [{ws.title}!{c.coordinate}] {v}')
