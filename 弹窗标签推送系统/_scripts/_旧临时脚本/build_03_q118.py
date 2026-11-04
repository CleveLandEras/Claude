"""Q118：03 配置单改版（推进计划 Q118，依据 A31「Q115」、约束 72–76）。
- 规则表：K 列由「去留」改为「批次」；行按 02 v6 重排为 9 行；N1 移到新工作表「提案（待主管定）」
- 排序明细：补「高卡储值下滑」「通用弹窗·金卡以上」
- 更正记录：重写。
不带参数；直接覆盖 03_弹窗配置单.xlsx。"""
from copy import copy
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side

P = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(P)
ws = wb['规则']

COLS = 'ABCDEFGHIJK'
tmpl_y = {c: copy(ws[f'{c}5']._style) for c in COLS}     # 第 5 行：H 黄格
tmpl_n = {c: copy(ws[f'{c}8']._style) for c in COLS}     # 第 8 行：H 无底色

ws['A2'] = ('黄色格为群组 ID，在后台创建群组后回填。未列出的字段沿用现值。新建规则的规则 ID 由后台生成。'
            '「批次」列：第一批 = 不依赖外部答复、可先由运营上线；其余写明等什么、谁补。')
ws['K4'] = '批次'

# 清空旧行 5–12（含 K 列）
for r in range(5, 13):
    for c in COLS:
        ws[f'{c}{r}'].value = None

GROUP_TAG = '等三处标签条件（Dk 自查：当前卡别标签能否圈出金卡以上；「当月储值额小于上月储值额 50%」按完整月还是当月 1 日至今；「已经先存储了」能否取反）；与序号 4、5、6 同时上线'
rows = [
    # 序号, 操作, 规则ID, 类型, 名称, 位置, 对象, 群组ID(黄:True), 弹出数量, 改动说明, 批次
    (1, '修改', 5, '活动类', '活动类弹窗', '大厅', '全部玩家，排除「新增」「回流」', True, 2,
     '仅改对象，排序与各项设置不变',
     '第一批；与序号 2、3 同时上线。上线前先建群组，核对能否选作弹窗对象；不能时改用新建标签「身份非新增、非回流」（Dk / 标签维护人）'),
    (2, '新建', None, '活动类', '新增用户活动弹窗', '大厅', '新增', True, 1,
     '排序见「排序明细」', '第一批；与序号 1、3 同时上线'),
    (3, '新建', None, '活动类', '回流用户活动弹窗', '大厅', '回流', True, 2,
     '排序见「排序明细」', '第一批；与序号 1、2 同时上线'),
    (4, '修改', 6, '储值类', '通用弹窗', '大厅', '任一满足：普卡、银卡', True, 1,
     '对象由「全部玩家」改为普卡、银卡；排序、每日次数、冷却不变', GROUP_TAG),
    (5, '新建', None, '储值类', '通用弹窗·金卡以上', '大厅',
     '任一满足：金卡、白金卡、钻石卡、黑卡、至尊卡；排除：当月储值额小于上月储值额 50%', True, 1,
     '排序、每日次数、冷却与 ID6 相同（沿用现值）', GROUP_TAG),
    (6, '新建', None, '储值类', '高卡储值下滑', '大厅',
     '全部满足：当月储值额小于上月储值额 50%；任一满足：金卡、白金卡、钻石卡、黑卡、至尊卡', True, 1,
     '排序见「排序明细」：第 1 项由运营从现有储值品项中指定（不写价格），之后接通用弹窗原排序',
     GROUP_TAG + '；另需运营指定第 1 项礼包及其每日次数、冷却'),
    (7, '不变', 10, '活动类', '普卡储值衰退50%', '大厅', '普卡 · 当月储值额小于上月储值额 50%', False, 1,
     '普卡的对象、内容、次数维持现状；金卡以上储值下滑者由序号 6 覆盖', '无需操作'),
    (8, '不变', 11, '活动类', '银卡储值衰退50%', '大厅', '银卡 · 当月储值额小于上月储值额 50%', False, 1,
     '维持现状（不停用）', '无需操作'),
    (9, '修改', 7, '储值类', '破产储值弹窗', '破产', '全部玩家', False, 1,
     '排序调整：破产礼包由第 3 位调至第 2 位',
     '等独享礼包、破产礼包价格（Dk 自查）：破产礼包低于独享礼包时上线；高于时保持现序，本行不上线'),
]
for i, row in enumerate(rows):
    r = 5 + i
    (n, op, rid, typ, name, pos, obj, need_grp, cnt, note, batch) = row
    tmpl = tmpl_y if need_grp else tmpl_n
    for c in COLS:
        ws[f'{c}{r}']._style = copy(tmpl[c])
    vals = [n, op, rid, typ, name, pos, obj, None if need_grp else '—', cnt, note, batch]
    for c, v in zip(COLS, vals):
        ws[f'{c}{r}'].value = v
    ws.row_dimensions[r].height = 92 if len(batch) > 60 or len(obj) > 30 else 48
ws.column_dimensions['K'].width = 52

# ---------- 排序明细：补两组 ----------
so = wb['排序明细']
base = so.max_row
tm = {c: copy(so[f'{c}{base}']._style) for c in 'ABCDEFGH'}
tm_stor = {c: copy(so[f'{c}23']._style) for c in 'ABCDEFGH'}   # 储值类行样式（ID7 第 1 行）
add = [
    ('高卡储值下滑', 1, '与储值下滑相关的一项（运营从现有储值品项中指定）', '—', '—', '—', '运营设定', '运营设定'),
    ('高卡储值下滑', 2, '通用弹窗（ID6）原排序', '—', '—', '—', '沿用现值', '沿用现值'),
    ('通用弹窗·金卡以上', '—', '与通用弹窗（ID6）相同', '—', '—', '—', '沿用现值', '沿用现值'),
]
for i, vals in enumerate(add):
    r = base + 1 + i
    for c, v in zip('ABCDEFGH', vals):
        so[f'{c}{r}']._style = copy(tm_stor[c])
        so[f'{c}{r}'].value = v
