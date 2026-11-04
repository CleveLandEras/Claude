import openpyxl

p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(p)
print(wb.sheetnames)
for ws in wb.worksheets:
    print('==', ws.title, ws.dimensions, 'zoom', ws.sheet_view.zoomScale, 'freeze', ws.freeze_panes)
    print(' widths', {k: round(v.width, 1) for k, v in ws.column_dimensions.items()})
    for addr in ['A1', 'A2', 'A4', 'B4', 'A5', 'G5', 'K5', 'L5']:
        c = ws[addr]
        print(' ', addr, c.font.name, c.font.sz, c.font.b, c.fill.fgColor.rgb if c.fill and c.fill.fill_type else None,
              c.alignment.wrap_text, c.alignment.vertical, c.border.left.style)
    print(' merged', ws.merged_cells.ranges)
    print(' row heights', {k: v.height for k, v in list(ws.row_dimensions.items())[:6]})
