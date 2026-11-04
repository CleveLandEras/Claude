# -*- coding: utf-8 -*-
"""Q154（审查 R206）：03 规则表补默认配法（随机对照，逐字取自 A36 各卡「三栏能写出吗 / 对照」格）、退路标注、新增「ID5 处理版」行、K5 第 0 步补分桶一句、A2 说明、提案表一行、更正记录一行。
不带参数运行；可重复运行（已有则跳过）。"""
import io
import os
from copy import copy
import openpyxl

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a36 = io.open(os.path.join(BASE, '分析', 'A36_验证计划.md'), encoding='utf-8').read()

# 与 A36 逐字一致的片段（断言它们确实出现在 A36 里）
S_ID5 = '对照组继续走原 ID5：对象「全部玩家」，排除栏加「分桶·处理」'
S_ID5B = '复制 ID5 为「ID5 处理版」，对象全部满足「分桶·处理」、排除「新增」「回流」（排序与各项设置照抄）'
S_NEW = '「新增用户活动弹窗」对象全部满足「新增」「分桶·处理」'
S_RET = '「回流用户活动弹窗」对象全部满足「回流」「分桶·处理」'
S_ID6 = '对照组继续走原 ID6，对象「全部玩家」，排除栏加「分桶·处理」'
S_ID6B = '处理组复制 ID6 为「ID6 处理版」（全部满足「分桶·处理」，排除金卡至至尊卡五项，排序照抄）'
S_ID6C = '「通用弹窗·金卡以上」「高卡储值下滑」两条各加「分桶·处理」到全部满足栏'
S_ID7 = 'ID7 对象「全部玩家」改为排除「分桶·处理」，另建「ID7 处理版」（全部满足「分桶·处理」，排序为新序）'
S_B = '「通用弹窗·金卡以上」的排除栏加「分桶·处理」，对照组继续走它；分档规则每档一条，对象全部满足「分桶·处理」、任一满足该档卡别、排除「当月储值额小于上月 50%」'
for s in (S_ID5, S_ID5B, S_NEW, S_RET, S_ID6, S_ID6B, S_ID6C, S_ID7, S_B):
    assert s in a36, ('A36 没有该片段', s[:40])

TAG = '默认配法（随机对照；推断，待运营核对）：'
RETREAT = '现行写法为退路（全量，走路 C）：分桶标签来不及建时用。'

p = os.path.join(BASE, '支撑文件', '03_弹窗配置单.xlsx')
wb = openpyxl.load_workbook(p)
ws = wb['规则']
done = []


def find_row(seq):
    for r in range(5, 20):
        if str(ws.cell(r, 1).value) == str(seq):
            return r
    raise AssertionError(('没找到序号', seq))


def append_k(seq, text):
    r = find_row(seq)
    c = ws.cell(r, 11)
    if TAG in (c.value or '') or '默认配法' in (c.value or ''):
        return False
    c.value = (c.value or '') + '。' + text
    return True


if '默认配法' not in (ws.cell(find_row(1), 11).value or ''):
    step0 = '第 0 步补：上线前先建「分桶·处理」（05 必建 1 个，谁写 SQL 见汇报第 9 件），并按 02 附录六核两组平衡；建不了时按退路全量上线，主指标最高判到「方向一致」，不挡第一批'
    append_k(1, TAG + S_ID5 + '；处理组：' + S_ID5B + '（见本表新增的「ID5 处理版」行）。' + RETREAT[:-1].replace('现行写法', '本行现行写法（对象「全部玩家，排除新增、回流」）') + '。' + step0)
    append_k(2, TAG + S_NEW + '；本行现行写法（对象「新增」）为退路（全量，走路 C）')
    append_k(3, TAG + S_RET + '；本行现行写法（对象「回流」）为退路（全量，走路 C）')
    # 第二张卡（序号 4–6）：按 A36 第二张卡格
    append_k(4, TAG + S_ID6 + '；' + S_ID6B + '。本行为等三处标签条件的批次，是否留对照在该批上线时定')
    append_k(5, TAG + S_ID6C.replace('两条各加', '两条各加（本行为其一）'))
    append_k(6, TAG + S_ID6C.replace('两条各加', '两条各加（本行为其一）'))
    # 第四张卡（序号 9）
    append_k(9, TAG + S_ID7)
    done.append('K 列默认配法（序号 1–6、9）')

