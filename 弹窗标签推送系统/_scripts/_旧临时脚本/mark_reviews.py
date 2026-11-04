import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
t = open(p, encoding='utf-8').read()

def add(t, sec_title, rid, note):
    s0 = t.find('\n## ' + sec_title)
    assert s0 >= 0, sec_title
    nxt_sec = t.find('\n## ', s0 + 5)
    s1 = nxt_sec if nxt_sec > 0 else len(t)
    sec = t[s0:s1]
    m = re.search(r'\n### ' + rid + r'｜', sec)
    assert m, rid
    nxt = re.search(r'\n### R\d+｜|\n\*\*复核：\*\*', sec[m.end():])
    end = m.end() + nxt.start()
    block = sec[m.start():end]
    if '已处理（' in block:
        return t, False
    sec = sec[:end].rstrip('\n') + '\n- 已处理（2026-09-30 执行轮）：' + note + '\n' + sec[end:]
    return t[:s0] + sec + t[s1:], True

sec = '2026-09-30 10:50 审查'
notes = [
 ('R189', '02 第一张卡风险句、A34 提案 1 / 结论 / S3 第 1b 行、汇报交主管块与第 16 件风险句、A32 指向句都改为按你给的原话：月月抽是 ID5 原第 1 位；「弹窗里不再出现」不写「看不到」；注册满 30 天转为持續后恢复；月月抽其他入口是否受影响本地不知道。02 附录四 +1 行、汇报更正第 73 条、A34 修改说明、设计卡追加 Q130 执行结果修正。（我在 10:50 之前已把推进计划 Q136 的旧句写进 02，现已按 R189 改正，请规划者同步改约束 84 与 Q136 原文。）'),
 ('R190', 'A34 标题、结论、S3 末段、判读命中第 2 条改为活动位「确定会变」9 人（新增 6、回流 3）与破产位调序（若上线，两个集合都会碰到，破产频率本地没有，第四张卡风险句已覆盖）分开写；删去「几乎没有确定变化」；A32 指向句同步；设计卡 Q130 执行结果追加修正。约束 84 的「涉及 9 人」请规划者改为「活动位涉及 9 人」。'),
 ('R191', '汇报第 7、8 件合看表「为什么要定」一行句末补「07 另含的短信、Facebook、LINE 能否定向、能触达多少待研发确认」；更正第 73 条。'),
 ('R192', 'A34 S4 写明「前 168 人」两种算法（合并 132 + 36，分格 131 + 37，重合 167 人，审查 10:50 复算），20 人在两种名单里都全部在内；交运营的名单按哪种导出留待交主管前由规划者定一种。汇报括注「131 / 37」暂不改（等定了算法再改）。'),
]
done = []
for rid, note in notes:
    t, ok = add(t, sec, rid, note)
    if ok:
        done.append(rid)
open(p, 'w', encoding='utf-8').write(t)
print('marked', done)
