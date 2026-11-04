"""审查 R139：03 规则表第 12 行 G、K 列的价格区间从最低一格写起（约 74 元以下 / 74–160 / 160–300 / 300–690），并在「更正记录」表追加一行；顺带把更正记录第 6 行 D 列的「约 75 元」校正为「约 74 元」。不带参数运行；可重复运行。"""
import os
from copy import copy
import openpyxl
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '支撑文件', '03_弹窗配置单.xlsx')
wb = openpyxl.load_workbook(p)
ws = wb['规则']
wc = wb['更正记录']
changed = []

g_old = '约 160–300 元：卡 3–4 / 卡 5–7（低于约 160 元时卡 4 也偏低）；300–690 元：卡 3–5 / 卡 6–7'
g_new = '约 160 元以下：卡 3 / 卡 4–7（约 74 元以下四档都偏低，仍按 8.7 倍分两档）；约 160–300 元：卡 3–4 / 卡 5–7；300–690 元：卡 3–5 / 卡 6–7'
g = ws['G12'].value or ''
if g_old in g:
    ws['G12'].value = g.replace(g_old, g_new); changed.append('G12')

k_old = '约 160–300 元对卡 5–7 有依据（上界 1,827 人、55%；低于约 160 元时卡 4 也有，约 74 元以下四档都有）'
k_new = '约 74 元以下四档都有依据（上界 5,146 人、100%）；74–160 元对卡 4–7（上界 3,446 人、84%）；160–300 元对卡 5–7（上界 1,827 人、55%）'
k = ws['K12'].value or ''
if k_old in k:
    ws['K12'].value = k.replace(k_old, k_new); changed.append('K12')

for r in range(1, wc.max_row + 1):
    for c in range(1, 6):
        cc = wc.cell(r, c)
        if isinstance(cc.value, str) and '约 75 元以下' in cc.value:
            cc.value = cc.value.replace('约 75 元以下', '约 74 元以下'); changed.append(f'更正记录 {cc.coordinate} 校正 74')

if not any((wc.cell(r, 5).value or '').startswith('审查 R139') for r in range(1, wc.max_row + 1)):
    r = wc.max_row + 1
    vals = ['2026-09-29', '规则表第 12 行（序号 8）G、K 列',
            'G：「约 160–300 元：卡 3–4 / 卡 5–7（低于约 160 元时卡 4 也偏低）」；K：「约 160–300 元对卡 5–7 有依据（…；低于约 160 元时卡 4 也有，约 74 元以下四档都有）」：区间没从最低一格写起，74–160 元无人数，G 列没有 160 元以下的切法；现首储礼包 NT$50 就在 74 元以下',
            'G：「约 160 元以下：卡 3 / 卡 4–7（约 74 元以下四档都偏低，仍按 8.7 倍分两档）；约 160–300 元：卡 3–4 / 卡 5–7；300–690 元：卡 3–5 / 卡 6–7」；K：「约 74 元以下四档都有依据（5,146 人、100%）；74–160 元对卡 4–7（3,446 人、84%）；160–300 元对卡 5–7（1,827 人、55%）」',
            '审查 R139；A30 表 2（卡 3 P25 = 74.3、卡 4 P25 = 159.7）、表 4、表 5']
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
