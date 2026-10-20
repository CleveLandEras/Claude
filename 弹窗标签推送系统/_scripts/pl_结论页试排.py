import sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from an_呈交版V2_版式库 import *
from pptx.enum.shapes import MSO_SHAPE
GREEN = '2F6B52'; GREEN_W = 'E2EFE8'
prs = new_prs(); s = new_slide(prs)
header(s, '结论', '弹窗分人群现有后台就能配；推送统一、每日上限与交集需新建能力', BLUE, 2)
TOP, H = 2.15, 3.55
def side(x, lab, col, lines):
    box(s, x, TOP, 3.55, H, fill=CARD, line=col, lw=1.25, radius=0.03)
    rect(s, x, TOP, 3.55, 0.08, col)
    text(s, x + 0.38, TOP + 0.38, 3.0, 0.45, lab, size=20, color=col, bold=True)
    for i, t in enumerate(lines):
        text(s, x + 0.38, TOP + 1.2 + i * 0.72, 3.0, 0.45, t, size=17, color=NAVY, bold=True)
side(0.9, '现在', RED, ['所有玩家看同一套弹窗', '五种推送分在三处配置', '两类目标人群没有标签'])
side(8.88, '目标', BLUE, ['五类人群各看一套弹窗', '推送一处配置、按人群发', '五类人群都能圈出'])
text(s, 4.7, TOP - 0.05, 3.95, 0.35, '原因  →  做法', size=14, color=GRAY, bold=True, align=PP_ALIGN.CENTER)
def lane(y, col, wash, head, sub):
    sp = s.shapes.add_shape(MSO_SHAPE.PENTAGON, Inches(4.7), Inches(y), Inches(3.95), Inches(1.4))
    sp.fill.solid(); sp.fill.fore_color.rgb = rgb(wash); sp.line.fill.background(); sp.shadow.inherit = False
    sp.adjustments[0] = 0.18
    text(s, 4.95, y + 0.24, 3.2, 0.45, head, size=17, color=col, bold=True)
    text(s, 4.95, y + 0.76, 3.25, 0.6, sub, size=14, color=INK, line=1.25)
lane(TOP + 0.45, GREEN, GREEN_W, '只缺配置 → 现有后台直接配', '按五类人群分组配置；新建两类标签')
lane(TOP + 2.15, AMBER, AMBER_W, '缺功能 → 新建能力', '每日上限、新手弹窗接入、\n推送统一后台、群组交集')
out = sys.argv[1]; prs.save(out); print('saved', out)
