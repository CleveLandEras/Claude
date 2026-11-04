import openpyxl

p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/09_取数需求_上线前基线.xlsx'
wb = openpyxl.load_workbook(p)
print(wb.sheetnames)
for name in wb.sheetnames:
    if name.startswith('表16') or name in ('通用口径', '更正记录') or name.startswith('表2 ') or name.startswith('表3 '):
        ws = wb[name]
        print('=' * 30, name, ws.max_row, ws.max_column)
        for row in ws.iter_rows():
            for c in row:
                if c.value not in (None, ''):
                    print(c.coordinate, '|', str(c.value)[:700])
