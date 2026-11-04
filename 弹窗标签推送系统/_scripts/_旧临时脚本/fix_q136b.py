base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
def sub(t, old, new, count=1):
    n = t.count(old)
    assert n == count, (old[:60], n)
    return t.replace(old, new)
p = base + '决策汇报.html'
t = open(p, encoding='utf-8').read()
t = sub(t, '风险：新增玩家单次进大厅的活动弹窗由 2 个降为 1 个（客户端另有新手弹窗）；储值下滑',
        '风险：新增玩家单次进大厅的活动弹窗由 2 个降为 1 个（客户端另有新手弹窗），且新增里金卡以上 57 人（0.53%）不再出现月月抽；储值下滑')
t = sub(t, '风险：新增玩家单次进大厅的活动弹窗由 2 个降为 1 个（客户端另有新手弹窗，个数未知）；回流玩家',
        '风险：新增玩家单次进大厅的活动弹窗由 2 个降为 1 个（客户端另有新手弹窗，个数未知），且新增里金卡以上 57 人（0.53%，分母 10,749）不再出现月月抽（提示性，涉及人很少）；回流玩家')
anchor = '审查 R178 同类残留；07 v2.0 前置条件表；推进计划 Q135</td></tr>\n'
assert t.count(anchor) == 1
row = ('      <tr><td>70</td><td>交主管块第 1 件风险句；第 16 件风险句</td>'
       '<td>只写新增玩家单次弹窗 2 → 1，没写新增里的金卡以上不再出现月月抽</td>'
       '<td>各补半句「新增里金卡以上 57 人（0.53%，分母 10,749）不再出现月月抽」（提示性），与 02 第一张卡风险一致</td>'
       '<td>分析 A34；推进计划 Q136</td></tr>\n')
t = t.replace(anchor, anchor + row)
t = sub(t, '汇报独有 69 条', '汇报独有 70 条')
open(p, 'w', encoding='utf-8').write(t)
print('ok')
