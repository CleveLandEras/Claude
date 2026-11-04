#!/bin/bash
# 改纠正提示钩子：思考页 7.3（C4）。只改提示里的一句，不改登记、不动 settings.json、不加新钩子。
# 默认只打印要做的改动并在临时副本上跑测试；加 --执行 才真改。
# 两份一起改：正在生效的 ~/.claude/hooks/correction_capture.py，和还没装上的 ~/claude/_底座/设置/correction_capture_新.py
# （Dk 以后照另一件任务 cp 新脚本时会覆盖正在生效的那份，所以两份都要是新句）。哪份里找不到原句就跳过并说明。
# 用法：bash ~/claude/_底座/任务/2026-10-29_规则体系分层整理/改钩子.sh          （预演）
#       bash ~/claude/_底座/任务/2026-10-29_规则体系分层整理/改钩子.sh --执行   （真改）
exec /usr/bin/python3 -I - "$@" <<'PY'
import os, subprocess, sys, tempfile
DO = '--执行' in sys.argv
H = os.path.expanduser('~')
OLD = '只有 Dk 明说「以后都／每次／所有」时，才同时更新已有的对应记忆条目。'
NEW = 'Dk 明说「以后都／每次／所有」时，在纠正记录这一行末尾标「通用」，由「整理纠正」写进对应的规则文件；记忆不放规则。'
T = [f'{H}/.claude/hooks/correction_capture.py', f'{H}/claude/_底座/设置/correction_capture_新.py']
def test(path):
    r = subprocess.run(['/usr/bin/python3', '-I', path], input='{"prompt":"不对，以后都这样"}', capture_output=True, text=True)
    return '标「通用」' in r.stdout, r.stdout[:120].replace('\n', ' ')
todo = []
for p in T:
    if not os.path.exists(p): print(f'跳过（不存在）：{p}'); continue
    t = open(p, encoding='utf-8').read(); n = t.count(OLD)
    if n == 0: print(f'跳过（已是新句或原句变了）：{p}｜含新句：{NEW in t}'); continue
    if n > 1: print(f'跳过（原句出现 {n} 次，要人工看）：{p}'); continue
    print(f'要改：{p}\n  - {OLD}\n  + {NEW}')
    with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(t.replace(OLD, NEW, 1)); tmp = f.name
    ok, out = test(tmp); os.unlink(tmp)
    print(f'  临时副本测试：{"过" if ok else "不过"}（输出开头：{out}）')
    todo.append((p, t))
if not DO:
    print('\n预演完毕，没有改任何文件。确认后运行：bash ~/claude/_底座/任务/2026-10-29_规则体系分层整理/改钩子.sh --执行'); sys.exit(0)
for p, t in todo:
    open(p, 'w', encoding='utf-8').write(t.replace(OLD, NEW, 1))
    ok, out = test(p); print(f'已改：{p}｜测试：{"过" if ok else "不过"}')
PY
