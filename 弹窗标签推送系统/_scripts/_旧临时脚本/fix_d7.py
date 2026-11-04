base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
def sub(t, old, new, count=1):
    n = t.count(old)
    assert n == count, (old[:60], n)
    return t.replace(old, new)
p = base + '决策汇报.html'
t = open(p, encoding='utf-8').read()
t = sub(t, '02 只让金卡以上的储值衰退者多弹；疲劳本身本地判断不了', '02 的 9/29 写法只让金卡以上的储值衰退者多弹（现行 02 已不多弹）；疲劳本身本地判断不了')
t = sub(t, '02 相对现状：多弹的只有金卡以上的储值衰退者—',
        '（按 02 的 9/29 写法；现行 02 新建储值位规则，金卡以上储值下滑者单次 3、活动类每日 12（新增 10），均不高于现状）02 相对现状：多弹的只有金卡以上的储值衰退者—')
anchor = '审查 10:42（R177、R181 复核通过）；口径约束 85；推进计划 Q137</td></tr>\n'
assert t.count(anchor) == 1
row = ('      <tr><td>72</td><td>第二节 D7 标题与「02 相对现状」一句</td>'
       '<td>「02 只让金卡以上的储值衰退者多弹」「多弹的只有金卡以上的储值衰退者，回流、其余 12 → 32」：这是 02 的 9/29 写法，现行 02 已改为新建储值位规则，金卡以上储值下滑者单次 3、活动类每日 12，均不高于现状</td>'
       '<td>标题与句首标明「按 02 的 9/29 写法」，并注明现行 02 的结果；诊断数字不改（第二节整体待 Q140 按 A32、A34、A35 改写）</td>'
       '<td>02 v6 第二张卡「结果」句；口径约束 85</td></tr>\n')
t = t.replace(anchor, anchor + row)
t = sub(t, '汇报独有 71 条', '汇报独有 72 条')
open(p, 'w', encoding='utf-8').write(t)
print('ok')
