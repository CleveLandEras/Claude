# Q177：R240、R242、R243 与「ID5、ID6 各项」说法更正
import os, shutil, sys, copy, datetime
import openpyxl

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
P02 = BASE + '支撑文件/02_弹窗分人群定制方案.html'
P03 = BASE + '支撑文件/03_弹窗配置单.xlsx'
P3 = BASE + '环节3_方案.html'
BAK03 = BASE + '_versions/03_pre_Q177.xlsx'
if os.path.exists(BAK03):
    print('已跑过，停止'); sys.exit(0)
shutil.copyfile(P03, BAK03)
shutil.copyfile(P02, BASE + '_versions/02_pre_Q177.html')
shutil.copyfile(P3, BASE + '_versions/环节3_pre_Q177.html')

# ---------- 02 ----------
h = open(P02, encoding='utf-8').read()
o1 = '各人群的人均每日活动类弹窗曝光，与上表逐格对照；金卡以上储值下滑者另看'
assert h.count(o1) == 1
h = h.replace(o1, '各人群的人均每日活动类弹窗曝光，与第五张卡的上限表逐格对照；金卡以上储值下滑者另看')
o2 = '按下面提案乙的验证计划里的过程指标与护栏判读'
assert h.count(o2) == 1
h = h.replace(o2, '按提案乙的验证计划（附录七）里的过程指标与护栏判读')
anchor = '</tbody>\n      </table></div>\n    </div></details>\n\n    <details class="apx"><summary>五　提案的数字出处</summary>'
assert h.count(anchor) == 1
row = ('          <tr><td>2026-09-30</td><td>附录七第五张卡「判读指标」；提案「代价与风险」第 2 条</td>'
       '<td>「与上表逐格对照」：验证计划移到附录七后，附录七里它的上面没有上限表；「按下面提案乙的验证计划」：提案乙的验证计划现在在这条上面（一句摘要）和附录七，「下面」已不对</td>'
       '<td>「与第五张卡的上限表逐格对照」；「按提案乙的验证计划（附录七）」。只改这两个方位词</td><td>审查 R240</td></tr>\n')
h = h.replace(anchor, row + '        ' + anchor)
open(P02, 'w', encoding='utf-8').write(h)

# ---------- 环节3 ----------
t = open(P3, encoding='utf-8').read()
a3 = '推进计划 Q170–Q173</td></tr>\n    </table></div>\n  </div></details>'
assert t.count(a3) == 1
row3 = ('<tr><td>43</td><td>第二节 ① 表第一张卡末列（「看不出」一格）</td>'
        '<td>「M1 提高就延长……」：与 02 附录七、第二张卡、提案乙的句式不同，「延长」在第 1 期末与合并 3 期终判读起来是两个意思</td>'
        '<td>改为「M1 提高就保留（第 1 期末延长、对照组照留；合并 3 期终判继续运行，对照组转全量……）」，与 02 附录七、第五节 ③ 同义；条件与去向未动（此项改动已由 R239 做在文件里，本行补登）</td>'
        '<td>审查 R239、R243</td></tr>\n')
t = t.replace(a3, '推进计划 Q170–Q173</td></tr>\n' + row3 + '    </table></div>\n  </div></details>')
open(P3, 'w', encoding='utf-8').write(t)

# ---------- 03 ----------
wb = openpyxl.load_workbook(P03)
ws = wb['最终规则全表']
v = ws['I5'].value
old_tail = '（ID5 各项设置取自「排序明细」回流用户活动弹窗各行，03 与 02 均写新建规则的时机、每日次数、冷却照抄 ID5）'
assert v.endswith(old_tail)
ws['I5'].value = v[:-len(old_tail)] + '（取自盘点第二节『时机占用』表，9/24 后台配置）'

