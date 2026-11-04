"""Q142：03 提案工作表风险句「本地只能确定 25 人买过，上界约 5,146 人」方向写反，按 A30 表 1 改正，并在「更正记录」追加一行。不带参数运行；可重复运行。"""
import os
from copy import copy
import openpyxl
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '支撑文件', '03_弹窗配置单.xlsx')
wb = openpyxl.load_workbook(p)
old = '本地只能确定 25 人买过，上界约 5,146 人'
new = '本地只能确定没买过首储（储值位先看到 NT$50）的 25 人，确定买过的 1 人，上界约 5,145 人（共 5,146 人）'
changed = []
for ws in wb.worksheets:
    if ws.title == '更正记录':
        continue
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and old in c.value:
                c.value = c.value.replace(old, new)
                changed.append(f'{ws.title}!{c.coordinate}')
wc = wb['更正记录']
if changed and not any((wc.cell(r, 5).value or '').startswith('Q142') for r in range(1, wc.max_row + 1)):
    r = wc.max_row + 1
    vals = ['2026-09-30', '提案工作表 风险（B12 一行）',
            '「本地只能确定 25 人买过，上界约 5,146 人」：方向写反',
            '「本地只能确定没买过首储（储值位先看到 NT$50）的 25 人，确定买过的 1 人，上界约 5,145 人（共 5,146 人）」',
            'Q142；A30 表 1（5,145 = 5,146 − 确定买过的 1 人；5,146 是高卡去大户总数）']
    for cidx, v in enumerate(vals, 1):
        cell = wc.cell(r, cidx, v)
        src = wc.cell(r - 1, cidx)
        if src.has_style:
            cell._style = copy(src._style)
    changed.append(f'更正记录第 {r} 行')
wb.save(p)
print('已改：', changed or '无')