so[f'A{base}'] = 'ID10 储值衰退50%（不变）'

# ---------- 提案（待主管定）----------
pw = wb.create_sheet('提案（待主管定）', index=2)
pw.column_dimensions['A'].width = 16
pw.column_dimensions['B'].width = 70
pw['A1'] = '提案：储值位按卡别分档（待主管定；定之前不上线，规则表不含本表各行）'
pw['A1'].font = Font(bold=True, size=14)
pw['A2'] = '定案后，本表各行并入「规则」工作表并填批次。'
pw['A2'].font = copy(ws['A2'].font)
hdr = Font(bold=True, size=12)
fill_h = copy(ws['A4'].fill)
thin = Side(style='thin')
items = [
    ('项', '内容'),
    ('操作', '新建（同时把序号 5「通用弹窗·金卡以上」按卡别拆成两条，不再改 ID6，也不会让高卡多弹 1 个）'),
    ('类型 / 位置 / 弹出数量', '储值类 / 大厅 / 1'),
    ('名称', '储值位按卡别分档（原称「在场高卡储值弹窗」）'),
    ('对象', '当前卡别金卡以上，按卡别至少分两档；切法随独享礼包价格定：约 160 元以下：卡 3 / 卡 4–7'
             '（约 74 元以下四档都偏低，仍按 8.7 倍分两档）；约 160–300 元：卡 3–4 / 卡 5–7；约 300–690 元：卡 3–5 / 卡 6–7。'
             '各档排除「当月储值额小于上月储值额 50%」（这部分由序号 6 覆盖）'),
    ('改动说明', '储值位放与该档付费档位相称的礼包（具体礼包由运营定）'),
    ('往上调有依据的人数上界（在场高卡去大户，共 5,146 人）',
     '约 74 元以下四档：5,146（100%）；约 74–160 元对卡 4–7：3,446（84%）；约 160–300 元对卡 5–7：1,827（55%）；'
     '约 300–690 元只对卡 6、7：662（26%）；约 690 元以上没有一档有往上调的依据（这里只判往上调，给低档换更便宜的礼包没有评估）'),
    ('前提', '独享礼包价格（Dk 自查）；当前卡别标签能否圈出金卡以上（Dk 自查）'),
    ('风险', '高卡看到更贵的礼包，反应方向未知；储值位是不是高卡的主要入口未知；1–3% 的提升在现有人数下测不出'),
]
for i, (a, b) in enumerate(items):
    r = 4 + i
    pw[f'A{r}'] = a
    pw[f'B{r}'] = b
    for c in 'AB':
        cell = pw[f'{c}{r}']
        cell.alignment = Alignment(wrap_text=True, vertical='top' if i else 'center')
        cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
        cell.font = hdr if i == 0 else Font(size=12)
        if i == 0:
            cell.fill = copy(fill_h)
    pw.row_dimensions[r].height = 22 if i == 0 else (96 if len(b) > 120 else 44)

# ---------- 更正记录：重写 ----------
cw = wb['更正记录']
for r in range(2, cw.max_row + 1):
    for c in 'ABCDE':
        cw[f'{c}{r}'].value = None
corr = [
    ('2026-09-30', '规则表 K 列', '「去留」列：逐行写「降级」「不进首期」等去留判断', '改为「批次」列：第一批 / 等什么、谁补；去留判断不再出现在配置单',
     '与 02 一致：五类人群卡按主管范围交付'),
    ('2026-09-30', '规则表第 4–6 行（通用弹窗、通用弹窗·金卡以上、高卡储值下滑）', '第 4 行「通用弹窗」：不变',
     '通用弹窗对象改为普卡、银卡；新建「通用弹窗·金卡以上」与「高卡储值下滑」，金卡以上储值下滑者在储值位换一项礼包',
     '02 第二张卡；按原写法金卡以上储值下滑者活动类每日上限 12 → 32、单次 3 → 4，改后三项都不高于现状'),
    ('2026-09-30', '规则表第 7、8 行（ID10、ID11）', 'ID10「对象去除普卡限定，覆盖全部卡别」；ID11「停用」',
     'ID10、ID11 均不变，仍覆盖普卡、银卡', '同上'),
    ('2026-09-30', '规则表第 1–3 行', '活动位三行的去留：随他项 / 降级', '三行同批上线；弹窗对象可用排除按推断已定，上线前先建群组核对',
     'Dk 9/28 认可按推断推进（问题 4）'),
    ('2026-09-30', '原第 12 行（在场高卡储值弹窗）', '与规则表并列，去留写「新增（主线）」',
     '移到工作表「提案（待主管定）」；价格分档的人数上界与切法原样保留', '02「提案：盯住高卡」一节；定之前按五类人群交付'),
    ('2026-09-30', '排序明细', '无高卡储值下滑与通用弹窗·金卡以上', '新增两组；第 1 项礼包由运营指定', '02 附录一'),
]
for i, vals in enumerate(corr):
    r = 2 + i
    for c, v in zip('ABCDE', vals):
        cell = cw[f'{c}{r}']
        cell.value = v
        cell.alignment = Alignment(wrap_text=True, vertical='top')
        cell.font = Font(size=11)
        cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
    cw.row_dimensions[r].height = 62

wb.save(P)
print('已保存', P)