lg = wb['更正记录']
last = lg.max_row
rows = [
    ['2026-09-30', '规则表 A2', 'A2 只写了对象带排除的群组不能用时，序号 1–3 的对照组改用互补标签「分桶·对照」；第二批序号 4–6、9 的对照版同样依赖排除，没写退路',
     '补：第 0 步查出带排除的对象不能用时，各卡对照版的对象都改用互补标签「分桶·对照」（与「分桶·处理」同一次分桶生成，共用 1 个，见 K5）；配置各列未动（此项改动已由 R238 做在文件里，本行补登；上一行「『规则』『排序明细』两表未动一格」只对新增「最终规则全表」这一步成立）', '审查 R238、R243'],
    ['2026-09-30', '最终规则全表 I5 括注', '「ID5 各项设置取自『排序明细』回流用户活动弹窗各行，03 与 02 均写新建规则的时机、每日次数、冷却照抄 ID5」：出处绕回来了（新建规则照抄 ID5，ID5 又取自新建规则），而 ID5 各项的时机、次数、冷却在盘点第二节「时机占用」表里逐项都有',
     '「（取自盘点第二节『时机占用』表，9/24 后台配置）」；各项数值未动。本地没有的是 ID6、ID7 各项的时机、次数、冷却（最终规则全表里写「沿用现值」的两行）', '审查 R242；盘点第二节「时机占用」表'],
]
for i, r in enumerate(rows, 1):
    n = last + i
    for j, val in enumerate(r, 1):
        src = lg.cell(row=last, column=j)
        dst = lg.cell(row=n, column=j)
        dst.value = val
        dst.font = copy.copy(src.font); dst.alignment = copy.copy(src.alignment)
        dst.border = copy.copy(src.border); dst.fill = copy.copy(src.fill)
        dst.number_format = src.number_format
    lg.row_dimensions[n].height = lg.row_dimensions[last].height
wb.save(P03)

# 03 读回：除 I5 与更正记录新增行外逐格一致
a = openpyxl.load_workbook(BAK03); b = openpyxl.load_workbook(P03)
diff = []
for name in a.sheetnames:
    wa, wb2 = a[name], b[name]
    for r in range(1, max(wa.max_row, wb2.max_row) + 1):
        for c in range(1, max(wa.max_column, wb2.max_column) + 1):
            if wa.cell(r, c).value != wb2.cell(r, c).value:
                diff.append((name, wa.cell(r, c).coordinate))
print('03 差异格：', diff)
print('03 sheets：', b.sheetnames)

# ---------- 正文检索「ID5、ID6 各项」 ----------
import re
for f in ['支撑文件/02_弹窗分人群定制方案.html', '决策汇报.html', '环节3_方案.html']:
    s = open(BASE + f, encoding='utf-8').read()
    print(f, '「ID5、ID6 各项」出现：', len(re.findall('ID5、ID6 各项', s)))
for tag in ['div', 'section', 'details', 'table', 'tr']:
    s = open(P02, encoding='utf-8').read(); s3 = open(P3, encoding='utf-8').read()
    print(tag, len(re.findall('<' + tag + r'[\s>]', s)), s.count('</' + tag + '>'), '| 环节3', len(re.findall('<' + tag + r'[\s>]', s3)), s3.count('</' + tag + '>'))

