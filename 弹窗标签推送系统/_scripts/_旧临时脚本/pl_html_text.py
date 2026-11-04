# 只读：把决策汇报等 HTML 去标签后输出纯文本（不含 <details> 折叠内容），规划者通读用
import re, html
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
FILES = ['决策汇报.html']
for f in FILES:
    s = open(BASE + f, encoding='utf-8').read()
    s = re.sub(r'<style.*?</style>', '', s, flags=re.S)
    s = re.sub(r'<script.*?</script>', '', s, flags=re.S)
    # 去掉折叠框（可能嵌套，重复几次）
    for _ in range(6):
        s2 = re.sub(r'<details[^>]*>(?:(?!<details).)*?</details>', '[折叠]', s, flags=re.S)
        if s2 == s:
            break
        s = s2
    s = re.sub(r'<(br|/p|/li|/tr|/h\d|/div|/table|/section)[^>]*>', '\n', s)
    s = re.sub(r'<(td|th)[^>]*>', ' | ', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    print('=' * 10, f, len(s), '字')
    print(s)
