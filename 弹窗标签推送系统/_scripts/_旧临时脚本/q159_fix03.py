"""Q159：03 按审查 R221 改 K5–K7 的重复退路句与 J5；L5/L7 同步 Q155 的护栏写法；更正记录追加一行。可重复运行。"""
import openpyxl
from copy import copy

P = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(P)
ws = wb['规则']
done = []


def rep(cell, old, new):
    v = ws[cell].value
    if v and old in v:
        ws[cell].value = v.replace(old, new)
        done.append(cell)


rep('K5', '本行现行写法（对象「全部玩家，排除新增、回流」）为退路（全量，走路 C）：分桶标签来不及建时用。', '')
rep('K6', '；本行现行写法（对象「新增」）为退路（全量，走路 C）', '')
rep('K7', '；本行现行写法（对象「回流」）为退路（全量，走路 C）', '')
if ws['J5'].value and '此为退路写法' in ws['J5'].value:
    ws['J5'].value = '仅改对象，排序与各项设置不变（两种配法都是）'
    done.append('J5')
rep('L5', '护栏：M7｜', '护栏：新增、回流人均储值不低于对照、M8、M7；监测：回流任务赠点发放量｜')
rep('L6', '护栏：M7｜', '护栏：新增人均储值不低于对照、M8、M7｜')
rep('L7', '（同时是护栏）；过程：M1；护栏：M7｜', '（其「不过」由主指标规则覆盖）；过程：M1；护栏：回流人均储值不低于对照、M8、M7；监测：回流任务赠点发放量｜')

cw = wb['更正记录']
if not any((cw.cell(r, 5).value or '').startswith('Q159') for r in range(1, cw.max_row + 1)):
    r = cw.max_row + 1
    row = ('2026-09-30', '规则表 K5、K6、K7、J5；L5、L6、L7',
           'K5–K7 末尾各有「本行现行写法……为退路」半句，而 G 列已是默认配法，退路已在 K 列开头写明，同一格出现两次退路且「现行写法」指向不清；J5 写「此为退路写法」，与 G5 默认配法对不上；L 列护栏还是 Q155 前的写法',
           'K5–K7 删去重复的半句，退路只留开头「退路对象」一处；J5 改为「仅改对象，排序与各项设置不变（两种配法都是）」；L5–L7 护栏写法按 02 现行（统计型储值护栏与 M8、配置核对 M7、赠点监测；M3 不再兼按护栏判）。批次与配置内容未改',
           'Q159；审查 R221；设计卡 Q155')
    for i, v in enumerate(row, start=1):
        c = cw.cell(row=r, column=i)
        c.value = v
        c._style = copy(cw.cell(row=r - 1, column=i)._style)
    done.append('更正记录一行')
wb.save(P)
print('已改：', done or '无')
