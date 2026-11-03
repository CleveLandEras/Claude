#!/bin/bash
# 装上（拷贝版）：新环境里，把仓库里的规则包拷进 ~/.claude/，按 路径替换.json 改 _底座/ 里写死旧电脑家目录的地方，再自检。长期用。
# 任务 ~/claude/_底座/任务/用好Claude/2026-11-03_规则搬家包.md；做法照思考页 7.3「M2'」，框架改自同任务文件夹的 候选/装上.sh（链接版）。
# 放在仓库的 _底座/搬家/装上.sh。仓库位置按本脚本自己的位置推（往上两级）。
#
# 拷哪些（按规则包现有的推，导出时加了技能，这里跟着多拷）：
#   _底座/全局规则_快照.md           → ~/.claude/CLAUDE.md
#   _底座/搬家/规则包/skills/<名>/   → ~/.claude/skills/<名>/
#   _底座/搬家/规则包/agents/<名>.md → ~/.claude/agents/<名>.md
#   _底座/搬家/规则包/hooks/<名>.py  → ~/.claude/hooks/<名>.py
#   ~/.claude/ 下已有同名的，先原样拷进备份夹 ~/.claude/backups/规则搬家_装上_<时间>/dot-claude/…；内容已一样的跳过。
#   文件用「临时文件 + os.replace」换上，文件夹先在备份夹里拷好再改名换上。
# 改 _底座/：按 _底座/搬家/路径替换.json。「逐条」一类原句恰好出现一次才改；「通用」一类把旧电脑家目录换成 ~。
#   {旧家} 代表旧电脑的家目录，表里不写用户名，装上时按「逐条」的原句在文件里认出它。改的是新克隆里已跟踪的文件，下次提交时一起提交。
# 不碰 ~/.claude/settings.json：按 规则包/钩子登记.json 打印一条命令，由你自己跑（先备份，只合并 hooks 一段）。
#
# 前提（任一不过就拒绝 --执行）：
#   仓库要在 ~/claude（realpath 相同；~/claude 是指向仓库的链接也算）。规则正文、钩子都按 ~/claude/… 找文件。
#   本机保护：~/.claude/ 下有一项和 规则包/清单.json 记的「来源 sha」相同（只看导出时改过路径的那几项），
#   说明这台正是导出规则包的旧环境，拒绝 --执行。只按 sha 判。
#   旧电脑家目录和现在的家目录相同（新电脑用同一个用户名）时不拒绝，_底座/ 的路径照常替换。
#
# 用法：
#   bash 装上.sh [--根 <目录>]                 预演：打印每项要做什么，不改任何文件
#   bash 装上.sh --执行 [--根 <目录>]          检查全过才动手：先备份、写装上记录，再拷、再改 _底座/，做完逐项核
#   bash 装上.sh --自检 [--根 <目录>]          只读，逐项打印「过／不过」，九项（见 selfcheck）
#   bash 装上.sh --撤回 <备份夹> [--根 <目录>] 按装上记录恢复 ~/.claude/ 各项和 _底座/ 被改的文件，逐项核 sha
#   --根 <目录>：只供测试，把 ~ 换成 <目录>
# 退出码：0 过；1 自检或撤回有不过；2 用法错；3 检查不过（一个文件都没改）
D="$(cd "$(dirname "$0")" && pwd -P)"
exec /usr/bin/python3 -I - "$D" "$@" <<'PY'
import datetime, hashlib, json, os, re, shutil, subprocess, sys, tempfile

HERE, ARGS = sys.argv[1], sys.argv[2:]
SCRIPT = os.path.join(HERE, '装上.sh')
REPO = os.path.realpath(os.path.join(HERE, '..', '..'))
BASE = os.path.join(REPO, '_底座')
PACK = os.path.join(HERE, '规则包')
SNAP = os.path.join(BASE, '全局规则_快照.md')
REPL = os.path.join(HERE, '路径替换.json')
REG = os.path.join(PACK, '钩子登记.json')
LIST = os.path.join(PACK, '清单.json')
RECORD = '装上记录.json'
SKIP_FILES = ('.DS_Store',)
BAD_NAMES = ('.claude', '.claude-plugin', 'CLAUDE.md', 'CLAUDE.local.md', 'AGENTS.md')
HOME_RE = r'/(?:Users|home)/[A-Za-z0-9_][A-Za-z0-9._-]*'  # 家目录的样子：/Users/<名>、/home/<名>（名不以 . 开头，免得认错 改前/home/.claude）
HOME_HIT = re.compile(HOME_RE + r'(?![A-Za-z0-9._-])')
OLD = '{旧家}'


