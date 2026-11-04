import copy
import openpyxl

p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(p)
ws = wb['规则']


def copy_style(src, dst):
    dst.font = copy.copy(src.font)
    dst.fill = copy.copy(src.fill)
    dst.border = copy.copy(src.border)
    dst.alignment = copy.copy(src.alignment)
    dst.number_format = src.number_format


# R235：K5 补对照组互补标签
k5 = ws['K5'].value
anchor = '（见本表新增的「ID5 处理版」行）。'
add = ('第 0 步第一项不通过（带排除的对象不能用）时，对照组 ID5 对象改用互补标签「分桶·对照」'
       '（与「分桶·处理」同一次分桶生成，多 1 个 SQL 标签，谁写见汇报第 9 件）。')
if 'R235' in k5 or '分桶·对照' in k5:
    print('K5 已含，跳过')
elif anchor in k5:
    ws['K5'] = k5.replace(anchor, anchor + add + '（R235）', 1)
else:
    print('K5 锚点未找到')

# Q166：A2 补转全量说明
a2 = ws['A2'].value
add2 = ('「转全量」（Q166）：随机对照下判完后对照组转全量，指去掉各行默认配法里的「分桶·处理」条件并停用处理版；'
        '序号 4–6、9 与提案表没有单独标「退路（全量）」，它们的 G 列（提案表为「对象」「改动说明」）本身就是全量写法，转全量即恢复该写法；'
        '判完各档后对照组去向见 02 附录六。')
if 'Q166' not in a2:
    ws['A2'] = a2 + ' ' + add2

# 更正记录
wc = wb['更正记录']
if not any('Q166' in str(wc.cell(r, 5).value) for r in range(2, wc.max_row + 1)):
    r = wc.max_row + 1
    vals = [
        '2026-09-30',
        '规则表 K5；A2',
        'K5 第 0 步第一项不通过（带排除的对象不能用）时，只写第 14 行对象改用合并标签，没有写对照组 ID5 本身要改用什么；A2 写「退路（全量）」只对序号 1–3 有标注，判完后「转全量」在序号 4–6、9 与提案表指什么没写',
        'K5 补「对照组 ID5 对象改用互补标签『分桶·对照』（与『分桶·处理』同一次分桶生成，多 1 个 SQL 标签）」；A2 补「转全量」的含义：去掉默认配法里的『分桶·处理』条件并停用处理版，序号 4–6、9 与提案表的 G 列（提案表为对象、改动说明）本身就是全量写法。批次与配置内容未改；L 列没有写「过 →」「看不出 →」去向与判读时点，按设计卡未补',
        '审查 R235（13:14）；设计卡 Q166 子问题三「执行前核对」；02 附录六',
    ]
    for i, v in enumerate(vals, start=1):
        c = wc.cell(r, i, v)
        copy_style(wc.cell(r - 1, i), c)

wb.save(p)

wb2 = openpyxl.load_workbook(p)
w = wb2['规则']
print('K5 命中分桶·对照:', '分桶·对照' in w['K5'].value)
print('K5 末 200:', w['K5'].value[-200:])
print('A2 末:', w['A2'].value[-260:])
print('更正记录行数', wb2['更正记录'].max_row)
print('sheets', wb2.sheetnames, '规则行', w.max_row)
print('G5', w['G5'].value[:40], '| G14', w['G14'].value[:40], '| L5', w['L5'].value[:30])
