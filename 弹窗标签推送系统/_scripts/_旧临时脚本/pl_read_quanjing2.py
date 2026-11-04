import re
root = '/Users/decheng.huang/claude/弹窗标签推送系统/'
s = open(root + '简报/弹窗规则全景.html', encoding='utf-8').read()
print('总长', len(s))
for m in re.finditer(r'<script[^>]*>(.*?)</script>', s, flags=re.S):
    print('---- script ----')
    print(m.group(1)[:9000])
b = s.find('<body')
print('---- body html ----')
print(re.sub(r'<script.*?</script>', '', s[b:], flags=re.S)[:3500])
