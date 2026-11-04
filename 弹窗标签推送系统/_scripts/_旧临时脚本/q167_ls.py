import os
base = '/Users/decheng.huang/claude/弹窗标签推送系统'
for d in ['', '支撑文件', '分析']:
    print('==', d)
    for f in sorted(os.listdir(os.path.join(base, d))):
        fp = os.path.join(base, d, f)
        if os.path.isfile(fp) and (d != '分析' or f.startswith('A36')):
            print(f, os.path.getsize(fp))
