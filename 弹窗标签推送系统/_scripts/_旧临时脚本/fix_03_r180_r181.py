import openpyxl
p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(p)
ws = wb['规则']

a2 = ws['A2'].value
assert '第一批 = 不依赖外部答复、可先由运营上线' in a2
ws['A2'] = a2.replace(
    '第一批 = 不依赖外部答复、可先由运营上线',
    '第一批 = 不依赖礼包价格和标签口径、可先由运营上线；前提是弹窗对象能选「全部玩家排除某些标签」，上线前由运营核对（第 0 步），不能时要先写一个标签（谁写 SQL：见汇报第 9 件）')

assert ws['K5'].value.startswith('第一批；与序号 2、3 同时上线。上线前先建群组')
ws['K5'] = ('第一批；第 0 步：上线前由运营先建群组「全部玩家，排除新增、回流」，核对能否选作弹窗对象；'
            '不能时改用新建标签「身份非新增、非回流」（谁写 SQL：见汇报第 9 件）；与序号 2、3 同时上线')

k9 = ws['K9'].value
assert '与序号 4、5、6 同时上线' in k9 and '新建标签' not in k9
ws['K9'] = k9 + ('；带排除的群组不能选作弹窗对象时，本行对象改用新建标签「金卡以上且储值未下滑」'
                  '（多一项 SQL，谁写见汇报第 9 件；代价：不能沿用「群组排除」的写法，标签刷新要与序号 4 的卡别标签同步）')

wc = wb['更正记录']
r = wc.max_row + 1
rows = [
    ('2026-09-30', '规则表 A2 表头；K5（序号 1）',
     '「第一批 = 不依赖外部答复」；K5 只写「上线前先建群组，核对能否选作弹窗对象」，没有第 0 步',
     '表头改为「不依赖礼包价格和标签口径；前提是弹窗对象能选『全部玩家排除某些标签』，上线前由运营核对（第 0 步），不能时要先写一个标签」；K5 句首写「第 0 步」，括注改为「谁写 SQL：见汇报第 9 件」',
     '审查 R181；口径约束 80；02 第一张卡'),
    ('2026-09-30', '规则表第 5 行（通用弹窗·金卡以上）K 列',
     '没有写带排除的群组不能选作弹窗对象时怎么办',
     '补退路：对象改用新建标签「金卡以上且储值未下滑」，并写明代价',
     '审查 R180；02 第二张卡前置条件'),
]
for i, row in enumerate(rows):
    for j, v in enumerate(row):
        c = wc.cell(row=r + i, column=j + 1, value=v)
        src = wc.cell(row=r - 1, column=j + 1)
        c.font = src.font.copy(); c.alignment = src.alignment.copy(); c.border = src.border.copy(); c.fill = src.fill.copy()
wb.save(p)
print('ok', r)
