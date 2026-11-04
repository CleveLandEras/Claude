# 整合前备份：把 阶段3_现状盘点.html 原样复制到 _versions/（不带参数运行；只复制，不改原文件）
import shutil
base = "/Users/decheng.huang/claude/弹窗标签推送系统/"
dst = base + "_versions/阶段3_现状盘点_整合前_1008.html"
shutil.copyfile(base + "阶段3_现状盘点.html", dst)
print("已备份到", dst)
