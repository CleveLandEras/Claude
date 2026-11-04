"""R229 尾项（按审查 12:40 对计划意见 1 的检索建议）：03 L8–L10 第二张卡仍写「护栏：M7」，同步 02 现行。不带参数运行。"""
import os, copy, openpyxl
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, '支撑文件', '03_弹窗配置单.xlsx')
wb = openpyxl.load_workbook(p)
ws = wb['规则']
old = '过程：M4；护栏：M7｜09 表 4、8、11'
new = '过程：M4；统计型护栏：M8 关闭率、再登录率；配置核对：M7（金卡以上下滑者单列）｜09 表 4、8、11、15'
for c in ('L8', 'L9', 'L10'):
    assert old in ws[c].value, c
    ws[c] = ws[c].value.replace(old, new)
lg = wb['更正记录']
r = lg.max_row + 1
vals = ('2026-09-30', '规则表 L8、L9、L10（第二张卡）',
        '过程：M4；护栏：M7｜09 表 4、8、11',
        '过程：M4；统计型护栏：M8 关闭率、再登录率；配置核对：M7（金卡以上下滑者单列）｜09 表 4、8、11、15',
        '审查 12:40 对计划意见 1（检索「护栏：M7」）；02 第二张卡现行；环节3 第二节 ① 表已同步（R227）')
for j, v in enumerate(vals):
    d = lg.cell(row=r, column=j + 1, value=v)
    d._style = copy.copy(lg.cell(row=r - 1, column=j + 1)._style)
wb.save(p)
print('ok')
