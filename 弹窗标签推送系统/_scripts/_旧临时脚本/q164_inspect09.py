"""Q164：只读，列出 09 中人均金额类表（表2、3、9、13、14、16）的结构，用来核对有没有「人数、截尾后合计、截尾后标准差、截尾值」。不改文件。"""
import openpyxl

P = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/09_取数需求_上线前基线.xlsx'
wb = openpyxl.load_workbook(P)
for name in wb.sheetnames:
    if name.split(' ')[0] not in ('表2', '表3', '表9', '表13', '表14'):
        continue
    ws = wb[name]
    print('=' * 60)
    print(name, ws.max_row, 'x', ws.max_column)
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
        vals = [(str(c.value)[:70] if c.value is not None else '') for c in row[:12]]
        if any(vals):
            print(row[0].row, ' | '.join(vals))
    print('合并单元格:', list(ws.merged_cells.ranges)[:10])
