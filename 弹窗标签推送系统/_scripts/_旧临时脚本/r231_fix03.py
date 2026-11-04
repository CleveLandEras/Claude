"""R231：03 K5、K14 补「全部满足 + 排除」不能并用时的合并标签退路（照 05 v2.5 前置条件行）；03 更正记录一行。
不带参数；可重复运行（已有则跳过）；不改其他格。做完读回 K5、K14。"""
import openpyxl
from copy import copy

P = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(P)
ws = wb['规则']
done = []

ADD = '不能时，第 14 行对象改用合并标签「分桶·处理且非新增、非回流」（多 1 个 SQL 标签，谁写见汇报第 9 件；序号 2、3 不受影响），也建不了才按退路全量上线。'

k5 = ws.cell(5, 11).value or ''
anchor = '运营上线前核对能否这样选。'
if '分桶·处理且非新增、非回流' not in k5 and anchor in k5:
    ws.cell(5, 11).value = k5.replace(anchor, anchor + ADD, 1)
    done.append('K5')

k14 = ws.cell(14, 11).value or ''
if '分桶·处理且非新增、非回流' not in k14:
    ws.cell(14, 11).value = k14.replace('（推断，待运营核对）', '（推断，待运营核对）；若「全部满足 + 排除」不能同时用：对象改用合并标签「分桶·处理且非新增、非回流」（多 1 个 SQL 标签，谁写见汇报第 9 件），也建不了才按退路全量上线（05 v2.5 前置条件表）', 1) if '（推断，待运营核对）' in k14 else k14 + '；若「全部满足 + 排除」不能同时用：对象改用合并标签「分桶·处理且非新增、非回流」（多 1 个 SQL 标签，谁写见汇报第 9 件），也建不了才按退路全量上线（05 v2.5 前置条件表）'
    done.append('K14')

# L8–L10 补 M9 编号（审查 12:54 R229 小瑕疵）
for r in (8, 9, 10):
    v = ws.cell(r, 12).value or ''
    if '统计型护栏：M8 关闭率、再登录率' in v:
        ws.cell(r, 12).value = v.replace('统计型护栏：M8 关闭率、再登录率', '统计型护栏：M8 关闭率、M9 再登录率', 1)
        done.append('L%d 补 M9' % r)

cw = wb['更正记录']
hdr = [c.value for c in cw[1]]
hr = None
for r in range(1, min(cw.max_row, 8) + 1):
    if cw.cell(r, 1).value in ('日期',) or (cw.cell(r, 1).value or '').startswith('日期'):
        hr = r
        break
print('更正记录表头行：', hr, [c.value for c in cw[hr]] if hr else hdr)
last = cw.max_row
print('更正记录最后一行：', [str(c.value)[:30] for c in cw[last]])
if not any('R231' in str(cw.cell(r, c).value or '') for r in range(1, cw.max_row + 1) for c in range(1, cw.max_column + 1)):
    r = last + 1
    ncol = cw.max_column
    vals = ['2026-09-30', 'K5、K14（规则表）；L8–L10',
            'K5 只写「运营上线前核对能否这样选」，紧接「建不了时按退路全量上线」；K14 前提只写「已建『分桶·处理』标签」：核对不通过时最顺手的读法是走退路，也就是放弃对照组；L8–L10 写「M8 关闭率、再登录率」没标 M9',
            'K5 补「不能时，第 14 行对象改用合并标签『分桶·处理且非新增、非回流』（多 1 个 SQL 标签），也建不了才按退路全量上线」；K14 补同一句；L8–L10 补 M9 编号。批次与配置内容未改',
            '审查 R231、R229 小瑕疵；05 v2.5 前置条件表；执行者第四十五次规划后自查']
    for i in range(ncol):
        c = cw.cell(row=r, column=i + 1)
        c.value = vals[i] if i < len(vals) else None
        c._style = copy(cw.cell(row=last, column=i + 1)._style)
    done.append('更正记录一行')

wb.save(P)
print('已改：', done or '无')
print('K5:', ws.cell(5, 11).value[-420:])
print('K14:', ws.cell(14, 11).value)
for r in (8, 9, 10):
    print('L%d:' % r, ws.cell(r, 12).value)
