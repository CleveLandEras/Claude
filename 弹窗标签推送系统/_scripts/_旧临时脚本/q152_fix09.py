"""Q152：09 按 A36 第六节 6.1 补表：表5 按注册天数拆行；表6、表7 补储值金额（与破产事件数）；新增表13（圈入者观察月人均储值）、表14（提案乙过程指标）、表15（关闭率与 7 日再登录率）；通用口径补说明；更正记录追加。
不带参数；可重复运行（已有则跳过）。只补黄格以外的口径说明，不填任何数值。"""
import openpyxl
from copy import copy
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

P = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/09_取数需求_上线前基线.xlsx'
wb = openpyxl.load_workbook(P)

FONT = "微软雅黑"
F = Font(name=FONT, size=12)
FB = Font(name=FONT, size=12, bold=True)
FT = Font(name=FONT, size=14, bold=True)
YELLOW = PatternFill("solid", fgColor="FFFF99")
GRAY = PatternFill("solid", fgColor="E7E6E6")
thin = Side(style="thin", color="999999")
BD = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical="center")


def cell(ws, r, c, v, font=F, fill=None, border=True):
    x = ws.cell(row=r, column=c, value=v)
    x.font = font
    x.alignment = WRAP
    if fill:
        x.fill = fill
    if border:
        x.border = BD
    return x


def find_row(ws, text, col=1):
    for r in range(1, ws.max_row + 1):
        if ws.cell(r, col).value == text:
            return r
    return None


done = []

# 表5：按注册天数补两行（与 A31「Q106」两群对上）
ws = wb['表5 潜在付费首储']
if find_row(ws, '其中：注册不到 30 天') is None:
    r0 = find_row(ws, '储值类窗口')
    for k, lab in enumerate(['其中：注册不到 30 天', '其中：注册满一年以上']):
        cell(ws, r0 + 1 + k, 1, lab, FB)
        cell(ws, r0 + 1 + k, 2, None, F, YELLOW)
        cell(ws, r0 + 1 + k, 3, None, F, YELLOW)
    ws['A1'].value = ws['A1'].value + '　按注册天数补两行：注册不到 30 天、注册满一年以上（分母口径同上，只多按注册日拆分，用于与首付率可检测幅度的两群对上）'
    done.append('表5 补两行')

# 表6：补储值金额列与合计行
ws = wb['表6 破产位转化']
if ws.cell(find_row(ws, '弹出礼包'), 4).value is None:
    hr = find_row(ws, '弹出礼包')
    cell(ws, hr, 4, '分子：该弹窗内完成购买的储值金额', FB, GRAY)
    ws.column_dimensions['D'].width = 34
    last = hr
    for r in range(hr + 1, ws.max_row + 1):
        if ws.cell(r, 1).value:
            last = r
            cell(ws, r, 4, None, F, YELLOW)
    cell(ws, last + 1, 1, '全部品项合计', FB)
    for c in (2, 3, 4):
        cell(ws, last + 1, c, None, F, YELLOW)
    ws['A1'].value = ws['A1'].value + '　补储值金额列与全部品项合计行：08 M6 主指标改为破产位内全部品项储值金额 ÷ 破产位曝光次数（合计行 D ÷ B）'
    done.append('表6 补金额列与合计行')

# 表7：补储值金额列与破产事件数
ws = wb['表7 破产位备选']
hr = find_row(ws, '礼包')
if ws.cell(hr, 3).value is None:
    cell(ws, hr, 3, '窗口内储值金额', FB, GRAY)
    ws.column_dimensions['C'].width = 34
    for r in range(hr + 1, ws.max_row + 1):
        if ws.cell(r, 1).value:
            cell(ws, r, 3, None, F, YELLOW)
    last = hr
    for r in range(hr + 1, ws.max_row + 1):
        if ws.cell(r, 1).value:
            last = r
    cell(ws, last + 1, 1, '破产事件数（窗口内破产次数）', FB)
    cell(ws, last + 1, 2, None, F, YELLOW)
    cell(ws, last + 1, 3, '—（本行只填 B 列；埋点未覆盖破产位时，作 08 M6 主指标的分母）', F)
    ws['A1'].value = ws['A1'].value + '　补储值金额列与破产事件数行：无破产位曝光埋点时，M6 主指标 = 破产礼包、独享礼包与其余品项储值金额合计 ÷ 破产事件数（其余品项金额另取）'
    done.append('表7 补金额列与破产事件数')


def new_sheet(name, title, spec, header, labels, widths=None, blank_last=None):
    if name in wb.sheetnames:
        return False
    idx = wb.index(wb['更正记录'])
    ws = wb.create_sheet(name, idx)
    ws.sheet_view.zoomScale = 140
    cell(ws, 1, 1, title, FT, border=False)
    r = 3
    for k, v, y in spec:
        cell(ws, r, 1, k, FB)
        cell(ws, r, 2, v, F, YELLOW if y else None)
        if len(header) > 2:
            ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=len(header))
            for cc in range(3, len(header) + 1):
                ws.cell(row=r, column=cc).border = BD
        r += 1
    r += 1
    for j, h in enumerate(header):
        cell(ws, r, 1 + j, h, FB, GRAY)
    ws.freeze_panes = ws.cell(row=r + 1, column=2)
    for lab in labels:
        r += 1
        cell(ws, r, 1, lab, FB)
        for j in range(1, len(header)):
            cell(ws, r, 1 + j, None, F, YELLOW)
    ws.column_dimensions['A'].width = 30
    for j in range(1, len(header)):
        ws.column_dimensions[chr(65 + j)].width = 34
    return True


