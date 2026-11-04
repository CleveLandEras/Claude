"""列出 分析/ 与 支撑文件/ 下的文件名。只读，不带参数。"""
import os
B = '/Users/decheng.huang/claude/弹窗标签推送系统'
for d in ('分析', '支撑文件'):
    print(d, sorted(os.listdir(os.path.join(B, d))))
