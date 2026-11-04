import re, html
root = '/Users/decheng.huang/claude/弹窗标签推送系统/'
def txt(p):
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'</(tr|p|h\d|li|div|section|table|summary)>', '\n', s)
    s = re.sub(r'</t[dh]>', ' | ', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    return s
q = txt(root + '简报/弹窗规则全景.html')
print('==== 参考稿 全景（新版）长度', len(q), '====')
print(q[:9000])
print('\n==== 02 开头 ====')
t = txt(root + '支撑文件/02_弹窗分人群定制方案.html')
i = t.find('按玩家看')
print(t[max(0, i-1500):i+5000])
