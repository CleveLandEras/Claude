"""Q162：09 按设计卡 Q160 补丁（守约束 98：接在 q156_fix09.py 之后运行，不重生成 build_09.py）。
只动表16：补五列（破产礼包储值合计、独享礼包储值合计、购买过破产礼包的破产者人数、主指标每人值标准差、独享礼包每人金额标准差）、
说明补截尾一句、加截尾值一行；通用口径与更正记录各追加一行。不带参数；可重复运行（已有则跳过）；只补黄格与口径说明，不填数值。
运行后读回核对表 13–16 与表 1–3、5、6、7 的改动仍在。"""
import openpyxl
from copy import copy
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

P = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/09_取数需求_上线前基线.xlsx'
wb = openpyxl.load_workbook(P)

FONT = "微软雅黑"
F = Font(name=FONT, size=12)
FB = Font(name=FONT, size=12, bold=True)
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
ws = wb['表16 破产者人均储值']
hr = find_row(ws, '判读时点·分组')
new_cols = [
    'Q160 补：破产礼包储值合计（同一批破产者、同一窗口、全部渠道）',
    'Q160 补：独享礼包储值合计（同上）',
    'Q160 补：购买过破产礼包的破产者人数（只作分解；破产礼包购买率 = 本列 ÷ C 列）',
    'Q160 补：主指标每人值的标准差（截尾后）',
    'Q160 补：独享礼包每人金额的标准差（截尾后）',
]
if hr is not None and ws.cell(hr, 7).value is None:
    for j, h in enumerate(new_cols):
        cell(ws, hr, 7 + j, h, FB, GRAY)
        ws.column_dimensions[chr(71 + j)].width = 34
    r = hr + 1
    while ws.cell(r, 1).value:
        for j in range(len(new_cols)):
            cell(ws, r, 7 + j, None, F, YELLOW)
        r += 1
    # 截尾值另列一行
    cell(ws, r, 1, '两组合并 P99 截尾值（主指标每人值；独享礼包每人金额；各判读时点各一格）', FB)
    for c in (2, 3):
        cell(ws, r, c, None, F, YELLOW)
    # 说明：大户一行补截尾句
    br = find_row(ws, '大户')
    if br is not None:
        v = ws.cell(br, 2).value or ''
        if 'Q160' not in v:
            ws.cell(br, 2).value = v + '。Q160 补：D 列与新增金额列、标准差列，均按两组合并 P99 截尾后的每人值计；截尾值另列一格（见表末一行）。用途：两礼包合计（G 列 + H 列）用于第四张卡「看不出」终判分格（主指标点估计大于 0，且两礼包合计人均金额处理组不低于对照）；标准差列用于主指标与挪量一支的区间；分格本身只用点估计'
    done.append('表16 补五列、截尾值行、说明')

ws = wb['通用口径']
if find_row(ws, '按 Q160 补（2026-09-30）') is None:
    r = ws.max_row + 1
    cell(ws, r, 1, '按 Q160 补（2026-09-30）', FB)
    cell(ws, r, 2, '表16 补两礼包储值合计、购买过破产礼包的破产者人数、两列标准差（第四张卡「看不出」终判分格用；同一批破产者、同一窗口、全部渠道、两组合并 P99 截尾后）。字段只含会员编号联结，不取任何个人身份或联系方式信息。数据组能否取到：待确认。详见 分析/A36_验证计划.md、设计卡 Q160', F)
    done.append('通用口径补一行')

cw = wb['更正记录']
if not any((cw.cell(r, 5).value or '').startswith('Q162') for r in range(1, cw.max_row + 1)):
    r = cw.max_row + 1
    row = ('2026-09-30', '表16；通用口径',
           '表16 只有破产者人数与储值合计（全部品项），分不出两个礼包，也没有每人值的离散度，第四张卡「看不出」终判分格与主指标、挪量一支的区间都算不出来',
           '表16 补五列（破产礼包储值合计、独享礼包储值合计、购买过破产礼包的破产者人数、主指标每人值标准差、独享礼包每人金额标准差），截尾值另列一行；通用口径补一行；新增格只留黄格，不填数',
           'Q162；设计卡 Q160；分析 A36')
    for i, v in enumerate(row, start=1):
        c = cw.cell(row=r, column=i)
        c.value = v
        c._style = copy(cw.cell(row=r - 1, column=i)._style)
    done.append('更正记录一行')

wb.save(P)
print('已改：', done or '无')
print(wb.sheetnames)
# 读回核对：表 13–16 与表 1–3、5、6、7 仍在
need = ['表1', '表2', '表3', '表5', '表6', '表7', '表13', '表14', '表15', '表16']
for n in need:
    ok = any(s.startswith(n + ' ') for s in wb.sheetnames)
    print(n, '在' if ok else '缺！')
ws = wb['表16 破产者人均储值']
for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
    vals = [str(c.value)[:30] if c.value is not None else '' for c in row[:11]]
    if any(vals):
        print(' | '.join(vals))
