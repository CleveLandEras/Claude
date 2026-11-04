import datetime, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
now = datetime.datetime.now().strftime('%H:%M')
d = '09-30 ' + now
# 检索
t = open(BASE + '环节3_方案.html', encoding='utf-8').read()
print('环节3 首屏含新写法：', '02 开头（结构、选一类玩家看改前 / 改后、9 条规则一览、规则全表）' in t, '；「按玩家看」出现', t.count('按玩家看'), '处（均在更正记录）')
for tag in ['div', 'section', 'details', 'table', 'tr', 'p']:
    print(tag, len(re.findall('<' + tag + r'[\s>]', t)), t.count('</' + tag + '>'))
def append(path, text):
    s = open(BASE + path, encoding='utf-8').read()
    if not s.endswith('\n'): s += '\n'
    open(BASE + path, 'w', encoding='utf-8').write(s + text)
append('过程记录/迭代记录.md', f'''
## 2026-09-30 执行轮：Q178（环节3 首屏指向 02 的新小节名；{now}）

- **环节3_方案.html**：首屏「方案线三句话」里「02 开头（结构、按玩家看、规则全表）」改为与决策汇报首屏逐字相同的「02 开头（结构、选一类玩家看改前 / 改后、9 条规则一览、规则全表）」；更正记录加第 44 行。正文检索「按玩家看」：环节3、决策汇报、08、A36 只剩更正记录里的历史原文；决策汇报无需改（首屏已在 Q176 改）。HTML 标签配对。
- **Q179 说明**：Q179 的内容（第 3、4 步、反例检查、汇报指向）已在做 Q174 时一并做完，A37 第一、二部分齐全，见 Q174 一节与 A37 结论。
''')
append('过程记录/任务清单.md', f'| 2026-09-30 {now} 执行轮（Q178、Q179） | 队列项 Q178（直接做）、Q179（并入 Q174 已做完）（状态：待 Dk 验收，待审查复核） | 环节3_方案.html（首屏指向、更正第 44 行）；Q179 无新增文件改动 | Q178：环节3 与汇报首屏该句逐字一致；Q179：A37 第一、二部分齐全（同 Q174 记录） |\n')
append('进展日志.md', f'| {d} | 执行者 | 方案线（交 Dk 验收前同步） | 把环节3 首屏里指向 02 的一句改成和决策汇报首屏一模一样，旧的「按玩家看」小节名已经不存在了 | 推进近交付 ①：Dk 从环节3 点到 02 要找得到全景 | 环节3、决策汇报、08、A36 里「按玩家看」只剩更正记录里的历史原文。另：队列里的 Q179（能力线后半）已在做 Q174 时一并做完，不再单独做 |\n')
p = BASE + '过程记录/推进计划.md'
L = open(p, encoding='utf-8').read().split('\n')
for i, s in enumerate(L):
    if s.startswith('- [ ] Q178｜'):
        L[i] = s.replace('- [ ] Q178｜', '- [x] Q178｜', 1) + f' → 完成（2026-09-30 {now}）：环节3 首屏与汇报首屏该句逐字一致，正文「按玩家看」只剩更正记录，环节3 更正第 44 行已登；汇报无需改；状态待 Dk 验收'
    elif s.startswith('- [ ] Q179｜'):
        L[i] = s.replace('- [ ] Q179｜', '- [x] Q179｜', 1) + f' → 完成（2026-09-30 {now}）：已在 Q174 中一并做完（A37 第一、二部分齐全，反例检查 1–5 脚本自检通过，汇报能力线一节已加指向 + 更正第 97 条）；审查 14:56 的 R247、R248 已处理；状态待 Dk 验收'
open(p, 'w', encoding='utf-8').write('\n'.join(L))
print('done', now)
