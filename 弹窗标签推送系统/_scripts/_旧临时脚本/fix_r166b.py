"""R166–R171 处理的第二部分（08、A31、03、09）。汇报与 02 已由 fix_r166.py 写入。不带参数。"""
import openpyxl
from copy import copy

B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
P08 = B + '支撑文件/08_弹窗效果评估方案.md'
PA31 = B + '分析/A31_决策点选项.md'
P03 = B + '支撑文件/03_弹窗配置单.xlsx'
P09 = B + '支撑文件/09_取数需求_上线前基线.xlsx'


def rep(text, old, new, n=1):
    assert text.count(old) == n, (text.count(old), old[:60])
    return text.replace(old, new)


e = open(P08, encoding='utf-8').read()
e = rep(e, 'ID6 曝光另行报告，不计入对照',
        '储值位（ID6、通用弹窗·金卡以上、高卡储值下滑）曝光另行报告，不计入活动类对照；金卡以上储值下滑者按 02 第二张卡评估重点单列人均每日储值位 + 活动类曝光，与切换前对照')
e = e.rstrip('\n') + '\n| 2026-09-30 | M7 指标定义末句 | 「ID6 曝光另行报告，不计入对照」：第二张卡拆出「通用弹窗·金卡以上」「高卡储值下滑」两条储值位规则后，储值位曝光只提到 ID6，看不出金卡以上下滑者的储值位有没有多弹 | 储值位三条规则的曝光另行报告；金卡以上储值下滑者单列人均每日储值位 + 活动类曝光，与切换前对照；分母、窗口未改 | 审查 R170；02 第二张卡评估重点 |\n'
open(P08, 'w', encoding='utf-8').write(e)

a = open(PA31, encoding='utf-8').read()
a = rep(a, '- 2026-09-30（推进计划 Q115）：新增「Q115」一节',
        '- 2026-09-30（审查 R167）：S6 里「群组的排除栏一次只能排除单个标签」以 02 改后写法为准：排除栏是「命中栏内任一标签即排除」，不能排除「且」组合。\n'
        '- 2026-09-30（推进计划 Q115）：新增「Q115」一节')
open(PA31, 'w', encoding='utf-8').write(a)

wb = openpyxl.load_workbook(P03)
ws = wb['规则']
k8 = ws['K8'].value
assert '与序号 4、5、6 同时上线' in k8
ws['K8'].value = k8 + '；「全部玩家，排除金卡至至尊卡」不能选作弹窗对象时，先新建标签「非金卡以上」作本行对象（谁写 SQL：见汇报第 9 件）'
cw = wb['更正记录']
r = cw.max_row + 1
for i, v in enumerate(['2026-09-30', '规则表第 4 行（通用弹窗）K 列', '批次说明没有写「全部玩家，排除…」不能选作弹窗对象时怎么办', '补退路：先新建标签「非金卡以上」作本行对象', '审查 R169；02 第二张卡前置条件'], start=1):
    c = cw.cell(row=r, column=i)
    c.value = v
    c._style = copy(cw.cell(row=r - 1, column=i)._style)
cw.row_dimensions[r].height = 48
wb.save(P03)

w9 = openpyxl.load_workbook(P09)
s8 = w9['表8 人均每日曝光']
assert s8['D9'].value == 'ID6 弹窗曝光次数（另行报告）', s8['D9'].value
s8['D9'].value = '储值位弹窗曝光次数（ID6、通用弹窗·金卡以上、高卡储值下滑；另行报告）'
c9 = w9['更正记录']
r = c9.max_row + 1
for i, v in enumerate(['2026-09-30', '表8 D9 列标题', '「ID6 弹窗曝光次数（另行报告）」', '「储值位弹窗曝光次数（ID6、通用弹窗·金卡以上、高卡储值下滑；另行报告）」', '审查 R170；08 M7'], start=1):
    c = c9.cell(row=r, column=i)
    c.value = v
    c._style = copy(c9.cell(row=r - 1, column=i)._style)
w9.save(P09)
print('第二部分写回')
