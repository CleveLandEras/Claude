# Q181：只读，在 决策汇报.html 原始源码里找「80 条动作」「更正记录」的位置与上下文
import re
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
h = open(B + '决策汇报.html', encoding='utf-8').read()
print('长度', len(h))
for m in re.finditer(r'80 条动作', h):
    print('--- 80 条动作 @', m.start())
    print(h[max(0, m.start() - 300):m.start() + 300])
idx = [m.start() for m in re.finditer(r'更正', h)]
print('更正 出现次数', len(idx))
# 更正记录表的最后几行
last = h.rfind('<tr')
print('--- 末尾 tr 前后 ---')
for m in list(re.finditer(r'更正记录', h))[:3]:
    print('@', m.start(), h[m.start() - 100:m.start() + 200].replace('\n', ' '))
