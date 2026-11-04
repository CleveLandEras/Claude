"""Q148：03 规则表加「对应验证指标」一列（L 列，只填 02 卡号、08 指标、09 表），更正记录追加一行。不带参数运行；可重复运行（不会重复加）。"""
import os
from copy import copy
import openpyxl
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '支撑文件', '03_弹窗配置单.xlsx')
wb = openpyxl.load_workbook(p)
ws = wb['规则']
HEAD = '对应验证指标（02 卡号｜08 指标｜09 表）'
vals = {
    1: '第一张卡｜主指标：M2 新增 7 日留存、M3 回流 7 日留存；过程：M1；护栏：M7｜09 表 1、2、3、8',
    2: '第一张卡｜主指标：M2 新增 7 日留存；护栏：M7｜09 表 2、8',
    3: '第一张卡｜主指标：M3 回流 7 日留存（同时是护栏）；过程：M1；护栏：M7｜09 表 1、3、8',
    4: '第二张卡｜主指标：08 第〇节（被圈入者观察月人均储值）；过程：M4；护栏：M7｜09 表 4、8、11',
    5: '第二张卡｜主指标：08 第〇节（被圈入者观察月人均储值）；过程：M4；护栏：M7｜09 表 4、8、11',
    6: '第二张卡｜主指标：08 第〇节（被圈入者观察月人均储值）；过程：M4；护栏：M7｜09 表 4、8、11',
    7: '第二张卡｜M4 普卡银卡组同期参照（只作参考，不作有效结论）｜09 表 4',
    8: '第二张卡｜M4 普卡银卡组同期参照（只作参考，不作有效结论）｜09 表 4',
    9: '第四张卡｜M6（主指标口径：破产位内全部品项储值金额 ÷ 破产位曝光次数，见 02 第四张卡验证计划）｜09 表 6、7',
}
done = []
if ws['L4'].value != HEAD:
    ws['L4'].value = HEAD
    ws['L4']._style = copy(ws['K4']._style)
    for r in range(5, 14):
        n = ws.cell(r, 1).value
        try:
            n = int(n)
        except Exception:
            continue
        if n in vals:
            c = ws.cell(r, 12, vals[n])
            c._style = copy(ws.cell(r, 11)._style)
    ws.column_dimensions['L'].width = 46
    note = ' 「对应验证指标」列只填 02 卡号、08 指标与 09 表；第三张卡（潜在付费，无新规则）对应 M5、09 表 5；第五张卡（总量，约束性）对应 M7、09 表 8。'
    if isinstance(ws['A2'].value, str) and '对应验证指标' not in ws['A2'].value:
        ws['A2'].value = ws['A2'].value + note
    done.append('规则!L4:L13')
wc = wb['更正记录']
if not any((wc.cell(r, 5).value or '').startswith('Q148') for r in range(1, wc.max_row + 1)):
    r = wc.max_row + 1
    rowvals = ['2026-09-30', '规则表 L 列；A2 说明',
               '无「对应验证指标」列：Dk 验收时看不出每条规则上线后看什么',
               '新增 L 列「对应验证指标」：只填 02 卡号、08 指标、09 表（序号 1–3：第一张卡；4–6：第二张卡；7、8：第二张卡同期参照；9：第四张卡）；A2 补第三、五张卡的对应；其他列不改',
               'Q148；分析 A36 第二节、第三节；02 各卡验证计划']
    for cidx, v in enumerate(rowvals, 1):
        cell = wc.cell(r, cidx, v)
        src = wc.cell(r - 1, cidx)
        if src.has_style:
            cell._style = copy(src._style)
    done.append(f'更正记录第 {r} 行')
wb.save(p)
print('已改：', done or '无')
for r in range(4, 14):
    print(r, repr(ws.cell(r, 1).value), '|', str(ws.cell(r, 12).value)[:60])
