#!/usr/bin/env python3
"""Q242：阶段2、阶段3 按层级重排（工作原则 v4.12）。只改组织方式与排版，不改结论和数字。
- 追加 tree/cap 样式；首屏加结构总览；各节加锚点
- 阶段3 第七节：按需求分析 5 项能力分组，原行 HTML 原样搬入
重排前备份到 _versions/。"""
import os, re, shutil

ROOT = '/Users/decheng.huang/claude/弹窗标签推送系统'
P2 = os.path.join(ROOT, '阶段2_人群分析.html')
P3 = os.path.join(ROOT, '阶段3_现状盘点.html')
P1 = os.path.join(ROOT, '阶段1_需求分析.html')
VER = os.path.join(ROOT, '_versions')
os.makedirs(VER, exist_ok=True)
shutil.copy(P2, os.path.join(VER, '阶段2_人群分析_重排前_1008.html'))
shutil.copy(P3, os.path.join(VER, '阶段3_现状盘点_重排前_1008.html'))

# 取阶段1 范例里 tree/cap 样式
css1 = open(P1, encoding='utf-8').read()
m = re.search(r'(\.tree\{.*?\.cap-v b\{[^}]*\})', css1, re.S)
assert m, 'css not found'
TREE_CSS = m.group(1) + '\n.tree li ul{margin:4px 0 4px}.tree li>b{font-weight:700}\n'

NUM = '一二三四五六七八'


def add_css(h):
    if '.tree{' in h:
        return h
    return h.replace('</style>', TREE_CSS + '</style>', 1)


def add_ids(h, n):
    for i in range(n):
        old = '<section class="sec"><div class="sec-h"><span class="sec-no">%s</span>' % NUM[i]
        new = '<section class="sec" id="s%d"><div class="sec-h"><span class="sec-no">%s</span>' % (i + 1, NUM[i])
        assert old in h, old
        h = h.replace(old, new, 1)
    return h


# ---------------- 阶段 2 ----------------
h = open(P2, encoding='utf-8').read()
h = add_css(h)
h = add_ids(h, 6)
tree2 = '''<div class="tree">
<p class="goal">人群分析：弹窗与推送面向的五类目标人群，以及五类以外的人群<small>分母：近一月活跃 62,292 人（已剔除機器人、測試帳號）；每类人群的口径、画像、重叠见第一至三节，覆盖与可达见第四、五节。</small></p>
<ul>
<li><b>五类目标人群</b>　<span class="d">口径→<a href="#s1">第一节</a> · 画像→<a href="#s2">第二节</a> · 重叠→<a href="#s3">第三节</a></span>
<ul>
<li><b>新增</b>　<span class="d">10,749 人（17.26%）· 口径已证实</span></li>
<li><b>回流</b>　<span class="d">存量 16,564 人、在场 8,022 人 · 回来后首次登录的事件口径不可知</span></li>
<li><b>潜在付费</b>　<span class="d">5,976 人（可核实）—25,972 人（上界）· 推断</span></li>
<li><b>潜在流失</b>　<span class="d">规模不可知，参照 13,449—18,265 人 · 推断</span></li>
<li><b>破产</b>　<span class="d">规模不可知，暴露范围 0—34,363 人 · 推断</span></li>
</ul></li>
<li><a href="#s4">五类以外的人群</a>　<span class="d">在场用户中 1,059—20,768 人（占在场 34,363 的 3.08%—60.44%）</span></li>
<li><a href="#s5">弹窗够不到的离线人群</a>　<span class="d">最后登录 ≥ 8 天 40,117 人（下界；真离开者更少，推断）</span></li>
<li><a href="#s6">关键假设</a>　<span class="d">10 项推断，推错时改规模与重叠，五类划分不变</span></li>
</ul>
</div>

'''
anchor = '<div class="summary"><dl>'
assert h.count(anchor) == 1
h = h.replace(anchor, tree2 + anchor, 1)
open(P2, 'w', encoding='utf-8').write(h)

# ---------------- 阶段 3 ----------------
h = open(P3, encoding='utf-8').read()
h = add_css(h)
h = add_ids(h, 8)

# 第一节三张表加小标题
subs = [
    ('<div class="tw"><table>\n<tr><th>规则</th>', '后台规则'),
    ('<div class="tw"><table>\n<tr><th>机制</th>', '规则机制'),
    ('<div class="tw"><table>\n<tr><th>内容池</th>', '内容池与礼包'),
]
for old, label in subs:
    assert h.count(old) == 1, old
    h = h.replace(old, '<p class="sec-sub"><b>%s</b></p>\n%s' % (label, old), 1)

# 第七节：抽出场景行
s7_start = h.index('<section class="sec" id="s7">')
s7_end = h.index('</section>', s7_start) + len('</section>')
s7 = h[s7_start:s7_end]
rows = {}
for line in s7.split('\n'):
    mm = re.match(r'<tr><td><span class="chip">(\d+)</span>', line)
    if mm:
        rows[int(mm.group(1))] = line
assert sorted(rows) == list(range(1, 26)), sorted(rows)

