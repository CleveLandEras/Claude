base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
p = base + '决策汇报.html'
s = open(p, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    if n != cnt:
        raise SystemExit('命中 %d 次（要 %d）：%s' % (n, cnt, old[:60]))
    s = s.replace(old, new)

rep('<b>提案 B：缩到首期基本不交研发（待主管定）</b>',
    '<b>提案 B：缩到首期基本不交研发（待主管定；依据待重写，改写前不作推荐；优先级按能力线逻辑链重排，待做）</b>')
rep('交集「有用、不必要」（前提：群组有排除栏，待研发确认；没有则改判「必要」）',
    '交集「有用、不必要」（这是按事先写死的业绩取舍规则判的，按能力线「解开多少方案」重排后可能改判，待做；前提：群组有排除栏，待研发确认；没有则改判「必要」）')
rep('第五节第 5、8、11 件与「要主管定」表 11③ 行</td>',
    '第五节第 5、8、9、11 件与「要主管定」表 11③ 行；环节3 首屏、第三节、第五节的同类句；04、05、07 文末提案；A26、A27、A29、A33 顶部说明</td>')
open(p, 'w', encoding='utf-8').write(s)
print('ok')