if new_sheet(
        '表13 圈入者观察月人均储值',
        '表13　被圈入用户观察月的人均储值（02 第二张卡主指标；08 第〇节）',
        [('窗口', '圈入月、观察月同表4：圈入月最后一日圈入，观察月为下一个自然月（台北时间）', False),
         ('圈入口径', '同表4；金卡至至尊卡组为第二张卡的圈入人群，普卡银卡组（ID10、ID11 不变）作不变参照', False),
         ('分组', '上线前取一次基线（不分组）；上线后按分桶标签「分桶·处理」，处理组、对照组各取一次', False),
         ('用途', '主指标：按分到该组的全部圈入者算人均储值（分母含没买的人）；付费人数只作分解描述', False),
         ('名单来源与取值日', '', True)],
        ['卡别组', '分母：圈入人数（全部人）', '分子：观察月储值总额', '观察月有储值的人数（描述）'],
        ['普卡、银卡', '金卡至至尊卡']):
    done.append('新增表13')

if new_sheet(
        '表14 提案乙过程指标',
        '表14　提案乙（储值位按卡别分档；待主管定）的过程指标（08 第〇节；主管选定后取数）',
        [('窗口', '储值类窗口（见通用口径）', False),
         ('档位', '按 03「提案」工作表的切法（随独享礼包价格）；每档取分档礼包，行数不够时不用的行留空', False),
         ('用途', '过程指标：分档礼包的购买人数与金额、储值位点击；用于「看不出」时区分保留延长与换便宜一级的礼包（购买人数是否不到对照组同一位置原礼包的一半）', False),
         ('分组', '上线后处理组、对照组各取一次（分桶标签「分桶·处理」）', False),
         ('埋点', '储值位点击需要弹窗曝光与点击埋点；没有时该列不取，写明缺', True)],
        ['档', '分母：该档在场人数', '分子：购买分档礼包的人数', '分子：分档礼包购买金额', '储值位点击次数（埋点）'],
        ['档 1', '档 2', '档 3（没有则留空）']):
    done.append('新增表14')

if new_sheet(
        '表15 关闭率与7日再登录率',
        '表15　护栏：弹窗关闭率与 7 日内再登录率（02 各卡验证计划护栏；08 M8、M9）',
        [('窗口', '基本窗口（D-14 至 D-1）；储值类的人群用储值类窗口', False),
         ('关闭率', '需要弹窗曝光与点击埋点：主动点击关闭的次数 ÷ 曝光次数；没有埋点时该列不取，写明缺', True),
         ('7 日内再登录率', '窗口首日有登录的人，之后 7 日内再次有登录的比例；用会员登录记录取', False),
         ('用途', '护栏：上线后处理组不比对照组变差（随机对照下 95% 区间不含 0；切换前后下变差 3 个百分点以上算突破）', False)],
        ['人群', '分母：曝光次数（关闭率）', '分子：主动关闭次数', '分母：窗口首日在场人数', '分子：其中 7 日内再登录的人数'],
        ['新增', '回流', '其余', '金卡以上储值下滑者', '在场高卡去大户（提案乙）', '破产（破产后 7 日内再登录）']):
    done.append('新增表15')

# 通用口径补说明
ws = wb['通用口径']
if find_row(ws, '按 A36 补（2026-09-30）') is None:
    r = ws.max_row + 1
    cell(ws, r, 1, '按 A36 补（2026-09-30）', FB)
    cell(ws, r, 2, '表5 按注册天数补两行；表6、表7 补储值金额（表7 另补破产事件数）；新增表13（圈入者观察月人均储值）、表14（提案乙过程指标）、表15（关闭率与 7 日再登录率）。表9、表13、表14、表15 上线后按处理组、对照组各取一次（分桶·处理）。上线前基线不分组。详见 分析/A36_验证计划.md 第六节 6.1', F)
    done.append('通用口径补一行')

# 更正记录
cw = wb['更正记录']
if not any((cw.cell(r, 5).value or '').startswith('Q152') for r in range(1, cw.max_row + 1)):
    r = cw.max_row + 1
    row = ('2026-09-30', '表5、表6、表7；新增表13、表14、表15；通用口径',
           '表6、表7 只取购买次数，无金额与全品项合计，也没有破产事件数；无「圈入者观察月人均储值」表；提案乙过程指标、关闭率、7 日再登录率无表；表5 只有一个潜在付费分母，无法与首付率的新注册、老账号两群对上',
           '表5 按注册天数补两行；表6、表7 补金额列（表6 补合计行、表7 补破产事件数行）；新增表13、表14、表15；通用口径补一行；所有新增格只留黄格，不填数',
           'Q152；分析 A36 第六节 6.1 第 2–5、8 条')
    for i, v in enumerate(row, start=1):
        c = cw.cell(row=r, column=i)
        c.value = v
        c._style = copy(cw.cell(row=r - 1, column=i)._style)
    done.append('更正记录一行')

wb.save(P)
print('已改：', done or '无')
print(wb.sheetnames)
