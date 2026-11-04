import re
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
t = open(B + '决策汇报.html', encoding='utf-8').read()
t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
t = re.sub(r'<(h[1-4])[^>]*>', r'\n\n### ', t)
t = re.sub(r'<(p|li|tr|summary|div)[^>]*>', '\n', t)
t = re.sub(r'<[^>]+>', ' ', t)
t = re.sub(r'[ \t]+', ' ', t)
t = re.sub(r'\n\s*\n+', '\n', t)
print(len(t))
for kw in ['原样转发', '可以转发', '可交研发', '可交数据组', '今天就能发']:
    for m in re.finditer(kw, t):
        s = max(0, m.start() - 70)
        print('[' + kw + ']', t[s:m.end() + 40].replace('\n', ' ⏎ '))
print('=====HEAD')
print(t[:6000])