def die(msg, code=2):
    print(msg)
    sys.exit(code)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(p):
    with open(p, 'rb') as f:
        return f.read()


def dir_sha(d):  # 和 导出.sh 的算法一样：「文件夹内相对路径\0文件 sha256\n」按路径排序拼起来再算（不含 .DS_Store）
    rows = {}
    for r, ds, fs in os.walk(d):
        for n in fs:
            if n in SKIP_FILES:
                continue
            q = os.path.join(r, n)
            rows[os.path.relpath(q, d)] = ('L:' + os.readlink(q)) if os.path.islink(q) else sha(read(q))
    return sha(''.join(f'{k}\0{rows[k]}\n' for k in sorted(rows)).encode())


def state(p):  # None / {'类型':'链接','指向'} / {'类型':'文件夹','sha'} / {'类型':'文件','sha'}
    if os.path.islink(p):
        return {'类型': '链接', '指向': os.readlink(p)}
    if os.path.isdir(p):
        return {'类型': '文件夹', 'sha': dir_sha(p)}
    if os.path.isfile(p):
        return {'类型': '文件', 'sha': sha(read(p))}
    return None


def flag_value(name):
    if name not in ARGS:
        return None
    i = ARGS.index(name)
    if i + 1 >= len(ARGS) or ARGS[i + 1].startswith('--'):
        die(f'{name} 后面要跟一个目录')
    return ARGS[i + 1]


UNDO_ARG, ROOT_ARG = flag_value('--撤回'), flag_value('--根')
rest = list(ARGS)
for f in ('--撤回', '--根'):
    if f in rest:
        i = rest.index(f)
        del rest[i:i + 2]
for a in rest:
    if a not in ('--执行', '--自检'):
        die(f'不认识的参数：{a}')
DO, CHECK = '--执行' in rest, '--自检' in rest
if sum(bool(x) for x in (DO, CHECK, UNDO_ARG)) > 1:
    die('--执行、--自检、--撤回 只能用一个')
ROOT = os.path.realpath(os.path.expanduser(ROOT_ARG or '~'))
DOT = os.path.join(ROOT, '.claude')
SETTINGS = os.path.join(DOT, 'settings.json')
ROOT_FLAG = f' --根 "{ROOT_ARG}"' if ROOT_ARG else ''


def S(p):  # 打印用：把根换成 ~
    return '~' + p[len(ROOT):] if p == ROOT or p.startswith(ROOT + os.sep) else p


def R(p):  # 打印用：仓库里的相对路径
    return os.path.relpath(p, REPO)


def B(rel):  # 备份夹里的相对路径：.claude 记作 dot-claude，免得备份里的说明和技能被当成现行的加载
    return '/'.join('dot-claude' if c == '.claude' else c for c in rel.split('/'))


def items():
    """[(~/.claude 下的相对路径, 来源绝对路径, 是文件夹)]"""
    out = [('CLAUDE.md', SNAP, False)]
    sd = os.path.join(PACK, 'skills')
    for n in sorted(os.listdir(sd)) if os.path.isdir(sd) else []:
        if os.path.isfile(os.path.join(sd, n, 'SKILL.md')):
            out.append(('skills/' + n, os.path.join(sd, n), True))
    for sub, ext in (('agents', '.md'), ('hooks', '.py')):
        d = os.path.join(PACK, sub)
        for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if n.endswith(ext) and os.path.isfile(os.path.join(d, n)):
                out.append((f'{sub}/{n}', os.path.join(d, n), False))
    return out


def src_state(src, is_dir):
    return {'类型': '文件夹', 'sha': dir_sha(src)} if is_dir else {'类型': '文件', 'sha': sha(read(src))}


# ---------- 路径替换.json ----------
def load_repl():
    try:
        return json.loads(read(REPL).decode('utf-8'))
    except FileNotFoundError:
        return None


def repl_targets(rep):
    ts = [e['目标'] for e in rep.get('逐条', [])] + list(rep.get('通用', {}).get('目标', []))
    return list(dict.fromkeys(ts))


def pattern(orig):
    if orig.count(OLD) != 1:
        raise ValueError(f'原句里 {OLD} 要恰好一个：{orig}')
    return re.compile(re.escape(orig).replace(re.escape(OLD), '(' + HOME_RE + '|' + re.escape(ROOT) + ')'))


