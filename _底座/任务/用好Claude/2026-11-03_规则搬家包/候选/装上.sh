#!/bin/bash
# 装上：新环境里，把 ~/.claude/ 下的规则项建成指向本仓库的软链接（规则只留仓库里一份），并自检。长期用。
# 任务 ~/claude/_底座/任务/用好Claude/2026-11-03_规则搬家包.md；写法照思考页 7.2「M1b」，预演、执行、撤回照 11/03 的装上.sh。
# 放在仓库的 _底座/搬家/装上.sh。仓库位置按本脚本自己的位置推（往上两级），不写死 ~/claude。
#
# 建哪些链接（按仓库现有的推，加了技能重跑就会补上）：
#   ~/.claude/CLAUDE.md          → <仓库>/.claude/全局规则.md
#   ~/.claude/skills/<名>        → <仓库>/.claude/skills/<名>     （仓库里每个带 SKILL.md 的文件夹）
#   ~/.claude/agents/<名>.md     → <仓库>/.claude/agents/<名>.md
#   ~/.claude/hooks/<名>.py      → <仓库>/.claude/hooks/<名>.py
#   ~/.claude/ 下已有同名实体（或指向别处的链接）的，先移进备份夹再建链接；已是指向本仓库的链接，跳过。
#   不碰 ~/.claude/settings.json：钩子没登记或登记的路径不对时，只打印一条命令，由你自己跑。
#
# 用法：
#   bash 装上.sh [--根 <目录>]                 预演：打印每项要做什么，不改任何文件
#   bash 装上.sh --执行 [--根 <目录>]          先做完全部检查，任一不过就一个都不改；过了先备份、写装上记录，再建链接，建完逐项核
#   bash 装上.sh --自检 [--根 <目录>]          只读：逐项打印「过／不过」（全局规则每轮附上、交付闸门能拦、技能和子代理、机检自测、
#                                             settings 登记、都还是链接、规则预算）
#   bash 装上.sh --撤回 <备份夹> [--根 <目录>] 按装上记录逐项恢复，核每项回到装上前
#   --根 <目录>：只供测试，把 ~ 换成 <目录>
D="$(cd "$(dirname "$0")" && pwd -P)"
exec /usr/bin/python3 -I - "$D" "$@" <<'PY'
import datetime, hashlib, json, os, re, shutil, subprocess, sys, tempfile

HERE, ARGS = sys.argv[1], sys.argv[2:]
SCRIPT = os.path.join(HERE, '装上.sh')
REPO = os.path.realpath(os.path.join(HERE, '..', '..'))
RDOT = os.path.join(REPO, '.claude')
MANIFEST = '装上记录.json'
SKIP_SKILLS = ('synced', '.trash')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(p):
    with open(p, 'rb') as f:
        return f.read()


def tree_sha(d):
    rows = []
    for r, ds, fs in os.walk(d):
        for n in sorted(ds + fs):
            q = os.path.join(r, n)
            rel = os.path.relpath(q, d)
            if os.path.islink(q):
                rows.append(f'L {rel}\0{os.readlink(q)}\n')
            elif os.path.isfile(q):
                rows.append(f'F {rel}\0{sha(read(q))}\n')
    return sha(''.join(sorted(rows)).encode())


def state(p):  # 一项现在是什么：None / {'类型':'链接','指向'} / {'类型':'文件','sha'} / {'类型':'文件夹','sha'}
    if os.path.islink(p):
        return {'类型': '链接', '指向': os.readlink(p)}
    if os.path.isdir(p):
        return {'类型': '文件夹', 'sha': tree_sha(p)}
    if os.path.isfile(p):
        return {'类型': '文件', 'sha': sha(read(p))}
    return None


def flag_value(name):
    if name not in ARGS:
        return None
    i = ARGS.index(name)
    if i + 1 >= len(ARGS) or ARGS[i + 1].startswith('--'):
        print(f'{name} 后面要跟一个目录')
        sys.exit(2)
    return ARGS[i + 1]


