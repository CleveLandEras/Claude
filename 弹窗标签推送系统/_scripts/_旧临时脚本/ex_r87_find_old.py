
# 只读：在迭代记录、决策汇报现行版里找 R87 点名的旧写法与现行写法
import re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
files = ['过程记录/迭代记录.md', '决策汇报.html', '过程记录/任务清单.md']
keys = ['两个字段的口径问', '随需求提', '看决定 C', '决定 C 前提', '埋点要不要']
for f in files:
    txt = open(BASE + f, encoding='utf-8').read()
    for k in keys:
        for m in re.finditer(re.escape(k), txt):
            s = txt[max(0, m.start() - 300): m.end() + 200]
            s = re.sub(r'<[^>]+>', '', s).replace('\n', ' ⏎ ')
            line = txt[:m.start()].count('\n') + 1
            print('--', f, line, '|', k, '|', s)
