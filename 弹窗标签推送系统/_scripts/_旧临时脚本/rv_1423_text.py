import re, html
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
out = '/Users/decheng.huang/claude/弹窗标签推送系统/_versions/'
for src, dst in [('环节3_方案.html', 'rv_1423_h3.txt'), ('决策汇报.html', 'rv_1423_hb.txt'), ('支撑文件/02_弹窗分人群定制方案.html', 'rv_1423_02.txt')]:
    t = open(base + src, encoding='utf-8').read()
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'</(p|div|tr|h\d|li|summary|table|section)>', '\n', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    open(out + dst, 'w', encoding='utf-8').write(t)
    print(src, len(t))
