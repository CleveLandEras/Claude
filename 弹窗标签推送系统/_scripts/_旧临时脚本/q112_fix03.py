"""推进计划 Q112（审查 R149）：03 规则表第 10 行 K 列、更正记录第 4 行 D 列的「每日活动类 12 → 32」改为「每日活动类弹窗上限 12 → 32」，并在「更正记录」表追加一行。不带参数运行；可重复运行。"""
import os
from copy import copy
import openpyxl
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '支撑文件', '03_弹窗配置单.xlsx')
wb = openpyxl.load_workbook(p)
ws = wb['规则']
wc = wb['更正记录']
changed = []

old = '每日活动类 12 → 32'
new_k = '每日活动类弹窗上限 12 → 32（要一天进大厅约 20 次才会碰到，按配置推算）'
new_d = '每日活动类弹窗上限 12 → 32'
k = ws['K10'].value or ''
if old in k:
    ws['K10'].value = k.replace(old, new_k); changed.append('K10')
d = wc['D4'].value or ''
if old in d:
    wc['D4'].value = d.replace(old, new_d); changed.append('更正记录 D4')

if not any('Q112' in str(wc.cell(r, 5).value or '') for r in range(1, wc.max_row + 1)):
    r = wc.max_row + 1
    vals = ['2026-09-29', '规则表第 10 行（ID10）K 列；本表第 4 行 D 列',
            '「按现写法金卡以上储值衰退者每日活动类 12 → 32」：两个数都是按配置推出的每天上限（多出的 20 个要一天进大厅约 20 次才碰到），读起来像每天实际弹出数',
            '「每日活动类弹窗上限 12 → 32（要一天进大厅约 20 次才会碰到，按配置推算）」；须改的判断不变',
            '审查 R149；推进计划 Q112；A21']
    for c, v in enumerate(vals, 1):
        cell = wc.cell(r, c, v)
        src = wc.cell(r - 1, c)
        if src.has_style:
            cell._style = copy(src._style)
    changed.append(f'更正记录第 {r} 行')

wb.save(p)
print('已改：', changed or '无（已是新写法）')
print('K10 =', ws['K10'].value)
print('D4 =', wc['D4'].value)
