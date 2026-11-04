# Q180：只读，打印 决策汇报.html 原始源码里「问 Dk 一句」「你自己查的 6 件」前后的 HTML
import re
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
h = open(B + '决策汇报.html', encoding='utf-8').read()
for key in ('问 Dk 一句', '你自己查的 6 件'):
    for m in re.finditer(key, h):
        print('=== ', key, '@', m.start())
        print(h[max(0, m.start() - 600):m.start() + 1300])
        break
print('=== 每项有没有见 A37')
m = re.search(r'每项有没有见 A37', h)
print(h[m.start() - 400:m.start() + 200])
