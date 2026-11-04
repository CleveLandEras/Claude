import re, html
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
def txt(p):
    t = open(base + p, encoding='utf-8').read()
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '|', t)
    t = html.unescape(t)
    return re.sub(r'\s*\|[\s|]*', '|', t)
a = txt('简报/弹窗规则全景.html')
b = txt('支撑文件/02_弹窗分人群定制方案.html')
print('=== REF ===')
print(a[:9000])
print('=== 02 head ===')
i = b.find('按玩家看')
print(b[max(0, i-2500):i+5200])
