#!/usr/bin/env python3
# 只读：进展日志行数与最后两行
p = "/Users/decheng.huang/claude/弹窗标签推送系统/进展日志.md"
lines = open(p, encoding="utf-8").read().split("\n")
print(len(lines))
for l in lines[-3:]:
    print(repr(l[:300]))
