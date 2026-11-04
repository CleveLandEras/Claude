import openpyxl, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
wb = openpyxl.load_workbook(BASE + '支撑文件/03_弹窗配置单.xlsx')
print(wb.sheetnames)
ws = wb['最终规则全表']
print('I5:', repr(ws['I5'].value)[:900])
print(ws['I5'].font.sz, ws['I5'].alignment.wrap_text)
for name in wb.sheetnames:
    if '更正' in name:
        w = wb[name]
        print(name, w.max_row, w.max_column)
        for r in range(1, 4):
            print([str(c.value)[:60] for c in w[r]])
        for r in range(w.max_row - 2, w.max_row + 1):
            print(r, [str(c.value)[:120] for c in w[r]])
        print([ (c.coordinate, c.font.sz, c.alignment.wrap_text, c.alignment.vertical, c.border.left.style) for c in w[w.max_row]])
        print({k: v.width for k, v in w.column_dimensions.items()}, w.row_dimensions[w.max_row].height)

h = open(BASE + '环节3_方案.html', encoding='utf-8').read()
i = h.find('<tr><td>42</td>')
print(i, repr(h[i:i + 1500]))

files = ['支撑文件/02_弹窗分人群定制方案.html', '决策汇报.html', '环节3_方案.html']
for f in files:
    t = open(BASE + f, encoding='utf-8').read()
    for m in re.finditer(r'ID5、ID6 各项', t):
        print(f, m.start(), repr(t[max(0, m.start() - 60):m.start() + 80]))
for f in ['支撑文件/03_弹窗配置单.xlsx']:
    for w in wb.worksheets:
        for row in w.iter_rows():
            for c in row:
                if isinstance(c.value, str) and 'ID5、ID6 各项' in c.value:
                    print(w.title, c.coordinate, c.value[:200])
