#!/bin/bash
# 迁移：把 ~/.claude/ 下的规则搬进仓库 ~/claude/.claude/，~/.claude/ 那几项换成指向仓库的软链接（只留一份）。一次性用。
# 任务 ~/claude/_底座/任务/用好Claude/2026-11-03_规则搬家包.md；写法照思考页 7.2「M1a」，预演、执行、撤回照 11/03 的装上.sh。
#
# 改什么：
#   ~/.claude/ 下：CLAUDE.md、skills/{开工,整理纠正,验收考试,report-format,grilling,grill-me}、agents/{总验收人,流程抽查员}.md、
#                 hooks/{correction_capture,delivery_gate,deliverable_check}.py 的现行内容，按 替换对.json 改好路径写法，
#                 写进仓库 .claude/（CLAUDE.md 改名 全局规则.md），~/.claude/ 那几项换成软链接。skills/synced/ 不碰。
#   仓库 .claude/ 下新建 settings.json（只在云端跑的钩子）和 hooks/云端准备.sh。
#   弹窗标签推送系统/.claude/skills/report-format 换成指向 ../../../.claude/skills/report-format 的相对链接。
#   _底座/ 下按 替换对.json 改路径写法（README、规则体系说明、工具/README、分角色验收、备评审材料.py、查规则预算.py）。
#   挪走四个过时副本（全局规则_快照.md、设置/correction_capture_新.py、设置/settings_待Dk运行.json、工具/撤回_1029.sh）。
#   不碰 ~/.claude/settings.json（前后核 sha）；要改的那条命令只打印，由 Dk 自己跑。
#
# 用法：
#   bash 迁移.sh [--根 <目录>]                预演：打印每项改前改后，不改任何文件
#   bash 迁移.sh --执行 --根 <目录>           先做完全部检查，任一不过就一个文件都不改；过了先备份、写迁移记录、再改、改完逐项核
#                                            不写 --根 就拒绝；真切换写 --根 ~
#   bash 迁移.sh --撤回 <备份夹> [--根 <目录>] 按迁移记录逐项恢复，核每项 sha 等于切换前
#   bash 迁移.sh --对比 <输出夹> [--根 <目录>] 只读：跑「切换前后对比」三样（两个钩子喂固定输入、机检.py --自测），存进输出夹
D="$(cd "$(dirname "$0")" && pwd -P)"
exec /usr/bin/python3 -I - "$D" "$@" <<'PY'
import datetime, difflib, hashlib, json, os, re, shutil, subprocess, sys

HERE, ARGS = sys.argv[1], sys.argv[2:]
SCRIPT = os.path.join(HERE, '迁移.sh')
PAIRS_FILE = os.path.join(HERE, '替换对.json')
MANIFEST = '迁移记录.json'

