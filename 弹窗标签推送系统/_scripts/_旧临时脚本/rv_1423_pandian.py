import re, html
p = '/Users/decheng.huang/claude/弹窗标签推送系统/来源资料/claude_弹窗标签推送_盘点.html'
t = open(p, encoding='utf-8').read()
t = re.sub(r'<script.*?</script>|<style.*?</style>', '', t, flags=re.S)
t = re.sub(r'<[^>]+>', '|', t)
t = html.unescape(t)
t = re.sub(r'\s*\|[\s|]*', '|', t)
i = t.find('时机占用')
print(t[i-600:i+1600])
