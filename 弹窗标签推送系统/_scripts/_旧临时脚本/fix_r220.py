# -*- coding: utf-8 -*-
"""R220：03 规则表序号 1–3 的 G 列改写默认配法对象，退路对象挪到 K 列开头；K5 第 0 步补「全部满足 + 排除」同时可用的核对；A2 与更正记录同步。
不带参数；有幂等检查（已改过就不再改）。批次与配置内容不改。"""
import copy
import openpyxl
p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(p)
ws = wb['规则']
if str(ws['K5'].value).startswith('退路对象'):
    print('已改过，不重复'); raise SystemExit

# 序号 1（第 5 行）：对照组仍走原 ID5
ws['G5'].value = '默认配法：全部玩家，排除「分桶·处理」（对照组，仍走原 ID5；处理组见第 14 行「ID5 处理版」）'
ws['K5'].value = ('退路对象（全量，走路 C；分桶标签来不及建时用）：全部玩家，排除「新增」「回流」。'
                  '第 0 步再补一项核对：默认配法要在同一个对象里同时用「全部满足」与「排除」（第 14 行、序号 2、3、5、6 都是这种写法），运营上线前核对能否这样选。'
                  + ws['K5'].value)
ws['J5'].value = ws['J5'].value + '（此为退路写法；默认配法的对象见 G 列）'
# 序号 2、3
ws['G6'].value = '默认配法：全部满足：新增；分桶·处理'
ws['K6'].value = '退路对象（全量，走路 C）：新增。' + ws['K6'].value
ws['G7'].value = '默认配法：全部满足：回流；分桶·处理'
ws['K7'].value = '退路对象（全量，走路 C）：回流。' + ws['K7'].value
# A2 说明
ws['A2'].value = ws['A2'].value + ' 「对象」列：序号 1–3 与第 14 行写默认配法的对象；序号 1–3 的退路对象在 K 列开头「退路对象」处。'

# 更正记录
w2 = wb['更正记录']
r = w2.max_row + 1
vals = ['2026-09-30', '规则表序号 1–3 的 G 列与 K 列；K5 第 0 步；A2',
        '第 17 件推荐默认配法，但序号 1–3 的 G 列（对象）仍写退路对象，默认配法的对象只在 K 列长句里；K5 第 0 步只核对「全部玩家，排除新增、回流」能不能选，没有核对「全部满足」与「排除」能否同时用',
        'G 列改写默认配法的对象（序号 1 为对照组「全部玩家，排除分桶·处理」，序号 2、3 为「全部满足：新增 / 回流；分桶·处理」），退路对象挪到 K 列开头写明；K5 第 0 步补核对「全部满足 + 排除」能否同时用；A2 同步。批次与配置内容未改',
        '审查 R220；Q154 遗留']
for c, v in enumerate(vals, 1):
    cell = w2.cell(r, c)
    cell.value = v
    src = w2.cell(r - 1, c)
    cell.font = copy.copy(src.font); cell.alignment = copy.copy(src.alignment)
    cell.border = copy.copy(src.border); cell.fill = copy.copy(src.fill)
w2.row_dimensions[r].height = w2.row_dimensions[r - 1].height or 62
wb.save(p)
wb2 = openpyxl.load_workbook(p)
print(wb2['规则']['G5'].value); print(wb2['规则']['G6'].value); print(wb2['规则']['G7'].value)
print(wb2['规则']['K5'].value[:120]); print(wb2['更正记录'].max_row)
