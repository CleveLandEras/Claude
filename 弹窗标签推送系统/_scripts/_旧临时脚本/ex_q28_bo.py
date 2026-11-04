"""Q28：在盘点中找「登入平台」及平台取值（含 bo）的上下文（只读）。不带参数运行。"""
import re, html
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
s = open(B + 'claude_弹窗标签推送_盘点.html', encoding='utf-8').read()
t = html.unescape(re.sub(r'<[^>]+>', ' ', s))
t = re.sub(r'\s+', ' ', t)
for k in ['登入平台', 'mweb', 'apk', 'mh5', ' bo', 'bo ', 'bo、', '、bo', '平台']:
    for m in re.finditer(re.escape(k), t):
        print(f'[{k}] …{t[max(0, m.start()-120):m.end()+160]}…')
        print()
