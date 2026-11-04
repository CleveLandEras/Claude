"""Q164 修复：q164_fix09.py 第一次运行时，表9 的表头按文字查找，误落在第 4 行（说明行，合并格 B4:D4），
把三列表头与黄格写到了 E4:G11。本脚本清掉 表9 E–G 列（第 1 行起）的值、底色、边框，再把三列正确写在表头行（第 7 行）与数据行（第 8–11 行）。
不带参数；可重复运行；不改其他表。"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

P = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/09_取数需求_上线前基线.xlsx'
wb = openpyxl.load_workbook(P)
ws = wb['表9 储值类主指标基线']

F = Font(name="微软雅黑", size=12)
FB = Font(name="微软雅黑", size=12, bold=True)
YELLOW = PatternFill("solid", fgColor="FFFF99")
GRAY = PatternFill("solid", fgColor="E7E6E6")
thin = Side(style="thin", color="999999")
BD = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical="center")

for r in range(1, ws.max_row + 1):
    for c in (5, 6, 7):
        x = ws.cell(row=r, column=c)
        x.value = None
        x.fill = PatternFill(fill_type=None)
        x.border = Border()
        x.font = Font(name="微软雅黑", size=12)

heads = ['Q164 补：截尾后储值总额（两组合并 P99 截尾）', 'Q164 补：截尾后每人值的标准差', 'Q164 补：P99 截尾值（两组合并；各取数点各一格）']
for j, h in enumerate(heads):
    x = ws.cell(row=7, column=5 + j, value=h)
    x.font, x.fill, x.border, x.alignment = FB, GRAY, BD, WRAP
    ws.column_dimensions[chr(69 + j)].width = 34
for r in range(8, 12):
    for j in range(3):
        x = ws.cell(row=r, column=5 + j)
        x.value = None
        x.font, x.fill, x.border, x.alignment = F, YELLOW, BD, WRAP

wb.save(P)
print('表9 已修复')
for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
    vals = [(str(c.value)[:24] if c.value is not None else '') for c in row[:8]]
    if any(vals):
        print(row[0].row, ' | '.join(vals))
