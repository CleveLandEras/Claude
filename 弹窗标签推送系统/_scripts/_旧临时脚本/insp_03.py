"""检视 03 配置单的样式（只读）。不带参数。"""
import openpyxl
p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(p)
for ws in wb.worksheets:
    print('==', ws.title, ws.dimensions, 'merged', ws.merged_cells.ranges, 'freeze', ws.freeze_panes)
    print(' widths', {k: round(v.width, 1) for k, v in ws.column_dimensions.items()})
    print(' heights', {k: v.height for k, v in list(ws.row_dimensions.items())[:14]})
ws = wb['规则']
for r in (1, 2, 4, 5, 6, 8, 12):
    for c in 'AGHJK':
        cell = ws[f'{c}{r}']
        print(r, c, repr(str(cell.value)[:12]), 'fill', cell.fill.fgColor.rgb if cell.fill and cell.fill.fill_type else None,
              'font', cell.font.b, cell.font.sz, cell.font.color.rgb if cell.font.color else None,
              'align', cell.alignment.wrap_text, cell.alignment.vertical, 'border', cell.border.left.style)
ws = wb['排序明细']
for r in (1, 2, 4, 5, 31):
    for c in 'ABCG':
        cell = ws[f'{c}{r}']
        print('排', r, c, repr(str(cell.value)[:12]), 'fill', cell.fill.fgColor.rgb if cell.fill and cell.fill.fill_type else None,
              'font', cell.font.b, cell.font.sz, 'align', cell.alignment.wrap_text, cell.alignment.horizontal)
ws = wb['更正记录']
for r in (1, 2, 9):
    for c in 'ABCDE':
        cell = ws[f'{c}{r}']
        print('更', r, c, 'fill', cell.fill.fgColor.rgb if cell.fill and cell.fill.fill_type else None, 'font', cell.font.b, cell.font.sz, 'wrap', cell.alignment.wrap_text)
print(ws.max_row)
