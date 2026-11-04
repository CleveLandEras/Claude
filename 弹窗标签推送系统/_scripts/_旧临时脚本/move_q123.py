"""把迭代记录里误插在 09 节开头的 Q123 一版挪到 09 节末尾，并补 08 节末的 Q123 一版。不带参数。"""
P = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/迭代记录.md'
t = open(P, encoding='utf-8').read()
h9 = '\n## 09_取数需求_上线前基线.xlsx\n'
assert t.count(h9) == 1
i9 = t.index(h9)
start = t.index('\n### v-Q123', i9)
end_mark = '剩余差距：表4 名单口径（M4）与 02 现行写法一致，无需改；表8 分子已含 ID11，无需改；其余同上一版。'
end = t.index(end_mark, start) + len(end_mark)
block = t[start:end]
t = t[:start] + t[end:]
# 09 节末尾 = 下一个二级标题之前
nxt = t.find('\n## ', i9 + len(h9))
assert nxt > 0
t = t[:nxt] + '\n' + block.lstrip('\n') + '\n' + t[nxt:]
# 08 节末尾 = 09 标题之前
i9 = t.index(h9)
entry08 = ('\n### v-Q123（2026-09-30 执行轮，推进计划 Q123）\n'
           '- 开头提示框与 M1、M2、M6 标题：「首期停用……已降级」改为「按对应规则上线批次取数」；M3、M4、M5 标题去掉方案池代号；M4 对比方式：金卡至至尊卡组与普卡银卡组内容不同（储值位换入的礼包 / 每日补给计划），差值之差只作参考；M7 定义补 ID11；第〇节「适用方案」标明提案乙。分类：纠错（范围）+ 口径细化。分母、窗口、数据来源未改。\n'
           '- 文末新增「更正记录」3 条。回归：检索「首期停用」「降级」「A26」08 正文为 0。\n'
           '剩余差距：同上一版；交叉表、月储值、名单快照留存仍待外部答复。\n')
t = t[:i9] + entry08 + t[i9:]
open(P, 'w', encoding='utf-8').write(t)
print('已整理')
