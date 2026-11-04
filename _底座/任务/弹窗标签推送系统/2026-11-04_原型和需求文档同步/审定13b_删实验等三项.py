# 审定 13b（第二级，11/04）：Dk 11/04 16:04「都删了」：建实验、加进更多规则、保存冲突也删。接在 审定13 后面跑。
# 不动（第一级定）：框架里原有的实验组、对照组群组和随机分组号，「实验」一节，上架确认。
# 「同事改过」「查版本」「打开后被改过的弹窗设置」都是保存冲突一家，基线 b0de2a35 里 0 处，是 p4改 加的，一起删。
# 备注不在 Dk 删的范围：页面字段和图说留着，规则从被删的小节挪到名称那一句后面（第二级定，可推翻）。
# 用法：先 cd 到 评审版_定稿改_1027/推送系统后台集成需求/，再 python3 -X utf8 这个文件。只能跑一次。
import os, re


def sub(s, a, b, n=1):
    assert s.count(a) == n, (a, s.count(a))
    return s.replace(a, b)


def drop_figure(s, alt):
    s, n = re.subn(r'[ \t]*<figure>(?:(?!</figure>).)*?alt="%s"(?:(?!</figure>).)*?</figure>\n' % alt, '', s, flags=re.S)
    assert n == 1, alt
    return s


# ---- 文字稿
p = '需求评审版源.html'
s = open(p, encoding='utf8').read()
s = sub(s, '顶部右侧加「建实验」；搜索框旁加按状态筛选；', '搜索框旁加按状态筛选；')
for alt in ['建实验', '加进更多规则', '保存冲突']:
    s = drop_figure(s, alt)
s = sub(s, '取自重叠人数）。保存时查本场景优先级顺序的版本：同事在你打开后保存过顺序时不按项合并，提示「放弃我的顺序，在最新顺序上重排」。', '取自重叠人数）。')
s = sub(s, '要客户端上报关闭）；底部左侧「加进更多规则」。', '要客户端上报关闭）。')
s = sub(s, '新增玩家被挡的会多约 60 人）。选位置时查本场景优先级顺序的版本：打开后同事保存过顺序时不合并，提示「放弃我的顺序，在最新顺序上重排」，再选位置。背后编辑页', '新增玩家被挡的会多约 60 人）。背后编辑页')
s = sub(s, ' · 备注、实验、加进更多规则 · 保存与测试', ' · 保存与测试')
s = sub(s, '（改前、改后）。保存场景设置时查场景设置的版本，被同事改过的先到保存冲突。', '（改前、改后）。')
s = sub(s, '列表顶部右侧有「建实验」，搜索框旁可按状态筛选。', '搜索框旁可按状态筛选。')
s = sub(s, '。保存时查这份设置的版本，被同事改过先到保存冲突；引用它的规则不因此冲突，规则保存确认顶部列出「打开后被改过的弹窗设置」。', '。')
s, n = re.subn(r'[ \t]*<h4 class="rg">备注、实验、加进更多规则</h4>\n[ \t]*<table class="rule">.*?</table>\n', '', s, count=1, flags=re.S)
assert n == 1
s, n = re.subn(r'[ \t]*<tr><td>保存冲突：.*?</td></tr>\n', '', s, count=1, flags=re.S)
assert n == 1
s = sub(s, '挡住它的规则。选位置时查本场景优先级顺序的版本，被同事改过时不合并，提示「放弃我的顺序，在最新顺序上重排」，再选位置。', '挡住它的规则。')
s = sub(s, '默认「发送对象群组名·场景」，改过的以改的为准。', '默认「发送对象群组名·场景」，改过的以改的为准。备注：0–200 字，写为什么这么配、对应哪份计划，复制规则时一起复制。')
open(p, 'w', encoding='utf8').write(s)

# ---- 页面
p = '需求评审版_原型/10a_弹窗列表.html'
s = open(p, encoding='utf8').read()
s = sub(s, '<span class="btno" style="margin-right:8px">建实验</span>', '')
open(p, 'w', encoding='utf8').write(s)

p = '需求评审版_原型/10a2_按活动筛选后改弹窗设置.html'
s = open(p, encoding='utf8').read()
s = sub(s, '<span class="lk" style="margin-right:auto">＋ 加进更多规则</span>', '')
open(p, 'w', encoding='utf8').write(s)

p = '需求评审版_原型/10a3_保存顺序确认.html'
s = open(p, encoding='utf8').read()
s = sub(s, '确认后记一条操作纪录。保存时查本场景顺序的版本：同事在你打开后保存过顺序时不合并，提示「放弃我的顺序，在最新顺序上重排」', '确认后记一条操作纪录。')
open(p, 'w', encoding='utf8').write(s)

p = '需求评审版_原型/11_保存确认.html'
s = open(p, encoding='utf8').read()
s = sub(s, '玩家下一次进入场景起按新设置；改了什么和最新版比。', '玩家下一次进入场景起按新设置。')
s, n = re.subn(r'[ \t]*<div class="imp">打开后被改过的弹窗设置：.*?</div>\n', '', s, count=1, flags=re.S)
assert n == 1
open(p, 'w', encoding='utf8').write(s)

# ---- 图
for f in ['10a4_建实验.jpg', '10a6_加进更多规则.jpg', '11a_保存冲突.jpg']:
    os.remove('需求评审版_图/' + f)

# ---- 自查
words = ['按人交接', '负责人', '优先级被改', '建实验', '加进更多规则', '保存冲突', '同事', '打开后被改过', '最新版', '放弃我的']
for f in ['需求评审版源.html', '需求评审版_原型/10a_弹窗列表.html', '需求评审版_原型/10a2_按活动筛选后改弹窗设置.html', '需求评审版_原型/10a3_保存顺序确认.html', '需求评审版_原型/11_保存确认.html']:
    t = open(f, encoding='utf8').read()
    print(f, {k: t.count(k) for k in words if t.count(k)})
