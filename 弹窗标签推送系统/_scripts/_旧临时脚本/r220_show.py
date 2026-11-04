# -*- coding: utf-8 -*-
"""R220 只读：打印 03 规则表 5–14 行的 A、E、G、K 全文与更正记录末 3 行。不带参数。"""
import openpyxl
p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(p)
ws = wb['规则']
for r in range(5, 15):
    print('=' * 30, '行', r, 'A=', ws.cell(r, 1).value, '| E=', ws.cell(r, 5).value)
    print('G:', ws.cell(r, 7).value)
    print('K:', ws.cell(r, 11).value)
ws2 = wb['更正记录']
for r in range(max(1, ws2.max_row - 2), ws2.max_row + 1):
    print('更正', r, [ws2.cell(r, c).value for c in range(1, 6)])
