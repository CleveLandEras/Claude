"""规划者只读：列出各目录文件、修改时间、行数（不改任何文件）。"""
import os, time
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for sub in ['', '过程记录', '分析', '支撑文件']:
    d = os.path.join(BASE, sub)
    print('=' * 20, sub or '根目录')
    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        if os.path.isdir(p):
            continue
        try:
            n = sum(1 for _ in open(p, encoding='utf-8', errors='ignore'))
        except Exception:
            n = -1
        print(time.strftime('%m-%d %H:%M', time.localtime(os.path.getmtime(p))), f'{n:6d}', f)
