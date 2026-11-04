"""审查 R137：改 03 规则表第 12 行 G、K 列的 N1 价格条件句，并在「更正记录」表追加一行。不带参数运行；可重复运行（已改过则不再改）。"""
import os
from copy import copy
import openpyxl
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '支撑文件', '03_弹窗配置单.xlsx')
wb = openpyxl.load_workbook(p)
ws = wb['规则']
changed = []

g_old = '当前卡别金卡以上，按卡别至少分两档（例如卡 3–4、卡 5–7；A30）'
g_new = '当前卡别金卡以上，按卡别至少分两档；切法随独享礼包价格定（300 元以内：卡 3–4 / 卡 5–7；300–690 元：卡 3–5 / 卡 6–7；A30）'
if ws['G12'].value == g_old:
    ws['G12'].value = g_new; changed.append('G12')

k_old = '若储值位第一个礼包在几百元，往上调只对卡 5–7 有依据（A30）。'
k_new = ('往上调有没有依据看储值位第一个礼包的价格：300 元以内只对卡 5–7 有依据（上界 1,827 人、55%），'
         '300–690 元只对卡 6、7（上界 662 人、26%），再高则没有一档判「偏低」（690–1,360 元时卡 6、7 不定），N1 去留交决策点（A30）。')
k = ws['K12'].value or ''
if k_old in k:
    k = k.replace(k_old, k_new)
    k = k.replace('上界约 5,146 人]', '上界约 5,145 人]（共 5,146 人）')
    ws['K12'].value = k; changed.append('K12')

wc = wb['更正记录']
if not any((wc.cell(r, 5).value or '').startswith('审查 R137') for r in range(1, wc.max_row + 1)):
    r = wc.max_row + 1
    vals = ['2026-09-29', '规则表第 12 行（序号 8）G、K 列',
            'G：「例如卡 3–4、卡 5–7」；K：「若储值位第一个礼包在几百元，往上调只对卡 5–7 有依据」「上界约 5,146 人」：卡 5 门槛 300.2 元贴着锚点 300，300 元以上只剩卡 6、7；示例切法只在 300 元以内对得上',
            'G：切法随价格定（300 元以内卡 3–4 / 卡 5–7；300–690 元卡 3–5 / 卡 6–7）；K：按门槛区间写（300 元以内卡 5–7、300–690 元卡 6、7、再高没有一档偏低），N1 去留交决策点；上界约 5,145 人（共 5,146 人）',
            '审查 R137；A30 表 2、表 5']
    for c, v in enumerate(vals, 1):
        cell = wc.cell(r, c, v)
        src = wc.cell(r - 1, c)
        if src.has_style:
            cell._style = copy(src._style)
    changed.append(f'更正记录第 {r} 行')

wb.save(p)
print('已改：', changed or '无（已是新写法）')
print('G12 =', ws['G12'].value)
print('K12 =', ws['K12'].value)
