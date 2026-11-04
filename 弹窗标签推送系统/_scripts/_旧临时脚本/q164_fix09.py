"""Q164：09 补「各人均金额表的标准差与截尾值」（约束 108；守约束 98：接在 q162_fix09.py 之后运行，不重生成）。
表2、表3：在表末加汇总块（组 / 队列人数 / 截尾后第 0–13 日储值合计 / 截尾后每人值标准差 / 两组合并 P99 截尾值）；
表9、表13：表头右边补三列（截尾后储值合计、截尾后每人值标准差、P99 截尾值）；
表14（过程指标，不做区间判读）、表16（Q162 已补）不动。通用口径与更正记录各追加一行。
不带参数；可重复运行（已有则跳过）；只补黄格与口径说明，不填数值。运行后读回核对。"""
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
TAG = 'Q164 补'

# 表2、表3：汇总块
for name, who in (('表2 新增7日留存', '新增'), ('表3 回流7日留存', '回流')):
    ws = wb[name]
    if find_row(ws, TAG + '：' + who + '队列储值护栏的检验用数') is None:
        r = 22
        cell(ws, r, 1, TAG + '：' + who + '队列储值护栏的检验用数', FB, border=False)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
        r += 1
        cell(ws, r, 1, '说明：上表 D 列是按日的合计，算不出区间；区间要按人算，所以另列本块。每人一个值 = 自注册日 / 回流判定日（第 0 日）起第 0–13 日储值合计（含没付费的人，记 0）；人群 = 该队列全部人。检验前按两组合并 P99 截尾（两组同一截尾值），截尾后的合计与标准差按截尾后的每人值计；截尾值另列一格。大户按 A34 名单单列监测，不进本块。新增、回流两队列合起来算一个检验，由两块的人数、合计、标准差合并得出。', F, border=False)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
        ws.row_dimensions[r].height = 96
        r += 1
        heads = ['分组（判读时点）', '队列人数（全部人）', '截尾后第 0–13 日储值合计', '截尾后每人值的标准差', '两组合并 P99 截尾值']
        for j, h in enumerate(heads):
            cell(ws, r, 1 + j, h, FB, GRAY)
        for lab in ('上线前基线（不分组）', '第 1 期末·处理组', '第 1 期末·对照组', '合并 3 期·处理组', '合并 3 期·对照组'):
            r += 1
            cell(ws, r, 1, lab, FB)
            for j in range(1, 5):
                cell(ws, r, 1 + j, None, F, YELLOW)
        for col in 'BCDE':
            ws.column_dimensions[col].width = max(ws.column_dimensions[col].width or 0, 30)
        done.append(name + ' 补检验用数块')

# 表9、表13：表头右边补三列
for name, hdr_text, first_data, last_data in (
        ('表9 储值类主指标基线', '人群', 8, 11),
        ('表13 圈入者观察月人均储值', '卡别组', 10, 11)):
    ws = wb[name]
    # 表头行写死（表9 第 4 行也叫「人群」且正文含「分母」，按文字找会找错，q164b_fix09.py 已修复一次误写）
    hr = first_data - 1
    if ws.cell(hr, 5).value is None:
        heads = [TAG + '：截尾后储值总额（两组合并 P99 截尾）', TAG + '：截尾后每人值的标准差', TAG + '：P99 截尾值（两组合并；各取数点各一格）']
        for j, h in enumerate(heads):
            cell(ws, hr, 5 + j, h, FB, GRAY)
            ws.column_dimensions[chr(69 + j)].width = 34
        for rr in range(hr + 1, ws.max_row + 1):
            if ws.cell(rr, 1).value:
                for j in range(3):
                    cell(ws, rr, 5 + j, None, F, YELLOW)
        done.append(name + ' 补三列')

ws = wb['通用口径']
if find_row(ws, '按约束 108 补（2026-09-30）') is None:
    r = ws.max_row + 1
    cell(ws, r, 1, '按约束 108 补（2026-09-30）', FB)
    cell(ws, r, 2, '各人均金额类表（凡 02 验证计划里按「人均储值 / 人均金额」做区间判读的指标）补截尾后标准差与截尾值：表2、表3 末尾加检验用数块，表9、表13 表头右边补三列，表16 已由 Q162 补；表14（分档礼包购买人数与金额，过程指标）不做区间判读，不补。区间按人算，所以标准差按截尾后的每人值计；两组合并 P99 截尾，截尾值另列。数据组若给不出按人的标准差，退路是给「会员编号 + 分组 + 每人值」名单（只含会员编号）由我们算；能否取到待确认（数据组）', F)
    done.append('通用口径补一行')

cw = wb['更正记录']
if not any((cw.cell(r, 5).value or '').startswith('Q164') for r in range(1, cw.max_row + 1)):
    r = cw.max_row + 1
    row = ('2026-09-30', '表2、表3、表9、表13；通用口径',
           '这四张表只取合计（或按日合计），算不出按人的区间；02 验证计划里第一张卡储值护栏、第二张卡与提案乙主指标都写「按人算 99% / 95% 区间」，数据组照 09 取完，上线后区间一个也算不出来',
           '表2、表3 末尾加检验用数块（人数、截尾后合计、截尾后标准差、截尾值，基线 / 处理 / 对照 × 两个判读时点）；表9、表13 表头右边补截尾后储值总额、标准差、截尾值三列；表14 不补（过程指标）；通用口径补一行；新增格只留黄格，不填数',
           'Q164；约束 108；设计卡 Q160 子问题三；分析 A36')
    for i, v in enumerate(row, start=1):
        c = cw.cell(row=r, column=i)
        c.value = v
        c._style = copy(cw.cell(row=r - 1, column=i)._style)
    done.append('更正记录一行')

wb.save(P)
print('已改：', done or '无')
print(wb.sheetnames)
for n in ['表1', '表2', '表3', '表5', '表6', '表7', '表13', '表14', '表15', '表16']:
    ok = any(s.startswith(n + ' ') for s in wb.sheetnames)
    print(n, '在' if ok else '缺！')
for name in ('表2 新增7日留存', '表9 储值类主指标基线', '表13 圈入者观察月人均储值'):
    ws = wb[name]
    print('---', name)
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
        vals = [(str(c.value)[:26] if c.value is not None else '') for c in row[:8]]
        if any(vals) and (row[0].row >= 5):
            print(row[0].row, ' | '.join(vals))