def plan_repl(problems):
    """返回 (改后内容 {仓库相对路径: 字节}, 打印行, 认出的旧家目录或 None)"""
    rep = load_repl()
    if rep is None:
        problems.append(f'找不到 {R(REPL)}')
        return {}, [], None
    texts, lines, olds = {}, [], set()

    def cur(t):
        if t not in texts:
            p = os.path.join(REPO, t)
            texts[t] = read(p).decode('utf-8') if os.path.isfile(p) else None
        return texts[t]
    orig = {}
    for k, e in enumerate(rep.get('逐条', []), 1):
        t = e['目标']
        s = cur(t)
        if s is None:
            problems.append(f'路径替换 逐条第 {k} 条：找不到 {t}')
            continue
        orig.setdefault(t, s)
        try:
            ms = list(pattern(e['原句']).finditer(s))
        except (ValueError, re.error) as ex:
            problems.append(f'路径替换 逐条第 {k} 条写法不对：{ex}')
            continue
        if len(ms) == 1:
            olds.add(ms[0].group(1))
            texts[t] = s[:ms[0].start()] + e['新句'] + s[ms[0].end():]
            lines.append(f'改　{t}：逐条第 {k} 条')
        elif not ms and s.count(e['新句']) == 1:
            lines.append(f'跳过　{t}：逐条第 {k} 条已改过')
        else:
            problems.append(f'路径替换 逐条第 {k} 条（{t}）：原句出现 {len(ms)} 次，要恰好 1 次')
    if len(olds) > 1:
        problems.append('路径替换：逐条原句里认出的旧家目录不止一个：' + '、'.join(sorted(olds)))
    old = next(iter(olds)) if len(olds) == 1 else None
    gen = rep.get('通用', {}).get('目标', [])
    if old is None and gen:
        lines.append('提醒：逐条都已改过、认不出旧家目录，通用一类跳过（--自检 第 8 项会查出没改到的）')
    elif old:
        rx = re.compile(re.escape(old) + r'(?![A-Za-z0-9._-])')
        for t in gen:
            s = cur(t)
            if s is None:
                problems.append(f'路径替换 通用：找不到 {t}')
                continue
            orig.setdefault(t, s)
            s2, n = rx.subn('~', s)
            texts[t] = s2
            lines.append(f'改　{t}：通用 {n} 处' if n else f'跳过　{t}：通用 0 处')
    out = {t: texts[t].encode('utf-8') for t in texts if texts[t] is not None and texts[t] != orig.get(t)}
    return out, lines, old


# ---------- settings.json ----------
def reg_hooks():
    try:
        return json.loads(read(REG).decode('utf-8')).get('hooks', {})
    except FileNotFoundError:
        return {}


def hook_file(cmd):
    m = re.search(r'([^/\s"\']+\.py)', cmd)
    return m.group(1) if m else ''


def settings_cmd():
    """改 settings.json 的命令：先备份，按 钩子登记.json 只合并 hooks 一段（同一事件里命令含同名钩子文件的就换命令，
    没有就加一组），别的键不动；文件不存在时只写 hooks。打印改前改后差异。只打印，不执行。"""
    p = SETTINGS if ROOT_ARG else '~/.claude/settings.json'
    g = REG if ROOT_ARG else '~/claude/_底座/搬家/规则包/钩子登记.json'
    return f'''/usr/bin/python3 -I - "{p}" "{g}" <<'EOF'
import difflib, json, os, re, shutil, sys, time
p, g = os.path.expanduser(sys.argv[1]), os.path.expanduser(sys.argv[2])
reg = json.load(open(g, encoding="utf-8"))["hooks"]
old = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
d = json.loads(old) if old else {{}}
if old:
    b = os.path.join(os.path.dirname(p), "backups", "settings_规则搬家_" + time.strftime("%Y%m%d_%H%M%S") + ".json")
    os.makedirs(os.path.dirname(b), exist_ok=True); shutil.copy2(p, b); print("备份：" + b)
H = d.setdefault("hooks", {{}})
for ev, groups in reg.items():
    for grp in groups:
        for h in grp.get("hooks", []):
            m = re.search(r"([^/\\s\\"']+\\.py)", h["command"]); f = m.group(1) if m else h["command"]
            hit = [x for gg in H.setdefault(ev, []) for x in gg.get("hooks", []) if f in x.get("command", "")]
            for x in hit: x["command"] = h["command"]
            if not hit: H[ev].append({{"hooks": [dict(h)]}})
new = json.dumps(d, ensure_ascii=False, indent=2) + "\\n"
os.makedirs(os.path.dirname(p), exist_ok=True)
open(p + ".tmp", "w", encoding="utf-8").write(new); os.replace(p + ".tmp", p)
print("".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), "改前", "改后")) or "没有变化")
EOF'''


