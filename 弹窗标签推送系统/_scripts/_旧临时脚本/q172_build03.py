import copy, shutil, os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
P = BASE + '支撑文件/03_弹窗配置单.xlsx'
BK = BASE + '_versions/03_pre_Q172.xlsx'
if not os.path.exists(BK):
    shutil.copyfile(P, BK)

wb = openpyxl.load_workbook(P)
assert '最终规则全表' not in wb.sheetnames, 'already built'

# 改前四张表的逐格快照
def snap(wb_):
    d = {}
    for ws_ in wb_.worksheets:
        for row in ws_.iter_rows():
            for c in row:
                if c.value is not None:
                    d[(ws_.title, c.coordinate)] = c.value
    return d
before = snap(wb)

# 读取排序明细
so = wb['排序明细']
items = {}
for r in range(5, so.max_row + 1):
    rule = so.cell(r, 1).value
    if not rule:
        continue
    items.setdefault(rule, []).append(tuple(so.cell(r, c).value for c in range(2, 9)))

def fmt_item(t):
    order, name, d, e, f, g, h = t
    slots = [lab for lab, v in (('活动开启', d), ('首次登入', e), ('大厅', f)) if v == '●']
    slot_txt = '、'.join(slots) if slots else '—'
    return f'{name}（时机：{slot_txt}；每日 {g} 次；冷却 {h} 秒）'

def lines(rule):
    return '\n'.join(f'{i+1}. ' + fmt_item(t) for i, t in enumerate(items[rule]))

# 回流规则各项设置（ID5 照抄）
liu = {t[1]: t for t in items['回流用户活动弹窗']}
id5_order = ['月月抽', '限时挑战', '卡别直升活动', '发信送奖', '天天敲蛋礼V2', 'BOSS战', '回流任务',
             '每日补给计划', '连线格格送', '活动排行榜']
id5_seq = ' → '.join(id5_order)
id5_set = '\n'.join(f'{i+1}. ' + fmt_item(liu[n]) for i, n in enumerate(id5_order))
id5_set += '\n（ID5 各项设置取自「排序明细」回流用户活动弹窗各行，03 与 02 均写新建规则的时机、每日次数、冷却照抄 ID5）'

id6_seq = '首储礼包 → 独享礼包 → 惊喜三选一 → 限时加码礼包 → 生涯限购 → 每日礼包 → 平台限量/专属礼包'
id6_set = '各项每日次数、冷却沿用现值（本地未取得，不改）'
carddown = '金卡、白金卡、钻石卡、黑卡、至尊卡'

def seq_of(rule):
    return ' → '.join(t[1] for t in items[rule])

price_note = '等独享礼包、破产礼包价格（Dk 自查）：破产礼包低于独享礼包时上线；高于时保持现序，本行不上线'
tag_note = '等三处标签条件（Dk 自查：当前卡别标签能否圈出金卡以上；「当月储值额小于上月储值额 50%」按完整月还是当月 1 日至今）；与序号 4、5、6 同时上线'

rows = [
    (1, 'ID5 活动类弹窗', '活动类', '大厅', '改对象', '全部玩家，排除：新增、回流', 2, id5_seq, id5_set,
     '第一批；与序号 2、3 同时上线；前提：弹窗对象能选「全部玩家，排除某些标签」（上线前由运营核对）'),
    (2, '新增用户活动弹窗（新建）', '活动类', '大厅', '新建', '新增', 1, seq_of('新增用户活动弹窗'), lines('新增用户活动弹窗'),
     '第一批；与序号 1、3 同时上线'),
    (3, '回流用户活动弹窗（新建）', '活动类', '大厅', '新建', '回流', 2, seq_of('回流用户活动弹窗'), lines('回流用户活动弹窗'),
     '第一批；与序号 1、2 同时上线'),
    (4, 'ID6 通用弹窗', '储值类', '大厅', '改对象', '全部玩家，排除：' + carddown, 1, id6_seq, id6_set + '；排序不变',
     tag_note),
    (5, '通用弹窗·金卡以上（新建）', '储值类', '大厅', '新建', '任一满足：' + carddown + '；排除：当月储值额小于上月储值额 50%', 1,
     '与 ID6 相同：' + id6_seq, '同 ID6，沿用现值', tag_note),
    (6, '高卡储值下滑（新建）', '储值类', '大厅', '新建', '全部满足：当月储值额小于上月储值额 50%；任一满足：' + carddown, 1,
     '第 1 项：与储值下滑相关的一项（运营从现有储值品项中指定，不写价格）→ 之后同 ID6：' + id6_seq,
     '第 1 项每日次数与冷却由运营设定；其后各项同 ID6，沿用现值', tag_note + '；另需运营指定第 1 项礼包及其每日次数、冷却'),
    (7, 'ID10 普卡储值衰退 50%', '活动类', '大厅', '不变', '普卡 · 当月储值额小于上月储值额 50%', 1, '每日补给计划',
     '每日补给计划（' + '时机：' + '、'.join(l for l, v in zip(['活动开启', '首次登入', '大厅'], items['ID10 储值衰退50%（不变）'][0][2:5]) if v == '●') + '；每日 20 次；冷却 1800 秒）',
     '无需操作'),
    (8, 'ID11 银卡储值衰退 50%', '活动类', '大厅', '不变', '银卡 · 当月储值额小于上月储值额 50%', 1, '每日补给计划', '同 ID10', '无需操作'),
    (9, 'ID7 破产储值弹窗', '储值类', '破产', '改顺序', '全部玩家', 1, seq_of('ID7 破产储值弹窗'),
     '各项每日次数、冷却沿用现值（「排序明细」ID7 各行）；只调顺序：破产礼包由第 3 位调至第 2 位，现状为首储礼包 → 独享礼包 → 破产礼包 → 限时加码礼包 → 惊喜三选一 → 生涯限购 → 每日礼包 → 平台限量/专属礼包',
     price_note),
]

