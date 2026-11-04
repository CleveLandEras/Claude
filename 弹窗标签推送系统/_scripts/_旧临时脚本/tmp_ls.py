import os
b='/Users/decheng.huang/claude/弹窗标签推送系统/_scripts/'
for f in sorted(os.listdir(b)):
    if '03' in f or 'xlsx' in f or f.startswith('q142') or 'build' in f:
        print(f, os.path.getsize(b+f))
