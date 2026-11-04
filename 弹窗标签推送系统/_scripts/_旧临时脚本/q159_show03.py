import openpyxl
P = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(P)
print(wb.sheetnames)
ws = wb['规则']
for r in range(5, 9):
    for col in 'BEGJKL':
        v = ws[col + str(r)].value
        if v is not None:
            print(col + str(r), repr(v))
for n in wb.sheetnames:
    if '更正' in n:
        w = wb[n]
        print('==', n, w.max_row, w.max_column)
        for r in range(max(1, w.max_row - 1), w.max_row + 1):
            for c in range(1, w.max_column + 1):
                v = w.cell(r, c).value
                if v is not None:
                    print(r, c, repr(v)[:200])
