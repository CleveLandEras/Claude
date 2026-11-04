import re, os
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
keys = ['机器人', '測試', '测试', '账号类型', '帳號類型', '已经先存储了', '交集', '或」', '「或', '互斥', '身份', '25 分钟', '25 分鐘', '排程', '从未储值', '未首储', '回流']
def strip(t):
    t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'[ \t]+', ' ', t)
for fn in ['claude_弹窗标签推送_盘点.html', '02_弹窗分人群定制方案.html', 'C2_新标签脚本草稿.md', '00_推进记录.md', '04_弹窗功能缺口需求.md']:
    t = open(base + fn, encoding='utf-8').read()
    if fn.endswith('.html'):
        t = strip(t)
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    print('=====', fn)
    for i, l in enumerate(lines):
        hit = [k for k in keys if k in l]
        if hit and not (fn != 'claude_弹窗标签推送_盘点.html' and hit == ['身份']) and not (hit == ['回流'] and fn != 'claude_弹窗标签推送_盘点.html'):
            print(i, '|', ','.join(hit), '|', l[:300])
