import os, time
d = '/Users/decheng.huang/claude/弹窗标签推送系统'
for n in sorted(os.listdir(d)):
    p = os.path.join(d, n)
    st = os.stat(p)
    print(f"{time.strftime('%m-%d %H:%M', time.localtime(st.st_mtime))}  {st.st_size:>9}  {n}")
