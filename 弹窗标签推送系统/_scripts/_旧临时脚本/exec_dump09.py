"""执行者用：只把 09 取数表转成文本输出（含每张表的全部单元格与黄格标记）。只读，不带参数。"""
import os
from openpyxl import load_workbook
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '支撑文件', '09_取数需求_上线前基线.xlsx')
wb = load_workbook(p)
for s in wb.worksheets:
    print('=' * 50, s.title, s.max_row, 'x', s.max_column)
    for row in s.iter_rows():
        vals = []
        for c in row:
            if c.value is not None or (c.fill and c.fill.fgColor and c.fill.fgColor.rgb in ('00FFFF99', 'FFFFFF99')):
                y = '[黄]' if c.fill.fgColor.rgb in ('00FFFF99', 'FFFFFF99') else ''
                vals.append(f'{c.coordinate}{y}={c.value}')
        if vals:
            print('  ' + ' | '.join(vals))
