import openpyxl

p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/09_取数需求_上线前基线.xlsx'
wb = openpyxl.load_workbook(p)
ws = wb['更正记录']
print('maxrow', ws.max_row, 'maxcol', ws.max_column)
for row in ws.iter_rows(min_row=1, max_row=4):
    for c in row:
        if c.value not in (None, ''):
            print(c.coordinate, ':', str(c.value)[:150])
for row in ws.iter_rows(min_row=ws.max_row - 2, max_row=ws.max_row):
    for c in row:
        if c.value not in (None, ''):
            print(c.coordinate, ':', str(c.value)[:400])
for name in ['表2 新增7日留存', '表3 回流7日留存']:
    w = wb[name]
    print(name, 'row4:', [c.value for c in w[4]], 'D6:', w['D6'].value, 'D13:', w['D13'].value)