UNDO_ARG, ROOT_ARG = flag_value('--撤回'), flag_value('--根')
for a in ARGS:
    if a.startswith('--') and a not in ('--执行', '--自检', '--撤回', '--根'):
        print(f'不认识的参数：{a}')
        sys.exit(2)
DO, CHECK = '--执行' in ARGS, '--自检' in ARGS
if sum(bool(x) for x in (DO, CHECK, UNDO_ARG)) > 1:
    print('--执行、--自检、--撤回 只能用一个')
    sys.exit(2)
ROOT = os.path.realpath(os.path.expanduser(ROOT_ARG or '~'))
DOT = os.path.join(ROOT, '.claude')
SETTINGS = os.path.join(DOT, 'settings.json')


def S(p):  # 打印用：把根换成 ~
    return '~' + p[len(ROOT):] if p == ROOT or p.startswith(ROOT + os.sep) else p


def B(rel):  # 备份夹里的相对路径：.claude 记作 dot-claude，免得备份里的说明和技能被当成现行的加载
    return '/'.join('dot-claude' if c == '.claude' else c for c in rel.split('/'))


def items():
    """[(~/.claude 下的相对路径, 仓库里的绝对路径, 是文件夹)]"""
    out = [('CLAUDE.md', os.path.join(RDOT, '全局规则.md'), False)]
    sd = os.path.join(RDOT, 'skills')
    for n in sorted(os.listdir(sd)) if os.path.isdir(sd) else []:
        if n not in SKIP_SKILLS and os.path.isfile(os.path.join(sd, n, 'SKILL.md')):
            out.append(('skills/' + n, os.path.join(sd, n), True))
    for sub, ext in (('agents', '.md'), ('hooks', '.py')):
        d = os.path.join(RDOT, sub)
        for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if n.endswith(ext) and os.path.isfile(os.path.join(d, n)):
                out.append((f'{sub}/{n}', os.path.join(d, n), False))
    return out


def settings_cmd():
    """改 ~/.claude/settings.json 的命令（思考页 7.4）：先备份，两条钩子命令改成 "$HOME/.claude/hooks/…"，别的键不动；
    文件不存在就只写 hooks。只打印，不执行。迁移.sh 用的是同一段。"""
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


def settings_status():
    """[(事件, 钩子文件名, 过否, 说明)]：settings.json 里两条钩子登记了没有、指向的文件在不在。"""
    try:
        d = json.load(open(SETTINGS, encoding='utf-8'))
    except FileNotFoundError:
        d = {}
    except Exception as e:
        return [('settings.json', '', False, f'读不出：{type(e).__name__}')]
    out = []
    for ev, f in (('UserPromptSubmit', 'correction_capture.py'), ('Stop', 'delivery_gate.py')):
        cmds = [h.get('command', '') for g in d.get('hooks', {}).get(ev, []) for h in g.get('hooks', []) if f in h.get('command', '')]
        if not cmds:
            out.append((ev, f, False, '没登记'))
            continue
        c = cmds[0].replace('${HOME}', ROOT).replace('$HOME', ROOT)
        m = re.search(r'["\']?((?:~|/)[^"\'\s]*' + re.escape(f) + r')', c)
        path = m.group(1) if m else ''
        path = ROOT + path[1:] if path.startswith('~/') else path
        ok = bool(path) and os.path.isfile(path)
        out.append((ev, f, ok, f'登记的是 {cmds[0]}' + ('' if ok else '，指向的文件不在')))
    return out


