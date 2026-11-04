# 审定 13（第二级，11/04）：Dk 11/04 16:03「删掉「按人交接」这种功能，毫无意义」。
# 删按人交接、负责人、优先级被改的提醒。建实验、加进更多规则、保存冲突不删（第一级定）。
# 「最后修改人」「乙 15:05 保存过一版」是操作记录，不是分工，不删。「由快显负责」不是负责人，不动。
# 用法：先 cd 到 评审版_定稿改_1027/推送系统后台集成需求/，再 python3 -X utf8 这个文件。只能跑一次。
import os, re


def sub(s, a, b, n=1):
    assert s.count(a) == n, (a, s.count(a))
    return s.replace(a, b)


# ---- 文字稿
p = '需求评审版源.html'
s = open(p, encoding='utf8').read()
s = sub(s, '顶部右侧加「按人交接」「建实验」；场景设置入口下一行是优先级被改的提醒（丙调了进大厅优先级，你负责的回流被挡住的人数从约 1,200 变成约 4,290，可「去看」「知道了」），只给受影响规则的负责人看；搜索框旁加按状态筛选、按负责人筛选；名称一栏写编号和负责人；潜在流失里',
        '顶部右侧加「建实验」；搜索框旁加按状态筛选；名称一栏写编号；潜在流失里')
s, n = re.subn(r'[ \t]*<figure><div class="stt c">在列表点「按人交接」后</div>.*?</figure>\n', '', s, flags=re.S)
assert n == 1
s = sub(s, '（乙 · 10/30 15:05），下面是给负责人看的优先级被改的提醒。新建时', '（乙 · 10/30 15:05）。新建时')
s = sub(s, '，下面是负责人（默认创建人，本例甲）和备注（为什么这么配、对应哪份计划）；', '，下面是备注（为什么这么配、对应哪份计划）；')
s = sub(s, '负责人、提醒、实验、加进更多规则', '备注、实验、加进更多规则', 2)
s = sub(s, '选是才列出已结束的规则。；列表顶部右侧有「按人交接」「建实验」，搜索框旁可按状态、按负责人筛选；场景设置下一行是优先级被改的提醒，只给受影响规则的负责人看',
        '选是才列出已结束的规则。列表顶部右侧有「建实验」，搜索框旁可按状态筛选。')
s = sub(s, '每行写名称、编号、负责人、发送对象', '每行写名称、编号、发送对象')
s = sub(s, '<tr><td>负责人：每条规则有一个负责人，默认创建人，在名称段改；备注：0–200 字，写为什么这么配、对应哪份计划，复制规则时一起复制。列表顶部「按人交接」：选交接：原负责人、交接：接手人，列出原负责人的规则（默认全选），一次转给接手人；只改负责人，每条记一条操作纪录。</td></tr>',
        '<tr><td>备注：0–200 字，写为什么这么配、对应哪份计划，复制规则时一起复制。</td></tr>')
s, n = re.subn(r'[ \t]*<tr><td>优先级被改的提醒：.*?</td></tr>\n', '', s, flags=re.S)
assert n == 1
open(p, 'w', encoding='utf8').write(s)

# ---- 10a_弹窗列表
p = '需求评审版_原型/10a_弹窗列表.html'
s = open(p, encoding='utf8').read()
s = sub(s, '<span class="btno" style="margin-right:8px">按人交接</span>', '')
s, n = re.subn(r'<div style="[^"]*"><b>优先级被改的提醒</b>.*?</div>\n[ \t]*', '', s, flags=re.S)
assert n == 1
s = sub(s, '<span class="inp afl">按负责人筛选：全部<span class="dn">⌵</span></span>', '')
s = sub(s, '<th>名称、编号、负责人</th>', '<th>名称、编号</th>')
s, n = re.subn(r'(编号 \d+) · [甲乙丙]', r'\1', s)
assert n == 9, n
open(p, 'w', encoding='utf8').write(s)

# ---- 10_规则编辑
p = '需求评审版_原型/10_规则编辑.html'
s = open(p, encoding='utf8').read()
s, n = re.subn(r'<div style="[^"]*"><b>优先级被改的提醒</b>.*?</div>\n[ \t]*', '', s, flags=re.S)
assert n == 1
s, n = re.subn(r'[ \t]*<div class="row"><label>负责人</label>.*?按人交接」</span></div>\n', '', s, flags=re.S)
assert n == 1
open(p, 'w', encoding='utf8').write(s)

# ---- 按人交接的图
os.remove('需求评审版_图/10a5_按人交接.jpg')

# ---- 自查
for f in ['需求评审版源.html', '需求评审版_原型/10a_弹窗列表.html', '需求评审版_原型/10_规则编辑.html']:
    t = open(f, encoding='utf8').read()
    print(f, {k: t.count(k) for k in ['按人交接', '负责人', '优先级被改', '交接', '接手']})
