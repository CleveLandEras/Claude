import openpyxl
wb = openpyxl.load_workbook('/Users/decheng.huang/claude/弹窗标签推送系统/09_取数需求_上线前基线.xlsx')
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and ('月初' in c.value or '误圈' in c.value):
                print(ws.title, c.coordinate, c.value)
for p in ['C2_新标签脚本草稿.md', '02_弹窗分人群定制方案_迭代稿.html']:
    t = open('/Users/decheng.huang/claude/弹窗标签推送系统/' + p, encoding='utf-8').read()
    for line in t.splitlines():
        if '月初' in line or '误圈' in line:
            print(p, '|', line.strip()[:300])
