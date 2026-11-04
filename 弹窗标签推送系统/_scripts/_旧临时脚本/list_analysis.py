import os
base = '/Users/decheng.huang/claude/弹窗标签推送系统'
for d in ['分析', '数据', '_scripts']:
    p = os.path.join(base, d)
    print('==', d)
    for f in sorted(os.listdir(p)):
        print(f)
