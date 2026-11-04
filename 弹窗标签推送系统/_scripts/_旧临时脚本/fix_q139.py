import openpyxl
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
def sub(t, old, new, count=1):
    n = t.count(old)
    assert n == count, (old[:60], n)
    return t.replace(old, new)

p = base + '支撑文件/02_弹窗分人群定制方案.html'
t = open(p, encoding='utf-8').read()
t = sub(t, '代价是退路时要新建 2 个标签（「非金卡以上」与「金卡以上且储值未下滑」）',
        '代价是弹窗对象不能用带排除的群组时，要建 2 个退路标签（「非金卡以上」「金卡以上且储值未下滑」）')
# A35 三句
t = sub(t, '          <li>高卡对该礼包价格的反应方向未知；弹窗疲劳无法用现有数据判断</li>\n',
        '          <li>高卡对该礼包价格的反应方向未知；弹窗疲劳无法用现有数据判断</li>\n'
        '          <li>储值下滑相关礼包的点数成本未知，与礼包价格一起由运营确认；本方案不新增其他赠点来源</li>\n')
t = sub(t, '          <li>独享礼包在破产位的曝光减少</li>\n',
        '          <li>独享礼包在破产位的曝光减少</li>\n'
        '          <li>破产礼包前移后，礼包点数与价格未知，成本影响与价格一起由运营确认</li>\n')
t = sub(t, '涉及的人很少，属提示性风险，不建议改配置；是否保留由运营判断</li>\n',
        '涉及的人很少，属提示性风险，不建议改配置；是否保留由运营判断</li>\n'
        '          <li>回流任务置第 1 位后参与人数可能增加，其奖励点数的发放量未知（回流用户现有活动赠点占全体 5.47%，只作量级参照，不是上限）</li>\n')
anchor = '分析 A34 S3、S4；审查 10:42 后推进计划 Q136</td></tr>'
assert t.count(anchor) == 1
row = ('\n          <tr><td>2026-09-30</td><td>第一张卡、第二张卡、第四张卡主要风险</td>'
       '<td>三张卡风险都没有写点数成本：回流任务置顶后奖励发放、储值下滑礼包、破产礼包前移涉及的点数本地估不出</td>'
       '<td>各补一句「点数未知，与价格一起由运营确认」（第一张卡另注回流用户现有活动赠点占全体 5.47%，只作量级参照，不是上限）；第二张卡补「本方案不新增其他赠点来源」</td>'
       '<td>分析 A35 S3；口径约束 86</td></tr>')
t = t.replace(anchor, anchor + row)
open(p, 'w', encoding='utf-8').write(t)

p = base + '支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(p)
ws = wb['规则']
k9 = ws['K9'].value
old = '并与序号 6 所用的储值下滑标签同步'
assert old in k9
ws['K9'] = k9.replace(old, '并与序号 6 所用的下滑标签同步')
wb.save(p)
print('ok')