caps = [
    ('c1', '能力 1', '人群圈选', '运营可以：用标签圈出任一目标人群，看到规模与口径；人群之间可做交集、排除',
     [9, 10, 20, 21],
     '4 个场景全部推断可实现：且、或已记载；排除条件、标签规模查询与剔除机器人、测试账号为推断或未知；群组之间的交集尚无，可由标签「且」或排除达到同一结果。'),
    ('c2', '能力 2', '分人群内容配置', '运营可以：为五类人群分别配置弹窗内容，并能自助调整弹窗图文与新手弹窗',
     [1, 2, 3, 4, 5, 17, 18],
     '场景 1、3 可实现；2、4、5、18 推断可实现；17 的新手弹窗写死在客户端，不可实现（记载）。'),
    ('c3', '能力 3', '触达量与顺序控制', '运营可以：事前限定单人弹窗与推送的数量、先后和合计上限，改动前可测算影响',
     [6, 7, 8, 13, 16, 19],
     '场景 6、8 推断可实现（逐规则约束、手工测算）；7、13、16、19 推断不可实现，均为无记载的能力按推断处理，若实际有该能力则可实现。'),
    ('c4', '能力 4', '统一推送', '运营可以：在单一入口配置全部推送通路，按标签定向发送，支持跳转与行为触发',
     [11, 12, 22, 23],
     '场景 12 推断可实现；11 不可实现（记载：各功能各一套推送、快显写死在客户端）；22、23 推断不可实现。'),
    ('c5', '能力 5', '效果查看', '运营可以：查看推送到达与点击、弹窗曝光与点击购买，并能分组对照判断改动效果',
     [14, 15, 24, 25],
     '场景 15、24 推断可实现；14、25 推断不可实现（推送发送、到达、点击无数据）。'),
]
assert sorted(sum([c[4] for c in caps], [])) == list(range(1, 26))


def count(ids):
    tags = {'可实现': 0, '推断可实现': 0, '不可实现（记载）': 0, '推断不可实现': 0}
    for i in ids:
        r = rows[i]
        mm = re.search(r'<td><span class="tag t-(?:goal|inf|con)">([^<]+)</span></td>', r)
        tags[mm.group(1)] += 1
    return tags


def note_of(tags):
    parts = []
    for k in ['可实现', '推断可实现', '不可实现（记载）', '推断不可实现']:
        if tags[k]:
            parts.append('%s %d' % (k, tags[k]))
    return ' · '.join(parts)


tot = {'可实现': 0, '推断可实现': 0, '不可实现（记载）': 0, '推断不可实现': 0}
blocks = []
cap_notes = []
for cid, no, name, d, ids, summ in caps:
    t = count(ids)
    for k in tot:
        tot[k] += t[k]
    n = note_of(t)
    cap_notes.append((cid, name, len(ids), n))
    body = '\n'.join(rows[i] for i in ids)
    blocks.append(
        '<div class="cap" id="%s">\n<div class="cap-h"><div class="t"><span class="sec-no">%s</span><h3>%s</h3><span class="note">%d 个场景：%s</span></div>\n'
        '<p class="def">%s</p></div>\n'
        '<table>\n<tr><th>场景</th><th>判定</th><th>依据</th></tr>\n%s\n</table>\n'
        '<div class="cap-v"><b>现状小结</b>　%s</div>\n</div>' % (cid, no, name, len(ids), n, d, body, summ))
assert tot == {'可实现': 2, '推断可实现': 13, '不可实现（记载）': 2, '推断不可实现': 8}, tot

# 拼新第七节：保留标题、说明、尾注
head_end = s7.index('<div class="tw"><table>')
tail_start = s7.index('</table></div>', head_end) + len('</table></div>')
head = s7[:head_end]
tail = s7[tail_start:]
new_s7 = head + '\n'.join(blocks) + tail
h = h[:s7_start] + new_s7 + h[s7_end:]

tree3 = '''<div class="tree">
<p class="goal">现状盘点：现有弹窗、标签、推送、数据和运营流程，能否做到需求分析的 25 个场景<small>先看现有能力（第一至六节），再按需求分析的五项能力逐个判定场景（第七节），无记载的能力按推断处理（第八节）。</small></p>
<ul>
<li><b>现有能力</b>
<ul>
<li><a href="#s1">弹窗</a>　<span class="d">5 条规则、18 个弹窗项，仅 2 条按人群定向</span></li>
<li><a href="#s2">标签</a>　<span class="d">约 100 个，支持且、或，无交集</span></li>
<li><a href="#s3">推送</a>　<span class="d">5 种通路各自独立，无统一入口</span></li>
<li><a href="#s4">数据</a>　<span class="d">本地只有两份累计口径快照</span></li>
<li><a href="#s5">运营流程</a>　<span class="d">核心步骤在后台内，操作人只能推断</span></li>
<li><a href="#s6">人群触达</a>　<span class="d">五类中仅储值下滑的普卡、银卡有专属规则</span></li>
</ul></li>
<li><a href="#s7"><b>场景可行性</b></a>　<span class="d">25 个场景按五项能力分组</span>
<ul>
''' + '\n'.join('<li><a href="#%s">%s</a>　<span class="d">%d 个场景 · %s</span></li>' % c for c in cap_notes) + '''
</ul></li>
<li><a href="#s8">关键假设</a>　<span class="d">11 项推断，推错时只改对应场景的判定档位</span></li>
</ul>
</div>

'''
assert h.count('<div class="summary"><dl>') == 1
h = h.replace('<div class="summary"><dl>', tree3 + '<div class="summary"><dl>', 1)
open(P3, 'w', encoding='utf-8').write(h)

# 校验：25 行原样保留
h2 = open(P3, encoding='utf-8').read()
for i, r in rows.items():
    assert h2.count(r) == 1, i
print('完成：阶段2 加结构总览与锚点；阶段3 加结构总览，第七节按 5 项能力分组，计数', tot)
