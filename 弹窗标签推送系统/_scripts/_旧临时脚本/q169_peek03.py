import openpyxl

p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(p)
wc = wb['更正记录']
print('行数', wc.max_row, '列数', wc.max_column)
for r in (1, 2, wc.max_row - 1, wc.max_row):
    print(r, [str(wc.cell(r, c).value)[:60] for c in range(1, wc.max_column + 1)])
ws = wb['规则']
a2 = ws['A2'].value
i = a2.find('建不了或来不及时')
print(a2[i - 5:i + 90])
j = a2.find('「转全量」')
print(a2[j:])