# ---------- 写死的清单 ----------
SKILLS = ['开工', '整理纠正', '验收考试', 'report-format', 'grilling', 'grill-me']
# (~/.claude 下, 仓库 .claude 下, 是文件夹)
MOVES = [('CLAUDE.md', '全局规则.md', False)] + [('skills/' + s, 'skills/' + s, True) for s in SKILLS] + [
    ('agents/总验收人.md', 'agents/总验收人.md', False),
    ('agents/流程抽查员.md', 'agents/流程抽查员.md', False),
    ('hooks/correction_capture.py', 'hooks/correction_capture.py', False),
    ('hooks/delivery_gate.py', 'hooks/delivery_gate.py', False),
    ('hooks/deliverable_check.py', 'hooks/deliverable_check.py', False),
]
POPUP = '弹窗标签推送系统/.claude/skills/report-format'
POPUP_LINK = '../../../.claude/skills/report-format'
PARK = [  # 仓库内相对路径：(原位置, 挪到)
    ('_底座/全局规则_快照.md', '_底座/任务/用好Claude/2026-11-03_规则搬家包/挪走的副本/全局规则_快照.md'),
    ('_底座/设置/correction_capture_新.py', '_底座/任务/用好Claude/2026-11-03_规则搬家包/挪走的副本/correction_capture_新.py'),
    ('_底座/设置/settings_待Dk运行.json', '_底座/任务/用好Claude/2026-11-03_规则搬家包/挪走的副本/settings_待Dk运行.json'),
    ('_底座/工具/撤回_1029.sh', '_底座/任务/2026-10-29_规则体系分层整理/撤回_1029.sh'),
]
SETTINGS_NEW = json.dumps({'hooks': {
    'SessionStart': [{'hooks': [{'type': 'command', 'command': 'bash "$CLAUDE_PROJECT_DIR/.claude/hooks/云端准备.sh"', 'timeout': 10}]}],
    'UserPromptSubmit': [{'hooks': [{'type': 'command', 'timeout': 10, 'command':
        '[ "$CLAUDE_CODE_REMOTE" = "true" ] || exit 0; exec /usr/bin/python3 -I "$CLAUDE_PROJECT_DIR/.claude/hooks/correction_capture.py"'}]}],
    'Stop': [{'hooks': [{'type': 'command', 'timeout': 15, 'command':
        '[ "$CLAUDE_CODE_REMOTE" = "true" ] || exit 0; exec /usr/bin/python3 -I "$CLAUDE_PROJECT_DIR/.claude/hooks/delivery_gate.py"'}]}],
}}, ensure_ascii=False, indent=2) + '\n'
CLOUD_SH = '''#!/bin/bash
# 只在云端会话跑（SessionStart，仓库 .claude/settings.json 登记）：建 ~/claude 和 ~/.claude/CLAUDE.md 两个链接，
# 让规则正文里的 ~/claude/… 读得到、全局规则在用户级加载。本机直接退出。不输出任何东西，任何失败都 exit 0。
[ "$CLAUDE_CODE_REMOTE" = "true" ] || exit 0
{
  [ -n "$CLAUDE_PROJECT_DIR" ] || exit 0
  [ -e "$HOME/claude" ] || [ -L "$HOME/claude" ] || ln -s "$CLAUDE_PROJECT_DIR" "$HOME/claude"
  mkdir -p "$HOME/.claude"
  [ -e "$HOME/.claude/CLAUDE.md" ] || [ -L "$HOME/.claude/CLAUDE.md" ] || ln -s "$CLAUDE_PROJECT_DIR/.claude/全局规则.md" "$HOME/.claude/CLAUDE.md"
} >/dev/null 2>&1
exit 0
'''
NEW_FILES = [('.claude/settings.json', SETTINGS_NEW, 0o644), ('.claude/hooks/云端准备.sh', CLOUD_SH, 0o755)]


# ---------- 小工具 ----------
def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(p):
    with open(p, 'rb') as f:
        return f.read()


def walk_files(d):
    """文件夹里的文件（相对路径），不跟链接；里面有链接就报出来。"""
    out, links = [], []
    for r, ds, fs in os.walk(d):
        for n in ds + fs:
            q = os.path.join(r, n)
            if os.path.islink(q):
                links.append(os.path.relpath(q, d))
        for f in fs:
            q = os.path.join(r, f)
            if not os.path.islink(q):
                out.append(os.path.relpath(q, d))
    return sorted(out), links


def tree_sha(d):
    fs, _ = walk_files(d)
    return sha(''.join(f'{f}\0{sha(read(os.path.join(d, f)))}\n' for f in fs).encode())


def ent_sha(p, is_dir):
    if is_dir:
        return tree_sha(p) if os.path.isdir(p) and not os.path.islink(p) else None
    return sha(read(p)) if os.path.isfile(p) and not os.path.islink(p) else None


def flag_value(name):
    if name not in ARGS:
        return None
    i = ARGS.index(name)
    if i + 1 >= len(ARGS) or ARGS[i + 1].startswith('--'):
        print(f'{name} 后面要跟一个目录')
        sys.exit(2)
    return ARGS[i + 1]


UNDO_ARG, ROOT_ARG, CMP_ARG = flag_value('--撤回'), flag_value('--根'), flag_value('--对比')
for a in ARGS:
    if a.startswith('--') and a not in ('--执行', '--撤回', '--根', '--对比'):
        print(f'不认识的参数：{a}')
        sys.exit(2)
DO = '--执行' in ARGS
if sum(bool(x) for x in (DO, UNDO_ARG, CMP_ARG)) > 1:
    print('--执行、--撤回、--对比 只能用一个')
    sys.exit(2)
if DO and not ROOT_ARG:
    print('--执行 必须同时写 --根 <目录>（防止测试时误改本机；真切换写 --根 ~）。没改任何文件')
    sys.exit(2)
