# Q180：只读，核对 决策汇报.html 的同步结果与标签配对
import re
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
h = open(B + '决策汇报.html', encoding='utf-8').read()
bk = open(B + '_versions/决策汇报_q180前备份.html', encoding='utf-8').read()
for name, t in (('现在', h), ('备份', bk)):
    print(name, 'details 开', len(re.findall(r'<details', t)), '闭', len(re.findall(r'</details>', t)), 'pre 开', len(re.findall(r'<pre', t)), '闭', len(re.findall(r'</pre>', t)),
          'tr 开', len(re.findall(r'<tr', t)), '闭', len(re.findall(r'</tr>', t)), 'p 开', len(re.findall(r'<p[ >]', t)), '闭', len(re.findall(r'</p>', t)))
print('统计句', re.search(r'逐项有没有（A37 第三部分）：.*?见附录「能力线待确认问句」。', h, flags=re.S).group(0))
print('附录标记', h.count('<!-- Q180-APPENDIX-BEGIN -->'), h.count('<!-- Q180-APPENDIX-END -->'))
for i in ('q180a', 'q180b', 'q180c', 'q180d'):
    print(i, h.count('id="%s"' % i), h.count("cp('%s'" % i))
print('更正 99', '<td>99</td><td>第五节能力线组那一句</td>' in h)
print('旧句残留', h.count('Q175，待做'))
m = re.search(r'<!-- Q180-APPENDIX-BEGIN -->.*?<!-- Q180-APPENDIX-END -->', h, flags=re.S)
txt = re.sub(r'<[^>]+>', ' ', m.group(0))
print(txt[:1200])