def settings_status():
    """[(事件, 钩子文件名, 过否, 说明)]：钩子登记.json 里的每条钩子，settings.json 登记了没有、指向的文件在不在。"""
    try:
        d = json.loads(read(SETTINGS).decode('utf-8'))
    except FileNotFoundError:
        d = {}
    except Exception as e:
        return [('settings.json', '', False, f'读不出：{type(e).__name__}')]
    out = []
    for ev, groups in reg_hooks().items():
        for grp in groups:
            for h in grp.get('hooks', []):
                f = hook_file(h.get('command', ''))
                cmds = [x.get('command', '') for g in d.get('hooks', {}).get(ev, []) for x in g.get('hooks', [])
                        if f and f in x.get('command', '')]
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


# ---------- 前提 ----------
def protection():
    """本机保护：返回命中的说明列表（空＝不是导出规则包的那台）。"""
    hits = []
    try:
        man = json.loads(read(LIST).decode('utf-8'))
    except FileNotFoundError:
        return [f'找不到 {R(LIST)}，没法判是不是导出规则包的旧环境']
    its = man.get('项', [])
    look = [e for e in its if e.get('来源sha') != e.get('规则包sha')] or its
    for e in look:
        n = e['名']
        if e.get('种类') == '钩子登记':
            try:
                h = json.loads(read(SETTINGS).decode('utf-8')).get('hooks')
                cur = sha(json.dumps(h, ensure_ascii=False, sort_keys=True).encode('utf-8')) if h is not None else None
            except Exception:
                cur = None
        else:
            p = os.path.join(DOT, n)
            cur = dir_sha(p) if os.path.isdir(p) else (sha(read(p)) if os.path.isfile(p) else None)
        if cur == e.get('来源sha'):
            hits.append(n)
    return hits


def check_all():
    """预演和 --执行 共用：返回 (problems, plan, repl_out, repl_lines, old_home)"""
    problems = []
    for p, what in ((SNAP, '全局规则快照'), (PACK, '规则包'), (LIST, '规则包/清单.json'), (REPL, '路径替换.json')):
        if not os.path.exists(p):
            problems.append(f'找不到{what}：{R(p)}（脚本应放在仓库的 _底座/搬家/ 下）')
    if problems:
        return problems, [], {}, [], None
    if os.path.realpath(os.path.join(ROOT, 'claude')) != REPO:
        problems.append(f'仓库不在 {S(os.path.join(ROOT, "claude"))}（仓库在 {REPO}）：克隆到 ~/claude，'
                        f'或建一个链接 ln -s "{REPO}" "{os.path.join(ROOT, "claude")}"')
    hits = protection()
    if hits:
        problems.append(f'本机保护：这台像是导出规则包的旧环境，~/.claude/ 下 {len(hits)} 项和导出时的来源一样（'
                        + '、'.join(hits) + '），拒绝 --执行')
    plan = []
    for rel, src, is_dir in items():
        p = os.path.join(DOT, rel)
        par = os.path.dirname(p)
        while par != ROOT and len(par) > len(ROOT):
            if os.path.islink(par):
                problems.append(f'{S(par)} 本身是链接，先处理它再装')
                break
            par = os.path.dirname(par)
        now = state(p)
        want = src_state(src, is_dir)
        act = '拷' if now is None else ('跳过' if now == want else '先备份再换')
        plan.append((rel, src, is_dir, act, now, want))
    out, lines, old = plan_repl(problems)  # 旧家目录和现在相同（新电脑同名）也照常替换，不拒绝（第二级 11/03 定）
    return problems, plan, out, lines, old


