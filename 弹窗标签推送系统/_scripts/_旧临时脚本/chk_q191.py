# 检查阶段1 正文里旧说法是否还在。只读。
import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/阶段1_核心论证.html'
t = open(p, encoding='utf-8').read()
phrases = ['更像新账号', '共 32 次', '门槛不是原因', '等于已经覆盖', '维持第一位', '补齐「或」', '多建 2 个标签',
           '已走的高卡', '按卡别分档可行', '和你 9/28 的判断不同', '排序不动', '按 B 画', '暂按 B', '都没人查得到',
           '做法 A', '做法 B', '拿不到', '储值率 17.77%', '偏弱']
for ph in phrases:
    idx = [m.start() for m in re.finditer(re.escape(ph), t)]
    print(ph, len(idx))
    for i in idx[:3]:
        print('   ...', t[max(0, i - 30):i + 40].replace('\n', ' '))
