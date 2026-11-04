"""Q121：07 v2.0、06 改写后同步决策汇报第 8 件与第四节 07 行。不带参数；断言通过才写回。"""
P = '/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html'
t = open(P, encoding='utf-8').read()


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:50])
    t = t.replace(old, new)


rep('07 正在按此改写，完成后同步本件。', '07 已改写为 v2.0：适用范围 5 种通路，快显改为后台可配置，对象增加会员编号名单，每人每日上限跨通路，各通路能否定向、有无数据写入前置条件由研发确认。')
rep('07 推送需求（改写中）。', '07 推送需求 v2.0；06 推送现状。')
rep('<span class="tag t-wait">按主管范围改写中</span> 覆盖 5 种通路；完成后同步；「首期缩小」改为文末提案',
    '<span class="tag t-ok">已按主管范围改写（v2.0）</span> 覆盖 5 种通路；各通路能否定向、有无数据写入前置条件由研发确认；「首期缩小」改为文末提案（待主管定）')
open(P, 'w', encoding='utf-8').write(t)
print('已同步')
