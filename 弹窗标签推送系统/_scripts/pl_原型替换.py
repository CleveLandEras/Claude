#!/usr/bin/env python3
# 原型措辞改动：按 JSON [{"old","new","why"}] 逐条替换原型，old 须在当时的原型里恰好出现一次。
# 用法：python3 _scripts/pl_原型替换.py 检查|应用 <改动.json>
#   检查：只在内存里替换，报告找不到或不唯一的条目，不写文件
#   应用：全部条目无问题才写入；有问题一条都不写
# 10/19 起原型按页拆在 推送系统后台集成需求/原型源/（见 _scripts/an_原型拼装.py）：本脚本改的是源文件，
#   写入后自动运行拼装脚本生成 3_原型.html。old 跨两个源文件时找不到，需拆成两条。
import json, sys, pathlib, subprocess
BASE = pathlib.Path(__file__).resolve().parent.parent
SRC = BASE / '推送系统后台集成需求' / '原型源'
mode, src = sys.argv[1], sys.argv[2]
items = json.load(open(src, encoding='utf-8'))
names = [l.strip() for l in (SRC / '_顺序.txt').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
files = {n: (SRC / n).read_text(encoding='utf-8') for n in names}
changed = set()
bad = []
for i, it in enumerate(items):
    if it['old'] == it['new']:
        continue
    hits = [n for n in names if it['old'] in files[n]]
    total = sum(files[n].count(it['old']) for n in hits)
    if total != 1:
        bad.append(f"#{i} 出现 {total} 次：{it['old'][:50]}")
        continue
    n = hits[0]
    files[n] = files[n].replace(it['old'], it['new'], 1)
    changed.add(n)
print(f"{len(items)} 条，问题 {len(bad)} 条；涉及源文件：{'、'.join(sorted(changed)) or '无'}")
for b in bad[:30]:
    print(b)
if mode == '应用':
    if bad:
        print('有问题，未写入')
    else:
        for n in changed:
            (SRC / n).write_text(files[n], encoding='utf-8')
        print('已写入源文件')
        subprocess.run([sys.executable, str(BASE / '_scripts' / 'an_原型拼装.py')], check=True)