# 新增「ID5 处理版」行：放在规则表最后一行之后
if not any('ID5 处理版' in str(ws.cell(r, 5).value or '') for r in range(5, ws.max_row + 1)):
    last = max(r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value is not None)
    src = find_row(3)
    r = last + 1
    vals = {
        1: '1′（仅默认配法）', 2: '新建', 3: None, 4: '活动类', 5: '活动类弹窗·处理版（复制 ID5）', 6: '大厅',
        7: '全部满足：分桶·处理；排除：新增、回流', 8: None, 9: 2,
        10: '复制 ID5 的排序与各项设置（时机、每日次数、冷却照抄）；仅在默认配法（随机对照）时新建，走退路（全量）时不需要本行',
        11: '第一批（默认配法）；与序号 1–3 同时上线；前提：已建「分桶·处理」标签（05 必建 1 个）；' + '（推断，待运营核对）',
        12: '第一张卡｜与序号 1–3 同一组验证指标（M2、M3、M1、M7）｜09 表 1、2、3、8',
    }
    for cidx, v in vals.items():
        c = ws.cell(r, cidx, v)
        c._style = copy(ws.cell(src, cidx)._style)
    done.append(f'规则表新增行 {r}（ID5 处理版）')

# A2
a2 = ws['A2'].value or ''
if '默认配法' not in a2:
    ws['A2'].value = a2 + ' 「默认配法」：02 各卡验证计划默认随机对照，需先建 1 个「分桶·处理」标签（05 必建 1 个），第一、二、四张卡各多复制 1 条规则作处理版；建不了或来不及时，按各行标注的「退路（全量，走路 C）」上线，主指标最高判到「方向一致」，不挡第一批上线。'
    done.append('A2')

# 提案表：加一行默认配法
wp = wb['提案（待主管定）']
if not any('默认配法' in str(wp.cell(r, 1).value or '') for r in range(1, wp.max_row + 1)):
    r = wp.max_row + 1
    wp.cell(r, 1, '默认配法（随机对照）')
    wp.cell(r, 2, TAG + S_B)
    for cidx in (1, 2):
        wp.cell(r, cidx)._style = copy(wp.cell(r - 1, cidx)._style)
    done.append('提案表 默认配法一行')

# 更正记录
wc = wb['更正记录']
if not any((wc.cell(r, 5).value or '').startswith('Q154') for r in range(1, wc.max_row + 1)):
    r = wc.max_row + 1
    rowvals = ['2026-09-30', '规则表 K5–K13、新增「ID5 处理版」行；A2；提案表',
               '第一批只写全量配法（序号 1 ID5 对象「全部玩家，排除新增、回流」，序号 2、3 对象「新增」「回流」），K5 第 0 步只核「带排除的群组」，没有分桶标签、没有对照组：02 默认随机对照，照 03 上线就没有对照组，且上线后补不回来',
               '序号 1–3、4–6、9 各加「默认配法（随机对照；推断，待运营核对）」，逐字取自 A36 各卡对照格；现行全量写法标为退路（走路 C）；新增「ID5 处理版」行（默认配法时新建）；K5 第 0 步补「先建分桶·处理，建不了按退路全量上线，主指标最高判到方向一致」；A2 同步；提案表补默认配法一行。批次与配置内容未改',
               'Q154；审查 R206；A36 各卡「三栏能写出吗 / 对照」；约束 80、99']
    for cidx, v in enumerate(rowvals, 1):
        cell = wc.cell(r, cidx, v)
        src = wc.cell(r - 1, cidx)
        if src.has_style:
            cell._style = copy(src._style)
    done.append(f'更正记录第 {r} 行')

wb.save(p)
print('已改：', done or '无')
for seq in (1, 2, 3, 4, 5, 6, 9):
    r = find_row(seq)
    print(seq, '|', (ws.cell(r, 11).value or '')[-140:])
