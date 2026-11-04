import os
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for rel, n in [('进展日志.md', 14), ('过程记录/任务清单.md', 12)]:
    lines = open(base + rel, encoding='utf-8').read().splitlines()
    print('=====', rel, len(lines))
    for l in lines[-n:]:
        print(l[:900])
print('===== 分析/')
for f in sorted(os.listdir(base + '分析')):
    st = os.stat(base + '分析/' + f)
    print(f, st.st_size)
print('===== 审查记录 mtime', os.stat(base + '过程记录/审查记录.md').st_mtime)
import time
print(time.ctime(os.stat(base + '过程记录/审查记录.md').st_mtime))