# 复核：最终排序与「排序明细」一致
assert seq_of('ID7 破产储值弹窗') == '首储礼包 → 破产礼包 → 独享礼包 → 限时加码礼包 → 惊喜三选一 → 生涯限购 → 每日礼包 → 平台限量/专属礼包'

ws = wb.create_sheet('最终规则全表', 0)
font_t = Font(name='Microsoft YaHei', size=14, bold=True)
font_n = Font(name='Microsoft YaHei', size=11)
font_h = Font(name='Microsoft YaHei', size=12, bold=True)
font_b = Font(name='Microsoft YaHei', size=12)
fill_h = PatternFill('solid', fgColor='FFE8E6E1')
thin = Side(style='thin')
border = Border(left=thin, right=thin, top=thin, bottom=thin)

ws['A1'] = '最终规则全表：改完以后的 9 条弹窗规则（含没有改的 ID10、ID11）'
ws['A1'].font = font_t
ws['A1'].alignment = Alignment(wrap_text=False, vertical='top')
ws['A2'] = ('只写上线后的最终状态。验证用的处理版（「规则」表序号 1′）、「分桶·处理」「分桶·对照」、退路对象（全量）等配法见「规则」表，不在本表。'
            '序号与「规则」表一致。已有规则写规则 ID；新建规则的 ID 由后台生成。每次弹出数、排序、时机、次数、冷却沿用现值的，写明「沿用现值」。')
ws['A2'].font = font_n
ws['A2'].alignment = Alignment(wrap_text=False, vertical='top')
ws.row_dimensions[1].height = 32
ws.row_dimensions[2].height = 24

heads = ['序号', '规则', '类型', '位置', '改动', '最终对象', '每次弹出数', '完整排序（按顺序取第一个可参与、可购买的）',
         '各项时机 / 每日次数 / 冷却', '批次与上线条件']
for j, h in enumerate(heads, 1):
    c = ws.cell(4, j, h)
    c.font = font_h; c.fill = fill_h; c.border = border
    c.alignment = Alignment(wrap_text=True, vertical='center')
ws.row_dimensions[4].height = 34
for i, row in enumerate(rows):
    r = 5 + i
    for j, v in enumerate(row, 1):
        c = ws.cell(r, j, v)
        c.font = font_b; c.border = border
        c.alignment = Alignment(wrap_text=True, vertical='center' if j in (1, 3, 4, 5, 7) else 'top')
    nl = max(str(row[8]).count('\n') + 1, 3)
    ws.row_dimensions[r].height = min(max(76, 21 * nl), 260)

widths = {'A': 7, 'B': 24, 'C': 9, 'D': 8, 'E': 10, 'F': 36, 'G': 11, 'H': 46, 'I': 52, 'J': 46}
for k, v in widths.items():
    ws.column_dimensions[k].width = v
ws.sheet_view.zoomScale = 120
ws.freeze_panes = 'A5'

# 更正记录追加一行
ec = wb['更正记录']
last = 1
for r in range(1, ec.max_row + 1):
    if ec.cell(r, 1).value:
        last = r
nr = last + 1
vals = ['2026-09-30', '新增工作表「最终规则全表」（放在「规则」表之前）',
        '03 只有「规则」（默认配法、退路、处理版与 9 条规则混排）和「排序明细」，没有一处能看到改完以后的 9 条规则全貌，不变的 ID10、ID11 与没改动的排序也不在表内',
        '新增「最终规则全表」：9 条规则各一行，列出最终对象、每次弹出数、完整排序、各项时机 / 每日次数 / 冷却、批次与上线条件；「规则」「排序明细」两表未动一格',
        'Dk 9/30「02 要有全景」；推进计划 Q172；与 02 开头「规则全表」逐项一致']
for j, v in enumerate(vals, 1):
    src = ec.cell(last, j)
    c = ec.cell(nr, j, v)
    c.font = copy.copy(src.font); c.alignment = copy.copy(src.alignment); c.border = copy.copy(src.border)
    c.fill = copy.copy(src.fill)
ec.row_dimensions[nr].height = 62

wb.save(P)

# 校验：原四张表逐格不变
wb2 = openpyxl.load_workbook(P)
after = snap(wb2)
diff = 0
for k, v in before.items():
    if k[0] == '更正记录':
        continue
    if after.get(k) != v:
        diff += 1
for k in after:
    if k[0] not in ('最终规则全表', '更正记录') and k not in before:
        diff += 1
print('原三表（规则、排序明细、提案）逐格差异数：', diff)
ecb = {k: v for k, v in before.items() if k[0] == '更正记录'}
eca = {k: v for k, v in after.items() if k[0] == '更正记录' and k in ecb}
print('更正记录原有格差异：', sum(1 for k in ecb if eca.get(k) != ecb[k]))
print('工作表：', wb2.sheetnames)
for r in range(5, 14):
    print([wb2['最终规则全表'].cell(r, c).value for c in (1, 2, 5, 6, 7)])
