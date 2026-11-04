#!/bin/bash
# 改交付闸门：任务文件必答⑧。把同文件夹的 delivery_gate_新.py 装到 ~/.claude/hooks/delivery_gate.py，
# 同时把 ~/claude/_底座/README.md 里描述旧闸门的两句（第一级一条的末句、检查程序表里交付闸门一行）换成新闸门的说法。
# 不动 settings.json（登记的命令行不变），不加新钩子。
# 默认只打印新旧差别、README 要替换的原句和新句，并在新版上做一次不崩自查；加 --执行 才真改：
#   先把旧版备份到同文件夹 delivery_gate_旧.py（已有备份就不覆盖），再拷新版过去（已是新版就跳过）；
#   闸门装好、自查过了才改 README（原句找不到或已是新句就跳过）。跑两次没关系。
# 用法：bash ~/claude/_底座/任务/2026-10-29_规则体系分层整理/改交付闸门.sh          （预演）
#       bash ~/claude/_底座/任务/2026-10-29_规则体系分层整理/改交付闸门.sh --执行   （真改）
exec /usr/bin/python3 -I - "$@" <<'PY'
import difflib, filecmp, json, os, shutil, subprocess, sys
from datetime import datetime
DO = '--执行' in sys.argv
H = os.path.expanduser('~')
DIR = f'{H}/claude/_底座/任务/2026-10-29_规则体系分层整理'
NEW = f'{DIR}/delivery_gate_新.py'
BAK = f'{DIR}/delivery_gate_旧.py'
LIVE = f'{H}/.claude/hooks/delivery_gate.py'
README = f'{H}/claude/_底座/README.md'
README_SWAPS = [
    ('转交成品或给出刚建的任务文件路径时被交付闸门拦下：成品已由第二级过验收官，在回复里写出任务文件路径再答一次（闸门只拦一次），不自己调验收官。',
     '交付闸门只拦本对话本轮自己改过的成品，转交第二级做好的成品、给出任务文件路径都不拦；万一被拦，不自己调验收官，'
     '先确认对应任务文件「交付」一节写了成品的完整路径、「验收结论」已填、状态已是「待验收」，再答一次（闸门只拦一次）。'),
    ('| 交付闸门（回复结束时） | 最后一条回复把本轮新改的文件交给 Dk、本轮却没调用过验收官，就拦一次；回复末尾写「草稿，未交付」可跳过；'
     '规则、记忆、`_底座/考试/` 这类工作文件不算交付物 | `~/.claude/hooks/delivery_gate.py` |',
     '| 交付闸门（回复结束时） | 最后一条回复交出本对话本轮自己改过的文件（写入工具写的，或会写文件的 Bash 命令生成、拷贝的），'
     '本轮却没调用过验收官，也没以完整路径登记在任务文件「交付」一节里（那份任务文件状态「待验收」或「已完成」、「验收结论」已填、'
     '验收后成品没再改），就拦一次，提示分第一级与第二级、执行方两种说法；回复末尾写「草稿，未交付」可跳过；'
     '规则、记忆、`_底座/考试/`、`_底座/任务/` 下的任务文件和过程文件、思考页不算交付物 | `~/.claude/hooks/delivery_gate.py` |'),
]

def selftest(path):
    """按 settings.json 的跑法（python3 -I 脚本）喂两种输入：stop_hook_active 为真、找不到 transcript。都应退出码 0、无输出、无报错。"""
    compile(open(path, encoding='utf-8').read(), path, 'exec')  # 只在内存里查语法，不留 __pycache__
    for payload in ({"stop_hook_active": True}, {"last_assistant_message": "x", "transcript_path": "/不存在.jsonl"}):
        r = subprocess.run(['/usr/bin/python3', '-I', path], input=json.dumps(payload), capture_output=True, text=True)
        if r.returncode != 0 or r.stdout.strip() or r.stderr.strip():
            return False, f'退出码 {r.returncode}，输出 {r.stdout[:80]!r}，报错 {r.stderr[:200]!r}'
    return True, '语法通过，两种输入都退出码 0、无输出'