# ---------- 迭代记录 ----------
now = datetime.datetime.now().strftime('%H:%M')
it = open(BASE + '过程记录/迭代记录.md', encoding='utf-8').read()
if not it.endswith('\n'): it += '\n'
it += f'''
## 2026-09-30 执行轮：Q177（处理审查 14:35 的 R240、R242、R243，并更正「ID5、ID6 各项」说法；脚本 `_scripts/q177_edit.py`）

- **支撑文件/02（v+1）**：附录七第五张卡「与上表逐格对照」→「与第五张卡的上限表逐格对照」；提案「代价与风险」第 2 条「按下面提案乙的验证计划」→「按提案乙的验证计划（附录七）」（R240，只改这两个方位词）；更正记录加一行。改前备份 `_versions/02_pre_Q177.html`。
- **支撑文件/03（v+1）**：「最终规则全表」I5 括注改为「（取自盘点第二节『时机占用』表，9/24 后台配置）」（R242）；更正记录补两行：R238（「规则」A2 补互补标签「分桶·对照」适用范围）与 R242（R243）。读回：与改前 `_versions/03_pre_Q177.xlsx` 相比，只有 I5 与更正记录新增两行不同，配置各列无变化。
- **环节3_方案.html**：更正记录补第 43 行（R239 的「延长」→「保留（第 1 期末延长……）」，改动已在文件里，本行补登）（R243）。改前备份 `_versions/环节3_pre_Q177.html`。
- **更正 Q172 节的一句话**：上文 Q172 节写「ID5、ID6 各项时机、次数、冷却的现值本地未取得（盘点只有排序与 ID5 每日合计 12）」不对。ID5 各项的时机、次数、冷却在盘点第二节「时机占用」表里逐项都有（审查 14:35 已核实，10 项全对），03 最终规则全表 I5 已按此填写；本地没有的是 ID6、ID7 各项的时机、次数、冷却（03 最终规则全表里写「沿用现值」的两行）。同一说法在 02、03、决策汇报、环节3 正文里检索为 0 处，无需改。
- 剩余差距：ID6、ID7 各项现值待运营后台截图（挂起第 11 条，不影响照表配置）。环节3 首屏「02 开头（结构、按玩家看、规则全表）」仍是旧名，未在本项范围内（按计划环节3 只补一行更正记录），留给规划者判断。
'''
open(BASE + '过程记录/迭代记录.md', 'w', encoding='utf-8').write(it)

# ---------- 日志与队列标记 ----------
def append(path, text):
    s = open(BASE + path, encoding='utf-8').read()
    if not s.endswith('\n'): s += '\n'
    open(BASE + path, 'w', encoding='utf-8').write(s + text)
append('过程记录/任务清单.md', f'| 2026-09-30 {now} 执行轮（Q177） | 队列项 Q177（直接做；状态：待 Dk 验收，待审查复核） | 支撑文件/02（两个方位词、更正记录）、支撑文件/03（I5 括注、更正记录两行）、环节3_方案.html（更正第 43 行）、迭代记录（更正 Q172 节一句） | 方案线·交验收前修正：审查 R240、R242、R243 三条建议落地；配置各列读回无变化 |\n')
append('进展日志.md', f'| 09-30 {now} | 执行者 | 方案线·环节3（交 Dk 验收前修正） | 处理审查提的三条小建议：02 里两处「上表」「下面」的指向改对；03 最终规则全表里 ID5 各项的出处改成「盘点第二节时机占用表」（这些值盘点里本来就有）；03 和环节3 的更正记录补登两处已做的改动。同时更正之前记录里「ID5、ID6 各项现值没有」的说法（实际没有的是 ID6、ID7） | 推进近交付 ①②（02、03 验收前把出处和指向理清，Dk 翻文件不会找错地方、也不用去截不需要的后台图） | 03 配置各列读回和改前完全一致，只多了括注和两行更正记录；正文里那句错误说法检索为 0 处 |\n')

p = BASE + '过程记录/推进计划.md'
L = open(p, encoding='utf-8').read().split('\n')
for i, s in enumerate(L):
    if s.startswith('- [ ] Q177｜'):
        L[i] = s.replace('- [ ] Q177｜', '- [x] Q177｜', 1) + f' → 完成（2026-09-30 {now}）：R240、R242、R243 已落，03 读回只差 I5 与更正记录两行，「ID5、ID6 各项」正文检索 0 处，迭代记录 Q172 节已追加更正；状态待 Dk 验收'
        break
else:
    print('没找到 Q177 行')
open(p, 'w', encoding='utf-8').write('\n'.join(L))
print('done', now)
