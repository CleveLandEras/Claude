"""Q91：03 弹窗配置单按 A26、A28、A30 重核。只改「规则」表：加 K 列「去留（A26）」，新增 N1 行；加「更正记录」表。
不改原有各列内容。重复运行安全：K 列表头已存在时不再追加 N1 行。不带参数。"""
import os
from copy import copy

from openpyxl import load_workbook

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(BASE, '支撑文件', '03_弹窗配置单.xlsx')
wb = load_workbook(P)
ws = wb['规则']


def like(src, dst, value):
    dst.value = value
    dst.font = copy(src.font)
    dst.border = copy(src.border)
    dst.alignment = copy(src.alignment)
    dst.fill = copy(src.fill)
    dst.number_format = src.number_format


if ws['K4'].value != '去留（A26）':
    like(ws['J4'], ws['K4'], '去留（A26）')
    KV = {
        5: '随他项：只在回流付费内容（N3）或回流规则上线时做；本身不改变任何人看到的内容',
        6: '降级：服务新增只来当天，链上靠后，不进首期',
        7: '降级：服务回流又走，链上末位，不进首期',
        8: '不变；与新增第 12 行同时命中时要给本规则加排除（见第 12 行）',
        9: '降级：方向取决于破产礼包与独享礼包价格（待确认），先维持现序',
        10: '改（主线）：按现写法金卡以上储值衰退者每日活动类 12 → 32，须改为每日弹出不高于现状、内容换成与高卡储值相关的（次数与内容由运营定）。标签「当月储值额小于上月 50%」按自然月还是滚动比较，待自查 ③（A28 第 5 行）',
        11: '随第 6 行（改）：第 6 行不上线时不停用，否则银卡失去覆盖',
    }
    for r, v in KV.items():
        like(ws[f'J{r}'], ws[f'K{r}'], v)
    # 新增 N1 行（第 12 行）
    src = 6
    vals = {'A': 8, 'B': '新建', 'C': None, 'D': '储值类', 'E': '在场高卡储值弹窗（N1）', 'F': '大厅',
            'G': '当前卡别金卡以上，按卡别至少分两档（例如卡 3–4、卡 5–7；A30）', 'H': None, 'I': 1,
            'J': '储值位放与该档付费档位相称的礼包（具体礼包由运营定）；同时第 4 行 ID6 对象改为普卡、银卡两条规则，避免同时命中多弹 1 个',
            'K': '新增（主线）：N1 判「新增」依赖对规则 4 的一处解读，按字面会降级（审查 R128，待设计者裁定）；前提本地只能给 [确定 25 人, 上界约 5,146 人]；若储值位第一个礼包在几百元，往上调只对卡 5–7 有依据（A30）。当前卡别有没有能圈出金卡以上的标签，待自查 ③（A28 第 3 行）'}
    for col, v in vals.items():
        like(ws[f'{col}{src}'], ws[f'{col}12'], v)
    ws.column_dimensions['K'].width = max(ws.column_dimensions['J'].width or 30, 48)
    ws['A2'].value = (ws['A2'].value or '') + '　（2026-09-29 按 A26 重核：K 列为去留；第 8 行 N1 为新增；原各列未改，见「更正记录」表）'

if '更正记录' not in wb.sheetnames:
    c = wb.create_sheet('更正记录')
    head = ws['A4']
    rows = [('日期', '所在处', '原写', '现写', '依据'),
            ('2026-09-29', '规则表 K 列', '无去留列', '新增「去留（A26）」列，逐行写去留与理由', 'A26 表 1；推进计划 Q91'),
            ('2026-09-29', '规则表第 12 行（序号 8）', '无', '新增 N1 在场高卡储值弹窗（按卡别至少分两档），附规则 4 解读与前提上下界的披露', 'A26 N1；A30；审查 R128'),
            ('2026-09-29', '规则表第 10 行（ID10）K 列', '—（原改动说明只写「对象去除普卡限定」）', '注明按现写法金卡以上每日活动类 12 → 32 须改，标签口径待自查 ③', 'A21；A26 P4；A28 第 5 行')]
    for i, rv in enumerate(rows, 1):
        for j, v in enumerate(rv, 1):
            cell = c.cell(row=i, column=j, value=v)
            cell.font = copy(head.font)
            cell.alignment = copy(ws['J5'].alignment)
            cell.border = copy(head.border)
    for col, w in zip('ABCDE', (14, 24, 36, 60, 28)):
        c.column_dimensions[col].width = w

wb.save(P)
wb2 = load_workbook(P)
s = wb2['规则']
print('规则表行列', s.max_row, s.max_column)
for r in range(4, s.max_row + 1):
    print(r, s[f'A{r}'].value, s[f'B{r}'].value, s[f'E{r}'].value, '｜K:', (s[f'K{r}'].value or '')[:60])
print('工作表', wb2.sheetnames)
