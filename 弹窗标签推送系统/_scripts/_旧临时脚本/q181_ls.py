# Q181：只读，列出 支撑文件/ 与 分析/ 的文件名
import os
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for d in ('支撑文件', '来源资料'):
    print(d, sorted(os.listdir(B + d)))
