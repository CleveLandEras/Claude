"""Q156：09 按设计卡 Q155 补丁（守约束 98：接在 q152_fix09.py 之后运行，不重生成）。
表1 补发放点数列；表2、表3 补队列第 0–13 日储值列与大户行，表3 标题改主指标；表6、表7 改标分解项（表7 补其余品项行）；
新增表16 破产者人均储值（M6 新主指标）；表15 补普卡银卡圈入者一行并改护栏判读说明；通用口径与更正记录各追加一行。
不带参数；可重复运行（已有则跳过）；只补黄格与口径说明，不填数值。"""
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

# 表1：补发放点数列（监测，不判）
ws = wb['表1 回流任务参与率']
if ws.cell(6, 4).value is None:
    cell(ws, 6, 4, '监测：窗口内回流任务发放点数合计（待确认数据源）', FB, GRAY)
    cell(ws, 7, 4, None, F, YELLOW)
    ws.column_dimensions['D'].width = 40
    ws['A1'].value = ws['A1'].value + '　Q156 补 D 列：回流任务赠点发放量，第一张卡只作监测、不判突破（A36；回流任务参与记录是否含发放点数未知，A35）。上线后处理组、对照组各取一次，报合计与人均（按回流队列全部人）'
    done.append('表1 补发放点数列')

# 表2、表3：补队列第 0–13 日储值列与大户行
for name in ('表2 新增7日留存', '表3 回流7日留存'):
    ws = wb[name]
    if ws.cell(5, 4).value is None:
        cell(ws, 5, 4, '护栏：队列第 0–13 日储值总额（含没付费的人；自注册日 / 回流判定日起）', FB, GRAY)
        ws.column_dimensions['D'].width = 40
        for r in range(6, 20):
            cell(ws, r, 4, None, F, YELLOW)
        cell(ws, 20, 1, '其中：活动位大户（A34 名单，单列监测，不进检验）', FB)
        for c in (2, 3, 4):
            cell(ws, 20, c, None, F, YELLOW)
        ws['A1'].value = ws['A1'].value + '　Q156 补 D 列与大户行：第一张卡储值护栏「新增、回流人均储值不低于对照」（08 M3 后；新增、回流两队列合起来算一个检验，每人第 0–13 日储值合计，检验前按两组合并 P99 截尾）。上线后按处理组、对照组各取一次'
        done.append(name + ' 补储值列与大户行')
ws = wb['表3 回流7日留存']
if '护栏：回流用户活动弹窗上线后不许下降' in (ws['A1'].value or ''):
    ws['A1'].value = ws['A1'].value.replace('【护栏：回流用户活动弹窗上线后不许下降】', '【回流子人群主指标；Q155 起其「不过」由主指标规则覆盖，不再兼按护栏判】')
    done.append('表3 标题')

# 表6：改标分解项
ws = wb['表6 破产位转化']
if 'Q156' not in ws['A1'].value:
    ws['A1'].value = ws['A1'].value.split('　补储值金额列')[0] + '　Q156 更正：08 M6 主指标已改为「破产者人均储值（全部渠道，按人算区间）」，取数见表16；本表（破产位内按礼包拆的次数与金额）只作分解项，不再作主指标分子分母，且需要埋点覆盖破产位'
    done.append('表6 改标分解项')

# 表7：改标分解项，补其余品项行
ws = wb['表7 破产位备选']
if 'Q156' not in ws['A1'].value:
    ws['A1'].value = ws['A1'].value.split('　补储值金额列')[0] + '　Q156 更正：08 M6 主指标已改为「破产者人均储值（全部渠道）」，见表16；本表不再作主指标分母，只作分解项（无埋点时的订单口径）'
    ws['C9'].value = '—（本行只填 B 列；只作分解项参考，不再作 M6 主指标分母）'
    cell(ws, 10, 1, '其余品项（限时加码礼包、惊喜三选一、生涯限购、每日礼包、平台限量/专属礼包）', FB)
    cell(ws, 10, 2, None, F, YELLOW)
    cell(ws, 10, 3, None, F, YELLOW)
    done.append('表7 改标分解项并补其余品项行')

# 表15：补普卡银卡圈入者一行；护栏判读说明
ws = wb['表15 关闭率与7日再登录率']
if find_row(ws, '普卡、银卡圈入者（ID10、ID11 不变）') is None:
    cell(ws, 15, 1, '普卡、银卡圈入者（ID10、ID11 不变）', FB)
    for c in range(2, 6):
        cell(ws, 15, c, None, F, YELLOW)
    if '95% 区间不含 0' in (ws['B6'].value or ''):
        ws['B6'].value = '护栏：上线后处理组不比对照组变差（统计型，只在第 1 期末、合并 3 期末两个时点判，均用 99% 区间不含 0；切换前后下变差 3 个百分点以上算突破，同样只在两个时点判；非判读时点只报数）'
    done.append('表15 补普银圈入者行并改判读说明')

