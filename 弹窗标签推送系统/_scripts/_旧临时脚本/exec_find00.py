"""执行者用：在 00_推进记录.md 中找「想确认三件事」「金卡以上的玩家储值明显下降」「发给运营」所在行号。只读，不带参数。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = open(os.path.join(BASE, '支撑文件', '00_推进记录.md'), encoding='utf-8').read().split('\n')
for i, l in enumerate(L, 1):
    if '想确认三件事' in l or '储值明显下降' in l or '发给运营' in l or '现行版' in l:
        print(i, l[:160])
