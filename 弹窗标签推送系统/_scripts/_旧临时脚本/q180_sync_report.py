# Q180 ③：把 A37 第三部分的统计句、「能力线待确认问句」附录、更正记录同步进 决策汇报.html（可重复运行；先备份）
import re, shutil, json, sys
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
sys.path.insert(0, BASE + '_scripts')
from q180_data import NEW, EXIST
cnt = json.load(open(BASE + '_versions/q175_counts.json', encoding='utf-8'))
S = cnt['S_all']          # 有、没有、未知、推断有、推断没有、无法推断
P = BASE + '决策汇报.html'
shutil.copyfile(P, BASE + '_versions/决策汇报_q180前备份.html')
h = open(P, encoding='utf-8').read()

# (a) 统计句
old_a = '；每项有没有见 A37 第三部分（Q175，待做）。'
new_a = (f'；逐项有没有（A37 第三部分）：{S[0]+S[1]+S[2]} 项中有 {S[0]} 项、没有 {S[1]} 项、未知 {S[2]} 项（其中推断有 {S[3]}、推断没有 {S[4]}、无法推断 {S[5]}）；'
         '未知项该问谁、问什么见附录「能力线待确认问句」。')
if old_a in h:
    h = h.replace(old_a, new_a, 1)
elif '逐项有没有（A37 第三部分）' in h:
    h = re.sub(r'；逐项有没有（A37 第三部分）：.*?见附录「能力线待确认问句」。', new_a, h, count=1, flags=re.S)
else:
    raise SystemExit('找不到统计句位置')

# (b) 附录小节
n_exist = sum(len(e[0]) for e in EXIST)
n_new = sum(len(q[3]) for q in NEW)
parts = []
ids = {'运营': 'q180a', '研发': 'q180b', '数据组': 'q180c', 'Dk 自查': 'q180d'}
for who in ('运营', '研发', '数据组', 'Dk 自查'):
    qs = [q for q in NEW if q[1] == who]
    lines = '\n'.join(f'{i}. {q[2]}' for i, q in enumerate(qs, 1))
    parts.append(f'<p class="small" style="margin:10px 0 4px"><b>{who}（{len(qs)} 句）</b></p>\n<pre id="{ids[who]}">{lines}</pre>\n<button onclick="cp(\'{ids[who]}\',this)">复制</button>')
block = (
    '<!-- Q180-APPENDIX-BEGIN -->\n'
    f'  <details><summary>能力线待确认问句（Q180；不计入上面的「三样」）· 是否转问、何时转问由 Dk 决定</summary><div class="body">\n'
    f'<p class="small" style="margin:0 0 6px">能力线第一环：{S[0]+S[1]+S[2]} 项能力里 {S[2]} 项只能是「未知」。其中 {n_exist} 项已被上面的问句、03 第 0 步、盘点第六节的待问句覆盖，不重复加问（逐项对照见 <a href="分析/A37_能力线现有能力.md">A37</a> 第三部分「未知项的确认人与问句」）；另有 {len(NEW)} 句新问句，覆盖 {n_new} 项，按确认人分组如下。是否转问、何时转问由你决定，agent 不对外发送；问句只问能不能、有没有，不含会员编号以外的个人信息。数据组的几句是「表名与字段」的一部分，对外问题精简③ 曾把它推迟到再导数据时一并问。</p>\n'
    + '\n'.join(parts) +
    '\n<p class="small" style="margin:6px 0 0">每句覆盖哪几个能力项，见 A37 第三部分各确认人下的表。已在别处问的 59 项里，方案线同一件、已在等答复的有：03 第 0 步（弹窗对象能否排除、能否并用）、自查 ①③④、运营第 4 句（4 种通路能否按名单发、有无发送到达点击数据）。</p></div></details>\n'
    '<!-- Q180-APPENDIX-END -->\n'
)
block = block.replace('59 项里', f'{n_exist} 项里')
if '<!-- Q180-APPENDIX-BEGIN -->' in h:
    h = re.sub(r'<!-- Q180-APPENDIX-BEGIN -->.*?<!-- Q180-APPENDIX-END -->\n', block, h, count=1, flags=re.S)
else:
    anchor = '这一句你答就行，不必发给别人。</p></div></details>\n'
    assert anchor in h, '找不到附录锚点'
    h = h.replace(anchor, anchor + '\n' + block, 1)

# (c) 更正记录第 99 条
row99 = ('<tr><td>99</td><td>第五节能力线组那一句</td><td>写「每项有没有见 A37 第三部分（Q175，待做）」；Q175、Q180 做完后第三部分已有逐项状态、冲突清单与确认人问句</td>'
         f'<td>改为「{S[0]+S[1]+S[2]} 项中有 {S[0]}、没有 {S[1]}、未知 {S[2]}（推断有 {S[3]}、推断没有 {S[4]}、无法推断 {S[5]}）」，并指向附录新增的「能力线待确认问句」；第 5、8、9、11 件的推荐、件号未动</td><td>设计卡 Q175；推进计划 Q175、Q180</td></tr>')
if '<td>99</td><td>第五节能力线组那一句</td>' in h:
    h = re.sub(r'<tr><td>99</td><td>第五节能力线组那一句</td>.*?</tr>', row99, h, count=1, flags=re.S)
else:
    anchor2 = '<td>审查 R249、R250、R251；推进计划 Q181</td></tr>'
    assert anchor2 in h, '找不到更正记录锚点'
    h = h.replace(anchor2, anchor2 + '\n' + row99, 1)
open(P, 'w', encoding='utf-8').write(h)
print('汇报已同步', S, '已在别处', n_exist, '新问句', len(NEW), '覆盖', n_new)