# 新增表16：破产者人均储值
name = '表16 破产者人均储值'
if name not in wb.sheetnames:
    idx = wb.index(wb['更正记录'])
    ws = wb.create_sheet(name, idx)
    ws.sheet_view.zoomScale = 140
    cell(ws, 1, 1, '表16　破产者人均储值（02 第四张卡主指标；08 M6，Q155 起）', FT, border=False)
    spec = [
        ('人群', '分到该组、从 D+1 起到本判读时点窗口末日之间至少破产 1 次的人（不论有没有买、有没有看到新排序）；上线前基线不分组，取切换前同长度窗口内破产者', False),
        ('每人一个值', '自首次破产起、落在储值类窗口内各日的全部储值金额，不分入口、不分品项；有时间戳从首次破产时刻算起，没有从当日算起，两组同一取法', False),
        ('名单', '破产者名单只含会员编号、分组、首次破产时间（会员编号不写进本表，只按名单联结储值订单取合计）', True),
        ('判读时点', '第 1 期末 = D+1 起第一个储值类窗口结束；合并 3 期 = 终点延到第三个储值类窗口结束，人群累计、每人只算一次', False),
        ('大户', '按 A34 前 134 人名单（上线前定）单列监测，不进检验；检验前按两组合并 P99 截尾', False),
        ('平衡核对', '每个判读时点先取「分到该组的在场人数」，比较两组「破产者 ÷ 分到该组的在场人数」，95% 区间；不含 0 时另取「排除第一、二张卡目标人群（新增、回流、储值下滑名单）后的破产者」一行', True),
    ]
    r = 3
    for k, v, y in spec:
        cell(ws, r, 1, k, FB)
        cell(ws, r, 2, v, F, YELLOW if y else None)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
        for cc in range(3, 7):
            ws.cell(row=r, column=cc).border = BD
        r += 1
    r += 1
    header = ['判读时点·分组', '分到该组的在场人数（平衡核对）', '分母：破产者人数', '分子：破产者储值合计（全部渠道）', '其中大户：人数与储值合计（单列）', '替代口径：排除第一、二张卡目标人群后的破产者人数与储值合计']
    for j, h in enumerate(header):
        cell(ws, r, 1 + j, h, FB, GRAY)
    ws.freeze_panes = ws.cell(row=r + 1, column=2)
    labels = ['上线前基线（不分组）', '第 1 期末·处理组', '第 1 期末·对照组', '合并 3 期·处理组', '合并 3 期·对照组']
    for lab in labels:
        r += 1
        cell(ws, r, 1, lab, FB)
        for j in range(1, len(header)):
            cell(ws, r, 1 + j, None, F, YELLOW)
    ws.column_dimensions['A'].width = 30
    for j in range(1, len(header)):
        ws.column_dimensions[chr(65 + j)].width = 34
    done.append('新增表16')

# 通用口径
ws = wb['通用口径']
if find_row(ws, '按 Q155 补（2026-09-30）') is None:
    r = ws.max_row + 1
    cell(ws, r, 1, '按 Q155 补（2026-09-30）', FB)
    cell(ws, r, 2, '表1 补回流任务发放点数列（监测）；表2、表3 补队列第 0–13 日储值列与大户行（第一张卡储值护栏）；表6、表7 改标分解项，表7 补其余品项行；新增表16（破产者人均储值，08 M6 新主指标）；表15 补普卡银卡圈入者一行。统计型护栏只在两个时点判（99%）。详见 分析/A36_验证计划.md、设计卡 Q155', F)
    done.append('通用口径补一行')

# 更正记录
cw = wb['更正记录']
if not any((cw.cell(r, 5).value or '').startswith('Q156') for r in range(1, cw.max_row + 1)):
    r = cw.max_row + 1
    row = ('2026-09-30', '表1、表2、表3、表6、表7、表15；新增表16；通用口径',
           '第四张卡主指标按「破产位内金额 ÷ 曝光次数（或破产事件数）」取数，表6、表7 是主指标分子分母，表7 无「其余品项」行；第一张卡没有储值护栏与回流任务发放点数的取数格；表15 缺普卡银卡圈入者（第二张卡护栏 ④ 的取数）；表15 护栏判读写 95%',
           '表16 新增（破产者人均储值，M6 新主指标）；表6、表7 改标分解项，表7 补其余品项行；表1 补发放点数列；表2、表3 补队列第 0–13 日储值列与大户行；表15 补普卡银卡圈入者一行，判读改两个时点、99%；通用口径补一行；所有新增格只留黄格，不填数',
           'Q156；设计卡 Q155；审查 R208、R211、R213；分析 A36')
    for i, v in enumerate(row, start=1):
        c = cw.cell(row=r, column=i)
        c.value = v
        c._style = copy(cw.cell(row=r - 1, column=i)._style)
    done.append('更正记录一行')

wb.save(P)
print('已改：', done or '无')
print(wb.sheetnames)