# ---------- --撤回 ----------
def undo():
    bk = os.path.abspath(os.path.expanduser(UNDO_ARG))
    mp = os.path.join(bk, RECORD)
    if not os.path.isfile(mp):
        die(f'备份夹里没有 {RECORD}：{bk}\n有问题，没改任何文件', 1)
    man = json.loads(read(mp).decode('utf-8'))
    if man['根'] != ROOT or man['仓库'] != REPO:
        die(f'这个备份是在 根 {man["根"]}、仓库 {man["仓库"]} 下装的，现在是 根 {ROOT}、仓库 {REPO}\n有问题，没改任何文件', 1)
    bad = [f'备份里的 {it["备份"]} 不在或和装上前的不一样' for it in man['项'] + man['仓库文件']
           if it['原来'] and state(os.path.join(bk, it['备份'])) != it['原来']]
    if bad:
        die('\n'.join('不过：' + b for b in bad) + '\n有问题，没改任何文件', 1)
    save = os.path.join(bk, '撤回前_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    saved = []

    def put_back(p, it, tag):
        now = state(p)
        if now == it['原来']:
            return
        if now is not None:
            if now != it['装上后']:  # 装上之后又被改过的，删前另存
                dst = os.path.join(save, tag)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(p, dst)
                saved.append(S(p))
            elif os.path.isdir(p) and not os.path.islink(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
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
    for it in man['项']:
        put_back(os.path.join(DOT, it['目标']), it, it['备份'])
    for it in man['仓库文件']:
        put_back(os.path.join(REPO, it['目标']), it, it['备份'])
    for d in reversed(man.get('新建的文件夹', [])):
        dp = os.path.join(ROOT, d)
        if os.path.isdir(dp) and not os.path.islink(dp) and not os.listdir(dp):
            os.rmdir(dp)
    bad = [S(os.path.join(DOT, it['目标'])) for it in man['项'] if state(os.path.join(DOT, it['目标'])) != it['原来']]
    bad += [R(os.path.join(REPO, it['目标'])) for it in man['仓库文件'] if state(os.path.join(REPO, it['目标'])) != it['原来']]
    for b in bad:
        print('核对不过：' + b + ' 没回到装上前')
    if saved:
        print(f'这 {len(saved)} 处在装上之后又被改过，删前另存在 {save}：' + '、'.join(saved))
    if bad:
        sys.exit(1)
    print(f'已撤回：~/.claude/ {len(man["项"])} 项、_底座/ {len(man["仓库文件"])} 个文件都回到装上前（逐项核过 sha）；'
          f'备份夹留着：{bk}。settings.json 若照打印的命令改过，用它自己的备份（~/.claude/backups/settings_规则搬家_*.json）恢复')


if UNDO_ARG:
    undo()
    sys.exit(0)


# ---------- --自检（只读；临时文件放系统临时目录，跑完删）----------
def first_session_id():
    try:
        m = re.search(r'local_[0-9a-f-]{36}', read(os.path.join(BASE, '对话定位.md')).decode('utf-8'))
        return m.group(0) if m else ''
    except OSError:
        return ''


GATE_TASK_LINE = 'TASK_DIR = os.path.join(WORKSPACE, "_底座", "任务")'
GATE_EXCL = '"scratchpad", "/tmp/", "/private/var/", '


def run_gate(gate, stdin, env, cwd, task_dir, drop_tmp_excl):
    """在内存里把闸门的任务目录换成 task_dir（假任务文件放那里，不写仓库）；仓库在临时目录时再去掉临时目录排除。文件不改。"""
    code = ('import sys\np=sys.argv[1]\ns=open(p,encoding="utf-8").read()\n'
            f'k={GATE_TASK_LINE!r}\nassert k in s, "闸门任务目录的写法变了"\ns=s.replace(k, "TASK_DIR = " + repr(sys.argv[2]))\n'
            + (f'e={GATE_EXCL!r}\nassert e in s, "闸门排除清单的写法变了"\ns=s.replace(e,"")\n' if drop_tmp_excl else '')
            + 'exec(compile(s,p,"exec"),{"__name__":"__main__","__file__":p})')
    return subprocess.run(['/usr/bin/python3', '-I', '-c', code, gate, task_dir], input=stdin,
                          capture_output=True, text=True, env=env, cwd=cwd, timeout=60)


def selfcheck():
    res = []
    tmp = tempfile.mkdtemp(prefix='装上自检_')
    env = dict(os.environ, HOME=ROOT, DK_HOOK_STATE_DIR=os.path.join(tmp, '状态'),
               DK_HOOK_LOG=os.path.join(tmp, '钩子日志.txt'), DK_HOOK_COMPACT_LOG=os.path.join(tmp, '压缩记录.md'))
    sid = first_session_id()
    its = items()
    rep = load_repl() or {}
    try:
        # ① 全局规则和本对话定位每轮附上
        hook = os.path.join(DOT, 'hooks', 'correction_capture.py')
        try:
            first = next(l for l in read(SNAP).decode('utf-8').splitlines() if l.strip())
            r = subprocess.run(['/usr/bin/python3', '-I', hook], input=json.dumps(
                {'session_id': sid, 'prompt': '测试', 'hook_event_name': 'UserPromptSubmit', 'transcript_path': '', 'cwd': REPO},
                ensure_ascii=False), capture_output=True, text=True, env=env, cwd=tmp, timeout=60)
            ctx = json.loads(r.stdout)['hookSpecificOutput']['additionalContext'] if r.stdout.strip() else ''
            miss = [n for n, k in (('全局规则第一行', first), ('「本对话定位」一节', '【本对话定位'), ('本对话那一条', sid)) if not k or k not in ctx]
            res.append(('① 每轮附上全局规则和本对话定位', r.returncode == 0 and not miss,
                        f'退出码 {r.returncode}' + (f'，缺：{"、".join(miss)}' if miss else f'，附上 {len(ctx)} 字（会话 {sid}）')))
        except Exception as e:
            res.append(('① 每轮附上全局规则和本对话定位', False, f'{type(e).__name__}: {e}'))

        # ② 交付闸门：没登记的拦、登记后又改的拦、登记过且没再改的放行
        gate = os.path.join(DOT, 'hooks', 'delivery_gate.py')
        try:
            fake = next(p for p in (os.path.join(BASE, '项目总览.md'), os.path.join(BASE, '规则体系说明.md')) if os.path.isfile(p))
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
            drop = any(x in REPO for x in ('scratchpad', '/tmp/', '/private/var/'))
            fm = os.path.getmtime(fake)
            outs = []
            for case, want_block, task_mtime in (('没登记', True, None), ('登记后又改', True, fm - 100), ('登记过没再改', False, fm + 100)):
                td = os.path.join(tmp, '假任务_' + case)
                os.makedirs(td)
                if task_mtime is not None:
                    tf = os.path.join(td, '假任务.md')
                    with open(tf, 'w', encoding='utf-8') as f:
                        f.write(f'# 任务：自检用\n\n状态：待验收\n\n## 验收结论\n- 自检用的假结论：过\n\n## 交付\n- 成品：{fake}\n')
                    os.utime(tf, (task_mtime, task_mtime))
                r = run_gate(gate, stdin, env, tmp, td, drop)
                blocked = '"decision": "block"' in r.stdout
                outs.append((case, blocked == want_block, ('拦' if blocked else '放行') + (f'（{(r.stderr or "").strip()[:120]}）' if r.returncode else '')))
            res.append(('② 交付闸门能拦', all(ok for _c, ok, _n in outs),
                        '；'.join(f'{c}：{n}{"" if ok else "（不对）"}' for c, ok, n in outs)
                        + ('（仓库在临时目录，闸门按设计不看临时目录；本项在内存里去掉这条排除后跑）' if drop else '')))
        except Exception as e:
            res.append(('② 交付闸门能拦', False, f'{type(e).__name__}: {e}'))

        # ③ 技能、子代理都在，头部 name 读得出
        bad, n_s, n_a = [], 0, 0
        for rel, _src, is_dir in its:
            if not rel.startswith(('skills/', 'agents/')):
                continue
            p = os.path.join(DOT, rel)
            f = os.path.join(p, 'SKILL.md') if is_dir else p
            n_s += rel.startswith('skills/')
            n_a += rel.startswith('agents/')
            head = read(f).decode('utf-8').split('\n---', 1)[0] if os.path.isfile(f) and not os.path.islink(p) else ''
            if not re.search(r'^name:\s*\S', head, re.M):
                bad.append(f'{S(f)} 不在、是链接，或头部读不出 name')
        res.append(('③ 技能、子代理都在', not bad and n_s > 0 and n_a > 0,
                    f'技能 {n_s} 个、子代理 {n_a} 个' + (f'；{"；".join(bad)}' if bad else '，都在 ~/.claude/ 下，name 都读得出')))

        # ④ 内容一致：~/.claude/ 每项等于规则包里的（全局规则等于快照）
        bad = [S(os.path.join(DOT, rel)) for rel, src, is_dir in its if state(os.path.join(DOT, rel)) != src_state(src, is_dir)]
        res.append(('④ 内容一致', not bad, f'{len(its)} 项' + (f'，和规则包不一样：{"、".join(bad)}' if bad else '都和规则包（全局规则和快照）一样')))

        # ⑤ settings.json 里登记的钩子指向存在的文件
        st = settings_status()
        res.append(('⑤ settings.json 登记了钩子', bool(st) and all(ok for _e, _f, ok, _n in st),
                    '；'.join(f'{e}：{n}' for e, _f, _ok, n in st) or '钩子登记.json 里没有钩子'))

        # ⑥ 机检自测
        r = subprocess.run(['/usr/bin/python3', '-I', os.path.join(BASE, '工具', '机检.py'), '--自测'],
                           capture_output=True, text=True, env=env, cwd=tmp, timeout=120)
        last = (r.stdout.strip().splitlines() or [''])[-1]
        res.append(('⑥ 机检.py --自测', r.returncode == 0, f'退出码 {r.returncode}，末行「{last}」'))

        # ⑦ 规则预算
        r = subprocess.run(['/usr/bin/python3', '-I', os.path.join(BASE, '工具', '查规则预算.py')],
                           capture_output=True, text=True, env=env, cwd=tmp, timeout=60)
        last = (r.stdout.strip().splitlines() or [''])[-1]
        res.append(('⑦ 查规则预算.py', last == '预算：过', f'末行「{last}」' + ('' if last == '预算：过' else '：' + r.stdout.strip()[-300:])))

        # ⑧ 不绑用户名：~/.claude/ 规则项和路径替换表列的 _底座/ 文件里，没有 /Users/<名>、/home/<名> 这样的家目录路径
        files = []
        for rel, _src, is_dir in its:
            p = os.path.join(DOT, rel)
            if is_dir and os.path.isdir(p):
                files += [os.path.join(r_, n) for r_, _d, fs in os.walk(p) for n in fs if n not in SKIP_FILES]
            elif os.path.isfile(p):
                files.append(p)
        files += [os.path.join(REPO, t) for t in repl_targets(rep)]
        hits = []
        for p in files:
            try:
                s = read(p).decode('utf-8')
            except (OSError, UnicodeDecodeError):
                continue
            for ln, line in enumerate(s.splitlines(), 1):
                if HOME_HIT.search(line) or ROOT in line:
                    hits.append(f'{S(p)}:{ln}')
        res.append(('⑧ 不绑用户名', not hits, f'查了 {len(files)} 个文件，' + (f'还有家目录路径 {len(hits)} 处：' + '、'.join(hits[:10]) if hits else '家目录路径 0 处')))

        # ⑨ 不多加载：_底座/搬家/ 下没有会被自动加载的名字
        bad = [S(os.path.join(r_, n)) for r_, ds, fs in os.walk(HERE) for n in ds + fs if n in BAD_NAMES]
        res.append(('⑨ 不多加载', not bad, '_底座/搬家/ 下' + ('有：' + '、'.join(bad) if bad else '没有叫 .claude、.claude-plugin、CLAUDE.md、CLAUDE.local.md、AGENTS.md 的')))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for name, ok, note in res:
        print(f'{"过" if ok else "不过"}　{name}：{note}')
    if not res[4][1]:
        print('\n钩子没登记或登记的路径不对。请自己跑这条命令（先备份 settings.json，只合并 hooks 一段）：\n' + settings_cmd())
    n_bad = sum(not ok for _n, ok, _x in res)
    print('自检：九项全过' if not n_bad else f'自检：{n_bad} 项不过')
    return 0 if not n_bad else 1


if CHECK:
    sys.exit(selfcheck())


# ---------- 预演、--执行 ----------
problems, plan, repl_out, repl_lines, old_home = check_all()
print(f'仓库：{REPO}\n根：{ROOT}')
for rel, src, is_dir, act, now, _w in plan:
    was = '' if not now else f'（现在是{now["类型"]}）'
    print(f'{act}　~/.claude/{rel}{was}  ←  {R(src)}')
for l in repl_lines:
    print(l)
for e, f, ok, n in settings_status():
    print(f'settings.json {e}：{"过" if ok else "不过"}，{n}')
if problems:
    print(f'\n检查：有 {len(problems)} 处不过，--执行 会整个停下：')
    for p in problems:
        print('  不过：' + p)
    print('有问题，没改任何文件')
    sys.exit(3)
todo = [x for x in plan if x[3] != '跳过']
print(f'\n检查：全过。~/.claude/ 要拷 {len(todo)} 项（其中 {sum(x[3] != "拷" for x in todo)} 项先备份原来的），跳过 {len(plan) - len(todo)} 项；'
      f'_底座/ 要改 {len(repl_out)} 个文件。')
if not DO:
    print('这是预演，没改任何文件。要执行：bash "' + SCRIPT + '" --执行' + ROOT_FLAG)
    sys.exit(0)
if not todo and not repl_out:
    print('都已装好，没什么要做。可以跑 --自检。')
    sys.exit(0)

stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
bk = os.path.join(DOT, 'backups', f'规则搬家_装上_{stamp}')
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
       '项': [{'目标': rel, '来源': R(src), '动作': act, '原来': now, '装上后': want, '备份': B('.claude/' + rel)}
             for rel, src, is_dir, act, now, want in todo],
       '仓库文件': [{'目标': t, '原来': state(os.path.join(REPO, t)), '装上后': {'类型': '文件', 'sha': sha(b)},
                  '备份': '仓库/' + B(t)} for t, b in sorted(repl_out.items())]}


def save_record():
    with open(os.path.join(bk, RECORD), 'w', encoding='utf-8') as f:
        json.dump(man, f, ensure_ascii=False, indent=1)


# 1. 先把要换掉的原样拷进备份夹、核过，再写装上记录；之后才动 ~/.claude 和 _底座
for it, base in [(x, DOT) for x in man['项']] + [(x, REPO) for x in man['仓库文件']]:
    o = it['原来']
    if o:
        src, dst = os.path.join(base, it['目标']), os.path.join(bk, it['备份'])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if o['类型'] == '文件夹':
            shutil.copytree(src, dst, symlinks=True)
        elif o['类型'] == '链接':
            os.symlink(o['指向'], dst)
        else:
            shutil.copy2(src, dst)
        if state(dst) != o:
            die(f'备份核对不过：{it["备份"]}；还没改任何东西，备份夹 {bk} 可删', 3)
save_record()
print(f'备份好了：{bk}')

# 2. 拷进 ~/.claude/
for it in man['项']:
    p = os.path.join(DOT, it['目标'])
    src = os.path.join(REPO, it['来源'])
    mkdirs(os.path.dirname(p))
    if it['装上后']['类型'] == '文件夹':
        stage = os.path.join(bk, '_新', B('.claude/' + it['目标']))
        os.makedirs(os.path.dirname(stage), exist_ok=True)
        shutil.copytree(src, stage, ignore=shutil.ignore_patterns(*SKIP_FILES))
        if os.path.lexists(p):
            gone = os.path.join(bk, '_换下的', it['备份'])
            os.makedirs(os.path.dirname(gone), exist_ok=True)
            os.rename(p, gone)
        os.rename(stage, p)
    else:
        tmp = p + '.装上tmp'
        if os.path.lexists(tmp):
            os.remove(tmp)
        shutil.copyfile(src, tmp)
        os.replace(tmp, p)

# 3. 改 _底座/
for it in man['仓库文件']:
    p = os.path.join(REPO, it['目标'])
    tmp = p + '.装上tmp'
    with open(tmp, 'wb') as f:
        f.write(repl_out[it['目标']])
    shutil.copymode(p, tmp)
    os.replace(tmp, p)
shutil.rmtree(os.path.join(bk, '_新'), ignore_errors=True)
save_record()

# 4. 核
bad = [S(os.path.join(DOT, it['目标'])) for it in man['项'] if state(os.path.join(DOT, it['目标'])) != it['装上后']]
bad += [R(os.path.join(REPO, it['目标'])) for it in man['仓库文件'] if state(os.path.join(REPO, it['目标'])) != it['装上后']]
print('\n撤回命令：\n  bash "' + SCRIPT + f'" --撤回 "{bk}"' + ROOT_FLAG)
if man['仓库文件']:
    print(f'\n_底座/ 改了这 {len(man["仓库文件"])} 个文件（下次提交时一起提交）：' + '、'.join(it['目标'] for it in man['仓库文件']))
if not all(ok for _e, _f, ok, _n in settings_status()):
    print('\n钩子没登记或登记的路径不对。请自己跑这条命令（先备份 settings.json，只合并 hooks 一段）：\n' + settings_cmd())
if bad:
    print('核对不过：' + '、'.join(bad) + '\n按上面的撤回命令撤回')
    sys.exit(1)
print(f'\n已装上：~/.claude/ 拷了 {len(man["项"])} 项（{sum(1 for it in man["项"] if it["原来"])} 项原来的已进备份），'
      f'_底座/ 改了 {len(man["仓库文件"])} 个文件，逐项核过。\n下一步：bash "' + SCRIPT + '" --自检' + ROOT_FLAG)
PY
