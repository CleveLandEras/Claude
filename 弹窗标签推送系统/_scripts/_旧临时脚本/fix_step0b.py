"""汇报更正第 63 条补一句「第 0 步」。不带参数；断言通过才写回。"""
p = '/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html'
g = open(p, encoding='utf-8').read()
old = '作废块改名并去掉复制按钮</td>'
assert g.count(old) == 1
g = g.replace(old, '作废块改名并去掉复制按钮；第一批前提统一写作「第 0 步：运营上线前核对弹窗对象能否选排除，不能时先写标签」（02、03、汇报三处同）</td>')
open(p, 'w', encoding='utf-8').write(g)
print('ok')
