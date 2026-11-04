import copy
import openpyxl

p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/09_取数需求_上线前基线.xlsx'
wb = openpyxl.load_workbook(p)


def copy_style(src, dst):
    dst.font = copy.copy(src.font)
    dst.fill = copy.copy(src.fill)
    dst.border = copy.copy(src.border)
    dst.alignment = copy.copy(src.alignment)
    dst.number_format = src.number_format


# ---- 表16 ----
ws = wb['表16 破产者人均储值']
if ws['L10'].value:
    print('表16 已改过，跳过')
else:
    ws['B7'] = (
        '按 A34 前 134 人名单（上线前定）单列监测，不进检验。'
        '截尾（Q166）：每个判读时点只算一个截尾值 C = 主指标每人值的两组合并 P99（基线行用基线自身 P99）；'
        'D 列、G 列、H 列都按每人 min(值, C) 汇总，J、K 列按截尾后的每人值算标准差；'
        '两礼包合计 = 截尾后 G + H，不再单独截尾；C 为 0 时改用每人值大于 0 者的 P99（退路，见 N 列）。'
        '用途：两礼包合计用于第四张卡「看不出」终判分格；标准差列用于主指标与挪量一支的区间；分格本身只用点估计。'
    )
    ws['A16'] = '截尾值见 M、N 列（Q166 起不再单列本行）'
    ws['L10'] = 'Q166 补：购买过独享礼包的破产者人数（只作分解；看礼包购买稀疏程度，09 回填后设计者复核本口径用）'
    ws['M10'] = ('Q166 补：截尾值 C（本判读时点两组合并的主指标每人值 P99；基线行为基线自身 P99；'
                 '同一判读时点的两行填同一个数；D、G、H、J、K 列都用这一个值）')
    ws['N10'] = 'Q166 补：C 的取法（标准 / 退路：P99 为 0 时改用每人值大于 0 者的 P99）'
    for col in 'LMN':
        copy_style(ws['K10'], ws[f'{col}10'])
        if ws.column_dimensions['K'].width:
            ws.column_dimensions[col].width = ws.column_dimensions['K'].width
        for r in range(11, 16):
            copy_style(ws[f'K{r}'], ws[f'{col}{r}'])

# ---- 表2、表3 ----
for sheet in ['表2 新增7日留存', '表3 回流7日留存']:
    ws = wb[sheet]
    b4 = ws['B4'].value
    old = '是否要因此把第 1 期末的判读时点整体后移，属判读合同，交设计者（见审查 R233）。'
    new = ('上线后第 k 期：队列为第 k 期队列窗口，储值观察至该期队列最后一日 + 13 日；'
           '第一张卡两个判读时点都定在这一天（设计卡 Q166），留存在队列最后一日 + 7 日取齐后只报数、不判。')
    if old in b4:
        ws['B4'] = b4.replace('上线后：每期队列最后一日再过 13 日，储值才取齐，储值护栏的取数在此之后；' + old, new)
        if old in ws['B4'].value:
            ws['B4'] = b4.replace(old, new)
    else:
        print(sheet, 'B4 未含原句，跳过')
    a23 = ws['A23'].value
    if 'Q166' not in a23:
        ws['A23'] = a23 + '截尾值为 0 时改用每人值大于 0 者的 P99（退路，见通用口径「按 Q166 补」）。'
    d5 = ws['D5'].value
    if 'R236' not in d5:
        ws['D5'] = d5 + '；D 列只覆盖基线储值窗口 14 天中的 8 天，只作按日走势参考，基线合计以下面检验用数块为准，不要当基线总额（R236）'

# ---- 通用口径 ----
ws = wb['通用口径']
if not any('Q166' in str(ws.cell(r, 1).value) for r in range(1, ws.max_row + 1)):
    r = ws.max_row + 1
    ws.cell(r, 1, '按 Q166 补（2026-09-30）')
    ws.cell(r, 2, (
        '凡本文件带两组合并 P99 截尾的表（表2、3、9、13、16）：每张表每个判读时点只算一个截尾值，'
        '取该表主指标（或护栏）每人值的两组合并 P99，同一值用于该表所有每人金额列，不按列另算；'
        '截尾值为 0 时改用每人值大于 0 者的 P99，并注明「退路」。表16 的对应关系见其 B7。'
    ))
    copy_style(ws.cell(r - 1, 1), ws.cell(r, 1))
    copy_style(ws.cell(r - 1, 2), ws.cell(r, 2))

# ---- 更正记录 ----
ws = wb['更正记录']
if not any('Q166' in str(ws.cell(r, 5).value) for r in range(4, ws.max_row + 1)):
    r = ws.max_row + 1
    vals = [
        '2026-09-30',
        '表16 B7、A16、L10–N10；表2、表3 B4、A23、D5；通用口径',
        '表16 各金额列各按自己的 P99 截尾，礼包金额稀疏时 P99 = 0，截尾后整列为 0（独享标准差为 0，挪量一支恒判不出；两礼包合计两组都为 0）；表2、表3 上线后判读时点写「交设计者」；D 列只覆盖基线储值窗口 14 天中的 8 天，易被当基线总额',
        '每个判读时点只算一个截尾值 C（主指标每人值两组合并 P99），D、G、H、J、K 列共用，两礼包合计 = 截尾后 G + H；C 为 0 时改用每人值大于 0 者的 P99；表16 补 L 列（购买过独享礼包人数）、M 列（截尾值）、N 列（取法），原 A16 改指向句；第一张卡两个判读时点定在该期队列最后一日 + 13 日，留存取齐后只报数；表2、表3 D 列标明只作走势参考（R236）；通用口径补一行',
        '审查 R232、R233、R236；设计卡 Q166；约束 100、108、109',
    ]
    for i, v in enumerate(vals, start=1):
        c = ws.cell(r, i, v)
        copy_style(ws.cell(r - 1, i), c)

wb.save(p)

# ---- 读回核对 ----
wb2 = openpyxl.load_workbook(p)
print(wb2.sheetnames)
ws = wb2['表16 破产者人均储值']
print('表16 B7:', ws['B7'].value[:80])
print('表16 A16:', ws['A16'].value)
for c in ['G10', 'H10', 'I10', 'J10', 'K10', 'L10', 'M10', 'N10']:
    print(c, str(ws[c].value)[:40])
for s in ['表2 新增7日留存', '表3 回流7日留存']:
    w = wb2[s]
    print(s, 'A4', w['A4'].value, '| B4 末句:', w['B4'].value[-110:])
    print('  D5 末:', w['D5'].value[-40:], '| A23 末:', w['A23'].value[-40:])
    print('  A24-E24', [w.cell(24, i).value for i in range(1, 6)])
w = wb2['通用口径']
print('通用口径 行数', w.max_row, w.cell(w.max_row, 1).value)
w = wb2['更正记录']
print('更正记录 行数', w.max_row)
# 原有改动仍在
print('表1 max_row', wb2['表1 回流任务参与率'].max_row, '表9', wb2['表9 储值类主指标基线'].max_row,
      '表13', wb2['表13 圈入者观察月人均储值'].max_row, '表14', wb2['表14 提案乙过程指标'].max_row)
print('检索残留 "交设计者"/"待 Q166"/"后移":')
for s in wb2.sheetnames:
    for row in wb2[s].iter_rows():
        for c in row:
            v = str(c.value or '')
            if s != '更正记录' and ('见审查 R233' in v or '待 Q166' in v or 'Q166 定稿中' in v or '还在定' in v):
                print('  残留', s, c.coordinate, v[:60])