def readme_plan():
    """[(原句, 新句, 状态)]，状态：要改（第 N 行）／已是新句／原句找不到。"""
    text = open(README, encoding='utf-8').read() if os.path.exists(README) else ''
    plan = []
    for old, new in README_SWAPS:
        n = text.count(old)
        if n == 1:
            line = text[:text.index(old)].count('\n') + 1
            plan.append((old, new, f'要改（第 {line} 行）'))
        elif n == 0 and new in text:
            plan.append((old, new, '跳过（已是新句）'))
        else:
            plan.append((old, new, f'跳过（原句出现 {n} 次，要人工看）'))
    return plan

if not os.path.exists(NEW): print(f'停：新版不存在：{NEW}'); sys.exit(1)
if not os.path.exists(LIVE): print(f'停：生效的钩子不存在：{LIVE}（settings.json 登记的就是这个路径，要人工看）'); sys.exit(1)
ok, msg = selftest(NEW)
print(f'新版自查：{"过" if ok else "不过"}（{msg}）')
if not ok: print('停：新版自查不过，没有改任何文件。'); sys.exit(1)

same = filecmp.cmp(NEW, LIVE, shallow=False)
if same:
    print(f'生效的钩子已经是新版：{LIVE}')
else:
    old = open(LIVE, encoding='utf-8').read().splitlines()
    new = open(NEW, encoding='utf-8').read().splitlines()
    diff = [l for l in difflib.unified_diff(old, new, 'delivery_gate.py（生效）', 'delivery_gate_新.py', n=0, lineterm='')]
    plus = sum(1 for l in diff if l.startswith('+') and not l.startswith('+++'))
    minus = sum(1 for l in diff if l.startswith('-') and not l.startswith('---'))
    mt = datetime.fromtimestamp(os.path.getmtime(LIVE)).strftime('%m/%d %H:%M')
    print(f'要改：{LIVE}（生效版修改于 {mt}）｜新增 {plus} 行、删掉 {minus} 行')
    print('改了什么：只认本对话本轮改过的文件（写入工具写过；或本轮被改过、且有会写文件的 Bash 提到它的文件名或文件夹'
          '——含相对命令 cwd 的写法——或跑了 _scripts/ 下的脚本而它在命令 cwd 里；cat、head、ls、grep 这类只读命令不算）；'
          '/_底座/任务/ 下和「思考页」不算交付物；成品以完整路径登记在任务文件「## 交付」节、'
          '该任务「待验收／已完成」、「## 验收结论」已填、且任务文件比成品改得晚，才放行；拦截提示分第一级、第二级和执行方两种说法。')
    print('差别（-生效版 +新版，最多 60 行）：')
    for l in diff[2:62]: print('  ' + l[:160])
    if len(diff) > 62: print(f'  ……还有 {len(diff) - 62} 行，完整差别：diff {LIVE} {NEW}')
print(f'备份：{"已有，不覆盖" if os.path.exists(BAK) else "将把生效版备份到"} {BAK}')
plan = readme_plan()
print(f'README（{README}）：')
for old, new, state in plan:
    print(f'  {state}\n    原句：{old}\n    新句：{new}')

if not DO:
    print('\n预演完毕，没有改任何文件。确认后运行：bash ~/claude/_底座/任务/2026-10-29_规则体系分层整理/改交付闸门.sh --执行'); sys.exit(0)

if not os.path.exists(BAK):
    shutil.copy2(LIVE, BAK); print(f'已备份：{BAK}')
if not same:
    shutil.copyfile(NEW, LIVE)
    ok, msg = selftest(LIVE)
    print(f'已装新版：{LIVE}｜与新版一致：{filecmp.cmp(NEW, LIVE, shallow=False)}｜自查：{"过" if ok else "不过"}（{msg}）')
    if not ok: print(f'自查不过，README 没改。恢复旧版：cp {BAK} {LIVE}'); sys.exit(1)
text = open(README, encoding='utf-8').read()
for old, new, state in plan:
    if state.startswith('要改') and text.count(old) == 1:
        text = text.replace(old, new, 1); print(f'README 已改：{state[3:-1]}')
    else:
        print(f'README 没改：{state}')
open(README, 'w', encoding='utf-8').write(text)
print('完成。')
PY