ROOT = os.path.realpath(os.path.expanduser(ROOT_ARG or '~'))
DOT = os.path.join(ROOT, '.claude')
REPO = os.path.join(ROOT, 'claude')
RDOT = os.path.join(REPO, '.claude')
SETTINGS = os.path.join(DOT, 'settings.json')


def S(p):  # 打印用：把根换成 ~
    return '~' + p[len(ROOT):] if p == ROOT or p.startswith(ROOT + os.sep) else p


def B(rel):  # 备份夹里的相对路径：.claude 记作 dot-claude，免得备份里的说明和技能被当成现行的加载
    return '/'.join('dot-claude' if c == '.claude' else c for c in rel.split('/'))


def undo_cmd(bk):
    return f'bash "{SCRIPT}" --撤回 "{bk}" --根 "{ROOT_ARG or "~"}"'


def settings_cmd():
    """改 ~/.claude/settings.json 的命令（Dk 自己跑；思考页 7.4）。只打印，不执行。"""
    p = SETTINGS if ROOT_ARG else '~/.claude/settings.json'
    return f'''/usr/bin/python3 -I - "{p}" <<'EOF'
import difflib, json, os, re, shutil, sys, time
p = os.path.expanduser(sys.argv[1])
old = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
d = json.loads(old) if old else {{}}
if old:
    b = os.path.join(os.path.dirname(p), "backups", "settings_规则搬家_" + time.strftime("%Y%m%d_%H%M%S") + ".json")
    os.makedirs(os.path.dirname(b), exist_ok=True); shutil.copy2(p, b); print("备份：" + b)
H = d.setdefault("hooks", {{}})
for ev, f, t in (("UserPromptSubmit", "correction_capture.py", 10), ("Stop", "delivery_gate.py", 15)):
    cmd = '/usr/bin/python3 -I "$HOME/.claude/hooks/%s"' % f
    hit = [h for g in H.setdefault(ev, []) for h in g.get("hooks", []) if f in h.get("command", "")]
    for h in hit: h["command"] = cmd
    if not hit: H[ev].append({{"hooks": [{{"type": "command", "command": cmd, "timeout": t}}]}})
new = json.dumps(d, ensure_ascii=False, indent=2) + "\\n"
os.makedirs(os.path.dirname(p), exist_ok=True)
open(p + ".tmp", "w", encoding="utf-8").write(new); os.replace(p + ".tmp", p)
print("".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), "改前", "改后")) or "没有变化")
EOF'''


# ---------- 切换前后对比（思考页 7.5）----------
def first_session_id():
    try:
        m = re.search(r'local_[0-9a-f-]{36}', open(os.path.join(REPO, '_底座', '对话定位.md'), encoding='utf-8').read())
        return m.group(0) if m else 'local_00000000-0000-0000-0000-000000000000'
    except OSError:
        return 'local_00000000-0000-0000-0000-000000000000'


def run_compare(out):
    os.makedirs(out, exist_ok=True)
    tmp = os.path.join(out, '_临时')
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    env = dict(os.environ, HOME=ROOT, DK_HOOK_STATE_DIR=os.path.join(tmp, '状态'),
               DK_HOOK_LOG=os.path.join(tmp, '钩子日志.txt'), DK_HOOK_COMPACT_LOG=os.path.join(tmp, '压缩记录.md'))
    sid = first_session_id()

    def run(name, argv, stdin):
        r = subprocess.run(argv, input=stdin, capture_output=True, text=True, env=env, cwd=tmp, timeout=120)
        body = r.stdout.replace(tmp, '<临时>') + f'\n退出码 {r.returncode}\n'
        if r.stderr.strip():
            body += '标准错误：\n' + r.stderr.replace(tmp, '<临时>')
        with open(os.path.join(out, name), 'w', encoding='utf-8') as f:
            f.write(body)
        return r.returncode

    run('1_correction_capture.txt', ['/usr/bin/python3', '-I', os.path.join(DOT, 'hooks', 'correction_capture.py')],
        json.dumps({'session_id': sid, 'prompt': '测试', 'hook_event_name': 'UserPromptSubmit',
                    'transcript_path': '', 'cwd': REPO}, ensure_ascii=False))
    tr = os.path.join(tmp, '假会话记录.jsonl')
    # 交付闸门按文件名跳过 CLAUDE.md、README 等，按位置跳过临时目录；所以拿 _底座/项目总览.md 当「本轮写了、没登记」的成品。
    # 仓库在临时目录（测试）时闸门照样放行，两次输出都为空；真切换（--根 ~）时两次都应是拦下。
    fake = os.path.join(REPO, '_底座', '项目总览.md')
    with open(tr, 'w', encoding='utf-8') as f:
        for e in ({'type': 'user', 'timestamp': '2026-11-03T00:00:00.000Z', 'cwd': REPO,
                   'message': {'role': 'user', 'content': '改一下项目总览'}},
                  {'type': 'assistant', 'timestamp': '2026-11-03T00:00:01.000Z', 'cwd': REPO,
                   'message': {'role': 'assistant', 'content': [
                       {'type': 'tool_use', 'id': 't1', 'name': 'Write', 'input': {'file_path': fake, 'content': 'x'}}]}}):
            f.write(json.dumps(e, ensure_ascii=False) + '\n')
    run('2_delivery_gate.txt', ['/usr/bin/python3', '-I', os.path.join(DOT, 'hooks', 'delivery_gate.py')],
        json.dumps({'session_id': sid, 'transcript_path': tr, 'cwd': REPO, 'hook_event_name': 'Stop',
                    'stop_hook_active': False, 'last_assistant_message': f'改好了：`{fake}`'}, ensure_ascii=False))
    run('3_机检自测.txt', ['/usr/bin/python3', '-I', os.path.join(REPO, '_底座', '工具', '机检.py'), '--自测'], '')
    shutil.rmtree(tmp, ignore_errors=True)


