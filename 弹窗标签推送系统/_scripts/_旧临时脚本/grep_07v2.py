"""只读检索：盘点及交付物中与推送相关的行（07 v2 迭代用）。"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _textify import BASE, textify

KEYS = ['推送', '推播', '通行证', '跳转', '到达', '发送量', '侧边栏', '红点', '问题 9', '问题 10', '9-2', '9-3', '推送条']
files = ['claude_弹窗标签推送_盘点.html', '00_推进记录.md', '04_弹窗功能缺口需求.md', '05_标签需求.md', 'C1_卡点解锁优先级.md']
for f in files:
    p = os.path.join(BASE, f)
    if not os.path.exists(p):
        print(f'### {f}: 不存在'); continue
    lines = textify(p).splitlines()
    print(f'### {f}')
    for i, l in enumerate(lines):
        if any(k in l for k in KEYS):
            print(f'{i+1}: {l[:400]}')
