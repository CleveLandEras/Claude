import re, glob
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for pat in ['支撑文件/04*.md', '支撑文件/05*.md', '支撑文件/07*.md']:
    for p in glob.glob(B + pat):
        s = open(p, encoding='utf-8').read()
        i = s.rfind('\n## 提案')
        if i < 0:
            i = s.rfind('提案')
        print('#####', p.split('/')[-1]); print(s[i:i+2200]); print()
for p in glob.glob(B + '支撑文件/02*.html'):
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'<(h[1-4]|tr|li|p|div)[^>]*>', '\n', s)
    t = re.sub(r'<[^>]+>', ' ', s)
    t = re.sub(r'[ \t]+', ' ', t)
    print('##### 02 全文长度', len(t))
    for k in ['评估', '验证', '判读', '下一版', '测不出', '对照']:
        ms = list(re.finditer(k, t))
        print(k, len(ms))
        for m in ms[:4]:
            print('   >', t[max(0, m.start()-60):m.start()+200].replace('\n', ' '))
