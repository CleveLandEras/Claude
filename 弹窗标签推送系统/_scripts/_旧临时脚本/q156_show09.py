import openpyxl
P = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/09_取数需求_上线前基线.xlsx'
wb = openpyxl.load_workbook(P)
print(wb.sheetnames)
for n in wb.sheetnames:
    if n.startswith(('表1 ', '表2 ', '表3 ', '表6', '表7', '表15', '表1_', '表2_', '表3_')) or n.split(' ')[0] in ('表1', '表2', '表3', '表6', '表7', '表15'):
        ws = wb[n]
        print('=====', n, ws.max_row, ws.max_column)
        for row in ws.iter_rows():
            for c in row:
                if c.value is not None:
                    print(c.coordinate, repr(c.value)[:200])
