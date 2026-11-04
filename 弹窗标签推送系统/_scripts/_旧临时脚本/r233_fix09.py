import copy
import openpyxl

p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/09_取数需求_上线前基线.xlsx'
wb = openpyxl.load_workbook(p)

MARK = 'R233'


def copy_style(src, dst):
    dst.font = copy.copy(src.font)
    dst.fill = copy.copy(src.fill)
    dst.border = copy.copy(src.border)
    dst.alignment = copy.copy(src.alignment)
    dst.number_format = src.number_format


def patch(sheet, who, day):
    ws = wb[sheet]
    if ws['A4'].value:
        print(sheet, '已改过，跳过')
        return
    ws['A4'] = '储值窗口（R233）'
    ws['B4'] = (
        f'基线：{who} D-27 至 D-14，观察至 D-1（每人第 0–13 日储值取齐，第 13 日不晚于 D-1）。'
        '留存仍用上一行窗口，两个窗口分开取。'
        f'D 列只填{day} D-21 至 D-14 各行；D-13 至 D-8 各行的 D 列不填（其第 13 日落在切换后）。'
        '下面检验用数块的「上线前基线」一行按本行窗口取（D-27 至 D-14 全部队列），不是按留存窗口取。'
        '上线后：每期队列最后一日再过 13 日，储值才取齐，储值护栏的取数在此之后；'
        '是否要因此把第 1 期末的判读时点整体后移，属判读合同，交设计者（见审查 R233）。'
    )
    copy_style(ws['A3'], ws['A4'])
    copy_style(ws['B3'], ws['B4'])
    ws['D5'] = ws['D5'].value + '；只填 D-21 至 D-14 各行，见第 4 行'
    a23 = ws['A23'].value
    ws['A23'] = a23 + '本块人群按第 4 行「储值窗口」取（基线 D-27 至 D-14），不按第 3 行留存窗口取。'


patch('表2 新增7日留存', '注册日', '注册日')
patch('表3 回流7日留存', '回流判定日', '回流判定日')

ws = wb['更正记录']
if not any('R233' in str(ws.cell(r, 5).value) for r in range(4, ws.max_row + 1)):
    r = ws.max_row + 1
    vals = [
        '2026-09-30',
        '表2、表3 窗口行、D5、A23',
        '第 0–13 日储值的队列沿用留存窗口（D-21 至 D-8，观察至 D-1），D-13 至 D-8 进来的人第 13 日落在切换后，取不满 14 天，数据组只能少算或混进切换后数据；上线后也没写储值观察到哪一天',
        '两个窗口分开写：留存窗口不变；新增第 4 行「储值窗口」——基线 D-27 至 D-14 观察至 D-1，D 列只填 D-21 至 D-14 各行，检验用数块基线一行按新窗口取；上线后每期队列最后一日再过 13 日储值才取齐。第 1 期末判读时点是否后移，不自行定，交设计者',
        '审查 R233；设计卡 Q155；约束 100',
    ]
    for i, v in enumerate(vals, start=1):
        c = ws.cell(r, i, v)
        copy_style(ws.cell(r - 1, i), c)

wb.save(p)

wb2 = openpyxl.load_workbook(p)
print(wb2.sheetnames)
for s in ['表2 新增7日留存', '表3 回流7日留存']:
    print(s, wb2[s]['A4'].value, '|', wb2[s]['D5'].value)
for s in ['表1 回流任务参与率', '表9 储值类主指标基线', '表13 圈入者观察月人均储值', '表14 提案乙过程指标', '表16 破产者人均储值']:
    print(s, '在', wb2[s].max_row)
print('更正记录行数', wb2['更正记录'].max_row)
