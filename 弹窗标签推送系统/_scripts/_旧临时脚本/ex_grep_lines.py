"""按行检索原始文件：读 _versions/grep_terms_exec.txt，第一行为逗号分隔的相对路径，其余每行一个检索词；输出 文件:行号:前 200 字。只读，不带参数。"""
import os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
lines = [l.rstrip('\n') for l in open(os.path.join(BASE, '_versions', 'grep_terms_exec.txt'), encoding='utf-8') if l.strip()]
files = [f.strip() for f in lines[0].split(',')]
for t in lines[1:]:
    print('=' * 40, t)
    for f in files:
        for i, s in enumerate(open(os.path.join(BASE, f), encoding='utf-8'), 1):
            if t in s:
                j = s.find(t)
                print(f'  {f}:{i}: …{s[max(0, j - 80):j + 160].strip()}…')