if CMP_ARG:
    out = os.path.abspath(os.path.expanduser(CMP_ARG))
    run_compare(out)
    print(f'对比输出存在 {out}（三个文件）；切换前后各跑一次，用 diff -r 比，为空即过')
    sys.exit(0)


# ---------- --撤回 ----------
def undo():
    bk = os.path.abspath(os.path.expanduser(UNDO_ARG))
    mp = os.path.join(bk, MANIFEST)
    if not os.path.isfile(mp):
        print(f'备份夹里没有 {MANIFEST}：{bk}\n有问题，没改任何文件')
        sys.exit(1)
    man = json.load(open(mp, encoding='utf-8'))
    if man['根'] != ROOT:
        print(f'这个备份是在 {man["根"]} 下迁的，现在的根是 {ROOT}；要撤回请加 --根 {man["根"]}\n有问题，没改任何文件')
        sys.exit(1)
    bad = []
    for it in man['项']:
        if it.get('备份'):
            src = os.path.join(bk, it['备份'])
            if ent_sha(src, it.get('文件夹', False)) != it['改前sha']:
                bad.append(f'备份里的 {it["备份"]} 不在或和迁移前的不一样')
    if bad:
        print('\n'.join('不过：' + b for b in bad) + '\n有问题，没改任何文件')
        sys.exit(1)
    save = os.path.join(bk, '撤回前_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    saved = []

    def keep(p, rel):  # 迁移之后又被改过的，删前先另存
        dst = os.path.join(save, B(rel))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.islink(p):
            os.symlink(os.readlink(p), dst)
        elif os.path.isdir(p):
            shutil.copytree(p, dst, symlinks=True)
        else:
            shutil.copy2(p, dst)
        saved.append(S(p))

    def remove(p):
        if os.path.islink(p) or os.path.isfile(p):
            os.remove(p)
        elif os.path.isdir(p):
            shutil.rmtree(p)

    def restore(p, src, is_dir):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + '.撤回tmp'
        remove(tmp)
        (shutil.copytree(src, tmp, symlinks=True) if is_dir else shutil.copy2(src, tmp))
        if is_dir:
            remove(p)
            os.rename(tmp, p)
        else:
            if os.path.isdir(p) and not os.path.islink(p):
                shutil.rmtree(p)
            os.replace(tmp, p)

    for it in man['项']:
        p = os.path.join(ROOT, it['目标'])
        is_dir = it.get('文件夹', False)
        act = it['动作']
        if act in ('换链接', '改', '链接到上级'):
            if ent_sha(p, is_dir) == it['改前sha']:
                continue
            if os.path.lexists(p) and not (os.path.islink(p) and act != '改'):
                if ent_sha(p, is_dir) != it.get('改后sha'):
                    keep(p, it['目标'])
            restore(p, os.path.join(bk, it['备份']), is_dir)
        elif act == '新建':
            if os.path.lexists(p):
                if ent_sha(p, is_dir) != it['改后sha']:
                    keep(p, it['目标'])
                remove(p)
        elif act == '挪走':
            to = os.path.join(ROOT, it['挪到'])
            if ent_sha(p, False) != it['改前sha']:
                if os.path.lexists(p):
                    keep(p, it['目标'])
                os.makedirs(os.path.dirname(p), exist_ok=True)
                if ent_sha(to, False) == it['改前sha']:
                    os.replace(to, p)
                else:
                    shutil.copy2(os.path.join(bk, it['备份']), p)
            if os.path.lexists(to) and ent_sha(to, False) == it['改前sha']:
                os.remove(to)
    for d in reversed(man.get('新建的文件夹', [])):
        dp = os.path.join(ROOT, d)
        if os.path.isdir(dp) and not os.path.islink(dp) and not os.listdir(dp):
            os.rmdir(dp)
    # 撤回后核
    bad = []
    for it in man['项']:
        p = os.path.join(ROOT, it['目标'])
        if it['动作'] == '新建':
            if os.path.lexists(p):
                bad.append(f'{S(p)} 还在')
        elif ent_sha(p, it.get('文件夹', False)) != it['改前sha']:
            bad.append(f'{S(p)} 没恢复')
        if it['动作'] == '挪走' and os.path.lexists(os.path.join(ROOT, it['挪到'])):
            bad.append(f'{S(os.path.join(ROOT, it["挪到"]))} 还在')
    st = sha(read(SETTINGS)) if os.path.isfile(SETTINGS) else None
    if st != man.get('settings_sha'):
        bad.append('~/.claude/settings.json 和迁移前不同（本脚本不碰它；若 Dk 已跑过改 settings 的命令，用那条命令打印的备份恢复）')
    for b in bad:
        print('核对不过：' + b)
    if saved:
        print(f'这 {len(saved)} 处在迁移之后又被改过，删前另存在 {save}：' + '、'.join(saved))
    if bad:
        sys.exit(1)
    print(f'已撤回：{len(man["项"])} 项都回到迁移前（sha 逐项核过）；备份夹留着：{bk}')


if UNDO_ARG:
    undo()
    sys.exit(0)


# ---------- 检查，算出改后的样子（预演和 --执行 共用）----------
problems = []
pairs = json.load(open(PAIRS_FILE, encoding='utf-8')) if os.path.isfile(PAIRS_FILE) else None
if pairs is None:
    problems.append(f'找不到 {PAIRS_FILE}')
    pairs = []


def target_source(t):  # 替换对的目标 → 现行内容所在
    if t.startswith('.claude/'):
        rel = t[len('.claude/'):]
        for a, b, is_dir in MOVES:
            if rel == b:
                return os.path.join(DOT, a)
            if is_dir and rel.startswith(b + '/'):
                return os.path.join(DOT, a, rel[len(b) + 1:])
        return None
    return os.path.join(REPO, t)


content = {}  # 目标 → 改后的文本
orig = {}
for i, p in enumerate(pairs, 1):
    t = p['目标']
    src = target_source(t)
    if src is None or not os.path.isfile(src):
        problems.append(f'替换对第 {i} 条的目标 {t} 找不到现行文件')
        continue
    if t not in content:
        orig[t] = content[t] = read(src).decode('utf-8')
    n = content[t].count(p['原句'])
    if n != 1:
        problems.append(f'替换对第 {i} 条（{t}）原句出现 {n} 次，要恰好 1 次：{p["原句"][:50]}…')
    else:
        content[t] = content[t].replace(p['原句'], p['新句'])

plan_moves = []
for a, b, is_dir in MOVES:
    src, dst = os.path.join(DOT, a), os.path.join(RDOT, b)
    if not os.path.lexists(src):
        problems.append(f'{S(src)} 不在')
        continue
    if os.path.islink(src):
        problems.append(f'{S(src)} 已经是链接（指向 {os.readlink(src)}），像是迁过了')
        continue
    if is_dir:
        if not os.path.isdir(src):
            problems.append(f'{S(src)} 应是文件夹')
            continue
        fs, links = walk_files(src)
        if links:
            problems.append(f'{S(src)} 里有链接：{links}')
        if 'SKILL.md' not in fs:
            problems.append(f'{S(src)} 里没有 SKILL.md')
    elif not os.path.isfile(src):
        problems.append(f'{S(src)} 应是文件')
        continue
    if os.path.lexists(dst):
        problems.append(f'仓库里已有 {S(dst)}')
    plan_moves.append((a, b, is_dir, src, dst))

for rel, _txt, _m in NEW_FILES:
    if os.path.lexists(os.path.join(REPO, rel)):
        problems.append(f'仓库里已有 {S(os.path.join(REPO, rel))}')

popup = os.path.join(REPO, POPUP)
if not os.path.isdir(popup) or os.path.islink(popup):
    problems.append(f'{S(popup)} 不在或已是链接')
elif tree_sha(popup) != tree_sha(os.path.join(DOT, 'skills', 'report-format')):
    problems.append(f'{S(popup)} 和 ~/.claude/skills/report-format 内容不同（弹窗可能正在改它），停下回报第二级')

for a, b in PARK:
    if not os.path.isfile(os.path.join(REPO, a)) or os.path.islink(os.path.join(REPO, a)):
        problems.append(f'要挪走的 {S(os.path.join(REPO, a))} 不在')
    if os.path.lexists(os.path.join(REPO, b)):
        problems.append(f'挪去的位置已有文件：{S(os.path.join(REPO, b))}')
settings_before = sha(read(SETTINGS)) if os.path.isfile(SETTINGS) else None


def show_diff(t, label):
    a, b = orig[t].splitlines(True), content[t].splitlines(True)
    print(''.join(difflib.unified_diff(a, b, f'{label}（改前）', f'{label}（改后）', n=0)))


print(f'根：{ROOT}   仓库：{S(REPO)}   替换对：{len(pairs)} 条（sha256 {sha(read(PAIRS_FILE)) if os.path.isfile(PAIRS_FILE) else "—"}）')
print('\n== 1. 搬进仓库、~/.claude 下换成链接 ==')
for a, b, is_dir, src, dst in plan_moves:
    print(f'{S(src)}{"/" if is_dir else ""}  →  {S(dst)}{"/" if is_dir else ""}，原处换成链接')
print('\n== 2. 路径写法（替换对）==')
for t in content:
    show_diff(t, t)
print('== 3. 仓库 .claude/ 下新建 ==')
for rel, txt, _m in NEW_FILES:
    print(f'--- {rel}\n{txt}')
print(f'== 4. 弹窗项目的 report-format 换成链接 ==\n{S(popup)} → {POPUP_LINK}')
print('\n== 5. 挪走的副本 ==')
for a, b in PARK:
    print(f'{a}  →  {b}')
print(f'\n== 6. 不碰 ==\n~/.claude/settings.json（sha256 {settings_before}）、~/.claude/skills/synced/、~/.claude/ 下别的东西')

if problems:
    print(f'\n检查：有 {len(problems)} 处不过，加 --执行 会整个停下：')
    for p in problems:
        print('  不过：' + p)
    print('有问题，没改任何文件')
    sys.exit(1)
print('\n检查：全过。')
if not DO:
    print('这是预演，没改任何文件。要执行：bash "' + SCRIPT + '" --执行 --根 ' + (ROOT_ARG or '~'))
    sys.exit(0)


# ---------- --执行 ----------
stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
bk = os.path.join(DOT, 'backups', f'规则搬家_{stamp}')
os.makedirs(bk)
run_compare(os.path.join(bk, '对比_切换前'))

new_dirs = []


def mkdirs(d):  # 记下新建的文件夹，撤回时删空的
    todo = []
    while not os.path.isdir(d):
        todo.append(d)
        d = os.path.dirname(d)
    for x in reversed(todo):
        os.mkdir(x)
        new_dirs.append(os.path.relpath(x, ROOT))


def planned_bytes(b, rel_in_dir=None):
    t = '.claude/' + b + ('/' + rel_in_dir if rel_in_dir else '')
    return content[t].encode('utf-8') if t in content else None


# 1. 先算好每项改后的 sha，写迁移记录（撤回靠它），再动手
items = []
for a, b, is_dir, src, dst in plan_moves:
    items.append({'动作': '换链接', '目标': os.path.relpath(src, ROOT), '文件夹': is_dir, '改前sha': ent_sha(src, is_dir),
                  '备份': B(os.path.relpath(src, ROOT)), '链到': dst})
    items.append({'动作': '新建', '目标': os.path.relpath(dst, ROOT), '文件夹': is_dir, '改后sha': None})
for rel, txt, _m in NEW_FILES:
    items.append({'动作': '新建', '目标': os.path.relpath(os.path.join(REPO, rel), ROOT), '改后sha': sha(txt.encode())})
items.append({'动作': '链接到上级', '目标': os.path.relpath(popup, ROOT), '文件夹': True, '改前sha': tree_sha(popup),
              '备份': B(os.path.relpath(popup, ROOT))})
for t in content:
    if not t.startswith('.claude/'):
        p = os.path.join(REPO, t)
        items.append({'动作': '改', '目标': os.path.relpath(p, ROOT), '改前sha': sha(orig[t].encode()),
                      '改后sha': sha(content[t].encode()), '备份': B(os.path.relpath(p, ROOT))})
for a, b2 in PARK:
    p = os.path.join(REPO, a)
    items.append({'动作': '挪走', '目标': os.path.relpath(p, ROOT), '挪到': os.path.relpath(os.path.join(REPO, b2), ROOT),
                  '改前sha': sha(read(p)), '备份': B(os.path.relpath(p, ROOT))})
man = {'根': ROOT, '时间': stamp, '替换对sha': sha(read(PAIRS_FILE)), 'settings_sha': settings_before, '项': items,
       '新建的文件夹': new_dirs}


def save_manifest():
    with open(os.path.join(bk, MANIFEST), 'w', encoding='utf-8') as f:
        json.dump(man, f, ensure_ascii=False, indent=1)


# 2. 备份：要改的、要换链接的、要挪走的，都原样拷进备份夹
for it in items:
    if it.get('备份'):
        s, d = os.path.join(ROOT, it['目标']), os.path.join(bk, it['备份'])
        os.makedirs(os.path.dirname(d), exist_ok=True)
        (shutil.copytree(s, d, symlinks=True) if it.get('文件夹') else shutil.copy2(s, d))
        if ent_sha(d, it.get('文件夹', False)) != it['改前sha']:
            print(f'备份核对不过：{it["备份"]}；还没改任何文件，备份夹 {bk} 可删')
            sys.exit(1)
save_manifest()
print(f'备份好了：{bk}')

# 3. 写仓库 .claude/ 下的文件（先写临时的再 os.replace / rename）
mkdirs(RDOT)
for a, b, is_dir, src, dst in plan_moves:
    mkdirs(os.path.dirname(dst))
    tmp = dst + '.迁移tmp'
    if is_dir:
        shutil.copytree(src, tmp, symlinks=True)
        for f in walk_files(tmp)[0]:
            nb = planned_bytes(b, f)
            if nb is not None:
                with open(os.path.join(tmp, f), 'wb') as fh:
                    fh.write(nb)
        os.rename(tmp, dst)
    else:
        shutil.copy2(src, tmp)
        nb = planned_bytes(b)
        if nb is not None:
            with open(tmp, 'wb') as fh:
                fh.write(nb)
        os.replace(tmp, dst)
    for it in items:
        if it['动作'] == '新建' and it['目标'] == os.path.relpath(dst, ROOT):
            it['改后sha'] = ent_sha(dst, is_dir)
save_manifest()

# 4. ~/.claude 下换成链接（文件：临时链接 + os.replace；文件夹：拿走原文件夹再建链接，原样已在备份夹）
for a, b, is_dir, src, dst in plan_moves:
    if is_dir:
        gone = os.path.join(bk, '_换下的原文件夹', B(os.path.relpath(src, ROOT)))
        os.makedirs(os.path.dirname(gone), exist_ok=True)
        os.rename(src, gone)
        os.symlink(dst, src)
    else:
        tmp = src + '.迁移tmp'
        os.symlink(dst, tmp)
        os.replace(tmp, src)

# 5. 新建仓库 .claude/settings.json 和 hooks/云端准备.sh
for rel, txt, mode in NEW_FILES:
    p = os.path.join(REPO, rel)
    mkdirs(os.path.dirname(p))
    with open(p + '.迁移tmp', 'w', encoding='utf-8') as f:
        f.write(txt)
    os.chmod(p + '.迁移tmp', mode)
    os.replace(p + '.迁移tmp', p)

# 6. 弹窗项目的 report-format 换成相对链接
gone = os.path.join(bk, '_换下的原文件夹', B(os.path.relpath(popup, ROOT)))
os.makedirs(os.path.dirname(gone), exist_ok=True)
os.rename(popup, gone)
os.symlink(POPUP_LINK, popup)

# 7. 改 _底座/ 下那几份
for t in content:
    if t.startswith('.claude/'):
        continue
    p = os.path.join(REPO, t)
    tmp = p + '.迁移tmp'
    shutil.copy2(p, tmp)
    with open(tmp, 'wb') as fh:
        fh.write(content[t].encode('utf-8'))
    os.replace(tmp, p)

# 8. 挪走四个副本
for a, b2 in PARK:
    to = os.path.join(REPO, b2)
    mkdirs(os.path.dirname(to))
    os.rename(os.path.join(REPO, a), to)
save_manifest()

# 9. 核
bad = []
for a, b, is_dir, src, dst in plan_moves:
    if not os.path.islink(src) or os.path.realpath(src) != os.path.realpath(dst):
        bad.append(f'{S(src)} 不是指向 {S(dst)} 的链接')
    want = next(it['改后sha'] for it in items if it['动作'] == '新建' and it['目标'] == os.path.relpath(dst, ROOT))
    if ent_sha(os.path.realpath(src), is_dir) != want:
        bad.append(f'{S(src)} 链过去的内容和写进仓库的不同')
    if is_dir:
        for f in walk_files(dst)[0]:
            nb = planned_bytes(b, f)
            want_b = nb if nb is not None else read(os.path.join(bk, B(os.path.relpath(src, ROOT)), f))
            if read(os.path.join(dst, f)) != want_b:
                bad.append(f'{S(dst)}/{f} 内容不是预期')
    else:
        nb = planned_bytes(b)
        want_b = nb if nb is not None else read(os.path.join(bk, B(os.path.relpath(src, ROOT))))
        if read(dst) != want_b:
            bad.append(f'{S(dst)} 内容不是预期')
if os.path.realpath(popup) != os.path.realpath(os.path.join(RDOT, 'skills', 'report-format')):
    bad.append(f'{S(popup)} 没链到仓库 .claude/skills/report-format')
for t in content:
    if not t.startswith('.claude/') and sha(read(os.path.join(REPO, t))) != sha(content[t].encode()):
        bad.append(f'{t} 内容不是预期')
for a, b2 in PARK:
    if os.path.lexists(os.path.join(REPO, a)) or not os.path.isfile(os.path.join(REPO, b2)):
        bad.append(f'{a} 没挪好')
if (sha(read(SETTINGS)) if os.path.isfile(SETTINGS) else None) != settings_before:
    bad.append('~/.claude/settings.json 变了（本脚本不该碰它）')
r = subprocess.run(['/usr/bin/python3', '-I', os.path.join(REPO, '_底座', '工具', '查规则预算.py')],
                   capture_output=True, text=True, env=dict(os.environ, HOME=ROOT))
last = (r.stdout.strip().splitlines() or [''])[-1]
print('查规则预算.py：\n' + r.stdout.strip())
if last != '预算：过':
    bad.append(f'查规则预算.py 最后一行是「{last}」，不是「预算：过」')
run_compare(os.path.join(bk, '对比_切换后'))
d = subprocess.run(['diff', '-r', os.path.join(bk, '对比_切换前'), os.path.join(bk, '对比_切换后')], capture_output=True, text=True)
if d.returncode != 0:
    bad.append('切换前后对比不一致：\n' + d.stdout[:3000])
else:
    print('切换前后对比：三样输出逐字一致（' + os.path.join(bk, '对比_切换前') + ' 对 对比_切换后）')

print('\n撤回命令（抄进交接记录）：\n  ' + undo_cmd(bk))
print('\n请 Dk 自己跑的命令（改 ~/.claude/settings.json 里两条钩子命令，把写死的用户名换成 $HOME；先备份）：\n' + settings_cmd())
if bad:
    for b in bad:
        print('核对不过：' + b)
    print('改动已做，但核对不过；按上面的撤回命令撤回')
    sys.exit(1)
print(f'\n已迁移：{len(plan_moves)} 项换成链接、{len([t for t in content if not t.startswith(".claude/")])} 份 _底座 文件改了路径写法、'
      f'挪走 {len(PARK)} 个副本；逐项核过。迁移记录：{os.path.join(bk, MANIFEST)}')
PY
