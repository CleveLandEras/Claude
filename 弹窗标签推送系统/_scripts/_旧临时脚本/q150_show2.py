base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
s = open(base + '决策汇报.html', encoding='utf-8').read()
a = s.find('<div class="panel"', s.find('id="to-boss-old"') + 3000)
a = s.find('  </div></details>\n\n  <div class="panel"', s.find('id="to-boss-old"'))
print(a)
b = s.find('<div class="dec"', a)
print(s[a:b])
