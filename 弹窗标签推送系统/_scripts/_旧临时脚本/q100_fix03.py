"""推进计划 Q100：03 规则表第 12 行 G、K 列的「300 元以内」补上约 160 元以下一格，并在「更正记录」表追加一行。不带参数运行；可重复运行（已改过则不再改）。"""
import os
from copy import copy
import openpyxl
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '支撑文件', '03_弹窗配置单.xlsx')
wb = openpyxl.load_workbook(p)
ws = wb['规则']
changed = []

g_old = '300 元以内：卡 3–4 / 卡 5–7；300–690 元：卡 3–5 / 卡 6–7'
g_new = '约 160–300 元：卡 3–4 / 卡 5–7（低于约 160 元时卡 4 也偏低）；300–690 元：卡 3–5 / 卡 6–7'
g = ws['G12'].value or ''
if g_old in g:
    ws['G12'].value = g.replace(g_old, g_new); changed.append('G12')

k_fix = ('约 75 元以下四档都有', '约 74 元以下四档都有')  # 卡 3 P25 = 74.3，第二次运行时校正
if k_fix[0] in (ws['K12'].value or ''):
    ws['K12'].value = ws['K12'].value.replace(*k_fix); changed.append('K12 校正 74')
for r in range(1, wb['更正记录'].max_row + 1):
    cc = wb['更正记录'].cell(r, 3)
    if cc.value and '约 75 元以下' in cc.value:
        cc.value = cc.value.replace('约 75 元以下', '约 74 元以下'); changed.append(f'更正记录第 {r} 行校正 74')
k_old = '300 元以内只对卡 5–7 有依据（上界 1,827 人、55%）'
k_new = '约 160–300 元对卡 5–7 有依据（上界 1,827 人、55%；低于约 160 元时卡 4 也有，约 75 元以下四档都有）'
k = ws['K12'].value or ''
if k_old in k:
    ws['K12'].value = k.replace(k_old, k_new); changed.append('K12')

wc = wb['更正记录']
if not any((wc.cell(r, 5).value or '').startswith('推进计划 Q100') for r in range(1, wc.max_row + 1)):
    r = wc.max_row + 1
    vals = ['2026-09-29', '规则表第 12 行（序号 8）G、K 列',
            'G：「300 元以内：卡 3–4 / 卡 5–7」；K：「300 元以内只对卡 5–7 有依据」：低于约 160 元时卡 4 也判偏低（卡 4 P25 = 159.7 元），约 75 元以下四档都偏低，「只对」不成立',
            'G：「约 160–300 元：卡 3–4 / 卡 5–7（低于约 160 元时卡 4 也偏低）」；K：「约 160–300 元对卡 5–7 有依据（…；低于约 160 元时卡 4 也有，约 75 元以下四档都有）」',
            '推进计划 Q100；口径约束 64；A30 表 2、表 4']
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