# ---------- --撤回 ----------
def undo():
    bk = os.path.abspath(os.path.expanduser(UNDO_ARG))
    mp = os.path.join(bk, MANIFEST)
    if not os.path.isfile(mp):
        print(f'备份夹里没有 {MANIFEST}：{bk}\n有问题，没改任何文件')
        sys.exit(1)
    man = json.load(open(mp, encoding='utf-8'))
    if man['根'] != ROOT:
        print(f'这个备份是在 {man["根"]} 下装的，现在的根是 {ROOT}；要撤回请加 --根 {man["根"]}\n有问题，没改任何文件')
        sys.exit(1)
    bad = []
    for it in man['项']:
        if it['原来'] and it['原来']['类型'] != '链接' and state(os.path.join(bk, it['备份'])) != it['原来']:
            bad.append(f'备份里的 {it["备份"]} 不在或和装上前的不一样')
    if bad:
        print('\n'.join('不过：' + b for b in bad) + '\n有问题，没改任何文件')
        sys.exit(1)
    save = os.path.join(bk, '撤回前_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    saved = []
    for it in man['项']:
        p = os.path.join(DOT, it['目标'])
        if os.path.islink(p) and os.path.realpath(p) == os.path.realpath(it['链到']):
            os.remove(p)
        elif os.path.lexists(p):
            if state(p) == it['原来']:
                continue
            dst = os.path.join(save, B('.claude/' + it['目标']))  # 装上之后又被换过的，删前另存
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            os.rename(p, dst)
            saved.append(S(p))
        o = it['原来']
        if o:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            src = os.path.join(bk, it['备份'])
            if o['类型'] == '链接':
                os.symlink(o['指向'], p)
            elif o['类型'] == '文件夹':
                shutil.copytree(src, p, symlinks=True)
            else:
                shutil.copy2(src, p)
    for d in reversed(man.get('新建的文件夹', [])):
        dp = os.path.join(ROOT, d)
        if os.path.isdir(dp) and not os.path.islink(dp) and not os.listdir(dp):
            os.rmdir(dp)
    bad = [S(os.path.join(DOT, it['目标'])) for it in man['项'] if state(os.path.join(DOT, it['目标'])) != it['原来']]
    for b in bad:
        print('核对不过：' + b + ' 没回到装上前')
    if saved:
        print(f'这 {len(saved)} 处在装上之后又被换过，删前另存在 {save}：' + '、'.join(saved))
    if bad:
        sys.exit(1)
    print(f'已撤回：{len(man["项"])} 项都回到装上前（逐项核过）；备份夹留着：{bk}')


if UNDO_ARG:
    undo()
    sys.exit(0)


# ---------- --自检（只读；临时文件放系统临时目录，跑完删）----------
def first_session_id():
    try:
        m = re.search(r'local_[0-9a-f-]{36}', open(os.path.join(REPO, '_底座', '对话定位.md'), encoding='utf-8').read())
        return m.group(0) if m else ''
    except OSError:
        return ''


def selfcheck():
    res = []
    tmp = tempfile.mkdtemp(prefix='装上自检_')
    env = dict(os.environ, HOME=ROOT, DK_HOOK_STATE_DIR=os.path.join(tmp, '状态'),
               DK_HOOK_LOG=os.path.join(tmp, '钩子日志.txt'), DK_HOOK_COMPACT_LOG=os.path.join(tmp, '压缩记录.md'))
    sid = first_session_id()
    try:
        # ① 全局规则每轮附上
        hook = os.path.join(DOT, 'hooks', 'correction_capture.py')
        try:
            first = next(l for l in open(os.path.join(RDOT, '全局规则.md'), encoding='utf-8').read().splitlines() if l.strip())
            r = subprocess.run(['/usr/bin/python3', '-I', hook], input=json.dumps(
                {'session_id': sid, 'prompt': '测试', 'hook_event_name': 'UserPromptSubmit', 'transcript_path': '', 'cwd': REPO},
                ensure_ascii=False), capture_output=True, text=True, env=env, cwd=tmp, timeout=60)
            ctx = json.loads(r.stdout)['hookSpecificOutput']['additionalContext'] if r.stdout.strip() else ''
            miss = [n for n, k in (('全局规则第一行', first), ('「本对话定位」一节', '【本对话定位'), ('本对话那一条', sid)) if not k or k not in ctx]
            res.append(('① 每轮附上全局规则和本对话定位', r.returncode == 0 and not miss,
                        f'退出码 {r.returncode}' + (f'，缺：{"、".join(miss)}' if miss else f'，附上 {len(ctx)} 字（会话 {sid}）')))
        except Exception as e:
            res.append(('① 每轮附上全局规则和本对话定位', False, f'{type(e).__name__}: {e}'))

        # ② 交付闸门能拦：本轮写了一个没登记的 .md 再在回复里交出去
        gate = os.path.join(DOT, 'hooks', 'delivery_gate.py')
        try:
            fake = next(p for p in (os.path.join(REPO, '_底座', '项目总览.md'), os.path.join(REPO, '_底座', '规则体系说明.md'))
                        if os.path.isfile(p))
            tr = os.path.join(tmp, '假会话记录.jsonl')
            with open(tr, 'w', encoding='utf-8') as f:
                for e in ({'type': 'user', 'timestamp': '2026-11-03T00:00:00.000Z', 'cwd': REPO,
                           'message': {'role': 'user', 'content': '改一下项目总览'}},
                          {'type': 'assistant', 'timestamp': '2026-11-03T00:00:01.000Z', 'cwd': REPO,
                           'message': {'role': 'assistant', 'content': [
                               {'type': 'tool_use', 'id': 't1', 'name': 'Write', 'input': {'file_path': fake, 'content': 'x'}}]}}):
                    f.write(json.dumps(e, ensure_ascii=False) + '\n')
            stdin = json.dumps({'session_id': sid, 'transcript_path': tr, 'cwd': REPO, 'hook_event_name': 'Stop',
                                'stop_hook_active': False, 'last_assistant_message': f'改好了：`{fake}`'}, ensure_ascii=False)
            note = ''
            argv = ['/usr/bin/python3', '-I', gate]
            if any(x in REPO for x in ('scratchpad', '/tmp/', '/private/var/')):
                # 闸门按设计不看临时目录里的文件；仓库在临时目录（测试时）就在内存里去掉这条排除再跑，文件不改
                note = '（仓库在临时目录，闸门按设计不看临时目录；本项在内存里去掉这条排除后跑）'
                argv = ['/usr/bin/python3', '-I', '-c',
                        'import sys\np=sys.argv[1]\ns=open(p,encoding="utf-8").read()\n'
                        'k=\'"scratchpad", "/tmp/", "/private/var/", \'\n'
                        'assert k in s, "排除清单写法变了"\n'
                        'exec(compile(s.replace(k,""),p,"exec"),{"__name__":"__main__","__file__":p})', gate]
            r = subprocess.run(argv, input=stdin, capture_output=True, text=True, env=env, cwd=tmp, timeout=60)
            ok = '"decision": "block"' in r.stdout
            res.append(('② 交付闸门能拦', ok, f'退出码 {r.returncode}，' + ('输出 "decision": "block"' if ok else f'没拦：{(r.stdout + r.stderr).strip()[:200]}') + note))
        except Exception as e:
            res.append(('② 交付闸门能拦', False, f'{type(e).__name__}: {e}'))

        # ③ 技能、子代理都是指向本仓库的链接，头部 name 读得出
        its = items()
        bad, n_s, n_a = [], 0, 0
        for rel, target, is_dir in its:
            if not rel.startswith(('skills/', 'agents/')):
                continue
            p = os.path.join(DOT, rel)
            n_s += rel.startswith('skills/')
            n_a += rel.startswith('agents/')
            if not (os.path.islink(p) and os.path.realpath(p) == os.path.realpath(target)):
                bad.append(f'{S(p)} 不是指向仓库的链接')
                continue
            f = os.path.join(p, 'SKILL.md') if is_dir else p
            head = open(f, encoding='utf-8').read().split('\n---', 1)[0] if os.path.isfile(f) else ''
            if not re.search(r'^name:\s*\S', head, re.M):
                bad.append(f'{S(f)} 头部读不出 name')
        res.append(('③ 技能、子代理都在', not bad and n_s > 0 and n_a > 0,
                    f'技能 {n_s} 个、子代理 {n_a} 个' + (f'；{"；".join(bad)}' if bad else '，都是指向仓库的链接，name 都读得出')))

        # ④ 机检自测
        r = subprocess.run(['/usr/bin/python3', '-I', os.path.join(REPO, '_底座', '工具', '机检.py'), '--自测'],
                           capture_output=True, text=True, env=env, cwd=tmp, timeout=120)
        last = (r.stdout.strip().splitlines() or [''])[-1]
        res.append(('④ 机检.py --自测', r.returncode == 0, f'退出码 {r.returncode}，末行「{last}」'))

        # ⑤ settings.json 里两条钩子登记了、指向的文件在
        st = settings_status()
        res.append(('⑤ settings.json 登记了两条钩子', all(ok for _e, _f, ok, _n in st),
                    '；'.join(f'{e}：{n}' for e, _f, _ok, n in st)))

        # ⑥ 搬过的每一项都还是指向本仓库的链接，没有一项变回实体
        bad = [S(os.path.join(DOT, rel)) for rel, target, _d in its
               if not (os.path.islink(os.path.join(DOT, rel)) and os.path.realpath(os.path.join(DOT, rel)) == os.path.realpath(target))]
        res.append(('⑥ 都还是链接', not bad, f'{len(its)} 项' + (f'，不是指向仓库的链接：{"、".join(bad)}' if bad else '都是指向仓库的链接')))

        # ⑦ 规则预算
        r = subprocess.run(['/usr/bin/python3', '-I', os.path.join(REPO, '_底座', '工具', '查规则预算.py')],
                           capture_output=True, text=True, env=env, cwd=tmp, timeout=60)
        last = (r.stdout.strip().splitlines() or [''])[-1]
        res.append(('⑦ 查规则预算.py', last == '预算：过', f'末行「{last}」' + ('' if last == '预算：过' else '：' + r.stdout.strip()[-300:])))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for name, ok, note in res:
        print(f'{"过" if ok else "不过"}　{name}：{note}')
    if not res[4][1]:
        print('\n钩子没登记或登记的路径不对。请自己跑这条命令（先备份 settings.json，只改两条钩子命令）：\n' + settings_cmd())
    n_bad = sum(not ok for _n, ok, _x in res)
    print('自检：全过' if not n_bad else f'自检：{n_bad} 项不过')
    return 0 if not n_bad else 1


if CHECK:
    sys.exit(selfcheck())


# ---------- 检查，定每项做什么（预演和 --执行 共用）----------
problems = []
if not os.path.isfile(os.path.join(RDOT, '全局规则.md')):
    problems.append(f'仓库里没有 .claude/全局规则.md（仓库按脚本位置推出来是 {REPO}；脚本应放在仓库的 _底座/搬家/ 下）')
plan = []  # (rel, target, is_dir, 动作)
for rel, target, is_dir in items():
    p = os.path.join(DOT, rel)
    parent = os.path.dirname(p)
    while parent != ROOT and len(parent) > len(ROOT):
        if os.path.islink(parent):
            problems.append(f'{S(parent)} 本身是链接，先处理它再装')
            break
        parent = os.path.dirname(parent)
    if not os.path.lexists(p):
        act = '建链接'
    elif os.path.islink(p) and os.path.realpath(p) == os.path.realpath(target):
        act = '跳过'
    else:
        act = '移进备份再建链接'
    plan.append((rel, target, is_dir, act))

print(f'仓库：{REPO}\n根：{ROOT}')
if os.path.realpath(os.path.join(ROOT, 'claude')) != REPO:
    print(f'提示：仓库不在 {S(os.path.join(ROOT, "claude"))}。规则正文里的 ~/claude/… 会找不到，'
          f'建议克隆到 ~/claude，或建一个链接：ln -s "{REPO}" "{os.path.join(ROOT, "claude")}"')
for rel, target, is_dir, act in plan:
    now = state(os.path.join(DOT, rel))
    was = '' if not now else (f'（现在是指向 {now["指向"]} 的链接）' if now['类型'] == '链接' else f'（现在是{now["类型"]}）')
    print(f'{act}　~/.claude/{rel}{was}  →  {target}')
st = settings_status()
for e, f, ok, n in st:
    print(f'settings.json {e}：{"过" if ok else "不过"}，{n}')
if problems:
    print(f'\n检查：有 {len(problems)} 处不过，加 --执行 会整个停下：')
    for p in problems:
        print('  不过：' + p)
    print('有问题，没改任何文件')
    sys.exit(1)
todo = [x for x in plan if x[3] != '跳过']
print(f'\n检查：全过。要建 {len(todo)} 个链接（其中 {sum(x[3] != "建链接" for x in todo)} 个先把原来的移进备份），跳过 {len(plan) - len(todo)} 个。')
if not DO:
    print('这是预演，没改任何文件。要执行：bash "' + SCRIPT + '" --执行' + (f' --根 "{ROOT_ARG}"' if ROOT_ARG else ''))
    sys.exit(0)
if not todo:
    print('都已是指向本仓库的链接，没什么要做。可以跑 --自检。')
    sys.exit(0)

# ---------- --执行 ----------
stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
bk = os.path.join(DOT, 'backups', f'装上_{stamp}')
new_dirs = []


def mkdirs(d):
    todo_d = []
    while not os.path.isdir(d):
        todo_d.append(d)
        d = os.path.dirname(d)
    for x in reversed(todo_d):
        os.mkdir(x)
        new_dirs.append(os.path.relpath(x, ROOT))


mkdirs(bk)
man = {'根': ROOT, '仓库': REPO, '时间': stamp, '新建的文件夹': new_dirs,
       '项': [{'目标': rel, '链到': target, '动作': act, '原来': state(os.path.join(DOT, rel)),
               '备份': B('.claude/' + rel)} for rel, target, is_dir, act in todo]}


def save_manifest():
    with open(os.path.join(bk, MANIFEST), 'w', encoding='utf-8') as f:
        json.dump(man, f, ensure_ascii=False, indent=1)


# 1. 先把要换掉的原样拷进备份夹、核过，再写装上记录；之后才动 ~/.claude
for it in man['项']:
    o = it['原来']
    if o and o['类型'] != '链接':
        src, dst = os.path.join(DOT, it['目标']), os.path.join(bk, it['备份'])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        (shutil.copytree(src, dst, symlinks=True) if o['类型'] == '文件夹' else shutil.copy2(src, dst))
        if state(dst) != o:
            print(f'备份核对不过：{it["备份"]}；还没改任何链接，备份夹 {bk} 可删')
            sys.exit(1)
save_manifest()
print(f'备份好了：{bk}')

# 2. 建链接（文件：临时链接 + os.replace，原子换上；文件夹：先移开原文件夹再建链接，原样已在备份夹）
for it in man['项']:
    p = os.path.join(DOT, it['目标'])
    mkdirs(os.path.dirname(p))
    if it['原来'] and it['原来']['类型'] == '文件夹':
        gone = os.path.join(bk, '_换下的原文件夹', it['备份'])
        os.makedirs(os.path.dirname(gone), exist_ok=True)
        os.rename(p, gone)
        os.symlink(it['链到'], p)
    else:
        tmp = p + '.装上tmp'
        if os.path.lexists(tmp):
            os.remove(tmp)
        os.symlink(it['链到'], tmp)
        os.replace(tmp, p)
save_manifest()

# 3. 核
bad = [S(os.path.join(DOT, rel)) for rel, target, _d, _a in plan
       if not (os.path.islink(os.path.join(DOT, rel)) and os.path.realpath(os.path.join(DOT, rel)) == os.path.realpath(target))]
print('\n撤回命令：\n  bash "' + SCRIPT + f'" --撤回 "{bk}"' + (f' --根 "{ROOT_ARG}"' if ROOT_ARG else ''))
if not all(ok for _e, _f, ok, _n in settings_status()):
    print('\n钩子没登记或登记的路径不对。请自己跑这条命令（先备份 settings.json，只改两条钩子命令）：\n' + settings_cmd())
if bad:
    print('核对不过：这些不是指向仓库的链接：' + '、'.join(bad) + '\n按上面的撤回命令撤回')
    sys.exit(1)
print(f'\n已装上：建了 {len(todo)} 个链接（{sum(x[3] != "建链接" for x in todo)} 个原来的已移进备份），{len(plan)} 项都核过是指向仓库的链接。'
      '\n下一步：bash "' + SCRIPT + '" --自检' + (f' --根 "{ROOT_ARG}"' if ROOT_ARG else ''))
PY
