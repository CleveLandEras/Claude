#!/bin/bash
# 导出：把本机 ~/.claude/ 下现行的规则收进仓库 _底座/搬家/规则包/，路径改成通用写法。本机 ~/.claude/ 一个字节不动。
# 任务 ~/claude/_底座/任务/用好Claude/2026-11-03_规则搬家包.md；做法照思考页 7.2「M1'」。长期用：换环境前、推送前都跑。
#
# 收哪些（按现有的全收，加了技能重跑就会收进来）：
#   ~/.claude/skills/<名>/       → 规则包/skills/<名>/     （synced/、.trash/ 除外；.DS_Store 不收）
#   ~/.claude/agents/<名>.md     → 规则包/agents/<名>.md
#   ~/.claude/hooks/<名>.py      → 规则包/hooks/<名>.py
#   ~/.claude/settings.json 的 hooks 一段 → 规则包/钩子登记.json（只存 {"hooks": …}；model、theme 这些不存）
#   全局规则不另拷：规则包用 _底座/全局规则_快照.md；~/.claude/CLAUDE.md 只拿来和快照比。
#   另写 规则包/清单.json：每项的来源（写成 ~/…）、来源 sha、规则包里的 sha、改了几处路径；导出时间、快照 sha。
#   不记主机名、不记用户名。文件夹的 sha＝把「相对路径\0文件 sha256\n」按路径排序拼起来再算 sha256（不含 .DS_Store）。
#
# 路径写法（只改规则包里的拷贝；<家>＝跑脚本的人的家目录）：
#   文本文件：<家>/ → ~/
#   .py：字符串 "<家>/<路径>" → os.path.expanduser("~/<路径>")；改了却没 import os 就停下报
#   钩子登记：<家>/.claude/hooks/<名>.py → "$HOME/.claude/hooks/<名>.py"
#
# 检查（任一不过就一个文件都不写，只报原因）：
#   ① 改完以后规则包里本机家目录的绝对路径（运行时 os.path.expanduser('~') 算出）是 0，不按字面 /Users/ 判
#   （delivery_gate.py 里匹配路径的正则含 /Users/，不含用户名，原样保留）；② 来源里没有叫 .claude、.claude-plugin 的文件夹，没有叫 CLAUDE.md、CLAUDE.local.md、
#   AGENTS.md 的文件，也没有链接；③ ~/.claude/CLAUDE.md 和 _底座/全局规则_快照.md 逐字节相同（不同就先照整理纠正同步快照，
#   本脚本不改快照）；④ 开头和结尾各算一次来源各项的 sha，两次相同，~/.claude/settings.json 的 sha 不变。
#
# 用法：
#   bash 导出.sh [--根 <目录>]          预演：打印每项要写什么、改了几处路径，不写任何文件
#   bash 导出.sh --执行 [--根 <目录>]   检查全过才写：先写 规则包.新/，核过后旧的改名 规则包.旧/、新的换上，再删 规则包.旧/
#   bash 导出.sh --对比 [--根 <目录>]   只读：规则包和「现在导出会得到的」逐项比，一致退出码 0，不一致退出码 1；
#                                       顺带报快照是否一致、_底座/搬家/路径替换.json「逐条」每条原句是否恰好出现一次、「通用」的文件在不在
#                                       （没有这个文件就跳过；格式 {"逐条": [{"目标": 相对仓库根的路径, "原句": 含 {旧家}, "新句": …}],
#                                       "通用": {"目标": [相对仓库根的路径…]}}，{旧家} 在本机按本机家目录算）
#   --根 <目录>：只供测试，把 ~ 换成 <目录>，仓库取 <目录>/claude
# 退出码：0 过；1 --对比不一致；2 用法错；3 检查不过（一个文件都没写）
exec /usr/bin/python3 -I - "$@" <<'PY'
import datetime, hashlib, json, os, re, shutil, sys

ARGS = sys.argv[1:]
SKIP_SKILLS = ('synced', '.trash')
SKIP_FILES = ('.DS_Store',)
BAD_NAMES = ('.claude', '.claude-plugin', 'CLAUDE.md', 'CLAUDE.local.md', 'AGENTS.md')


def die(msg, code=2):
    print(msg)
    sys.exit(code)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(p):
    with open(p, 'rb') as f:
        return f.read()


def flag_value(name):
    if name not in ARGS:
        return None
    i = ARGS.index(name)
    if i + 1 >= len(ARGS) or ARGS[i + 1].startswith('--'):
        die(f'{name} 后面要跟一个目录')
    return ARGS[i + 1]


ROOT_ARG = flag_value('--根')
rest = list(ARGS)
if ROOT_ARG is not None:
    i = rest.index('--根')
    del rest[i:i + 2]
for a in rest:
    if a not in ('--执行', '--对比'):
        die(f'不认识的参数：{a}')
DO, CMP = '--执行' in rest, '--对比' in rest
if DO and CMP:
    die('--执行、--对比 只能用一个')

ROOT = os.path.realpath(os.path.expanduser(ROOT_ARG or '~'))
HOME_STR = os.path.expanduser('~').rstrip('/')   # 文件里写死的家目录（不进清单）
DOT = os.path.join(ROOT, '.claude')
REPO = os.path.join(ROOT, 'claude')
BASE = os.path.join(REPO, '_底座')
OUTDIR = os.path.join(BASE, '搬家')
PACK = os.path.join(OUTDIR, '规则包')
NEW, OLD = PACK + '.新', PACK + '.旧'
SNAP = os.path.join(BASE, '全局规则_快照.md')
GLOBAL = os.path.join(DOT, 'CLAUDE.md')
SETTINGS = os.path.join(DOT, 'settings.json')
REPL = os.path.join(OUTDIR, '路径替换.json')
for p in (DOT, BASE):
    if not os.path.isdir(p):
        die(f'找不到 {p}')


def tilde(p):
    return '~/' + os.path.relpath(p, ROOT)


def mtime(paths):
    ts = [os.path.getmtime(p) for p in paths if os.path.exists(p)]
    return datetime.datetime.fromtimestamp(max(ts)).strftime('%m/%d %H:%M') if ts else '—'


def files_sha(rows):  # rows: {相对路径: sha}
    return sha(''.join(f'{k}\0{rows[k]}\n' for k in sorted(rows)).encode())


# ---------- 来源快照（检查 ④：开头和结尾各算一次） ----------
def source_fingerprint():
    rows = {}
    for sub in ('skills', 'agents', 'hooks'):
        d = os.path.join(DOT, sub)
        for r, ds, fs in os.walk(d):
            ds.sort()
            for n in sorted(ds + fs):
                q = os.path.join(r, n)
                rel = os.path.relpath(q, DOT)
                if os.path.islink(q):
                    rows[rel] = 'L:' + os.readlink(q)
                elif os.path.isfile(q):
                    rows[rel] = sha(read(q))
    for p in (SETTINGS, GLOBAL):
        rows[os.path.relpath(p, DOT)] = sha(read(p)) if os.path.isfile(p) else '无'
    return files_sha(rows), (sha(read(SETTINGS)) if os.path.isfile(SETTINGS) else '无')


# ---------- 收来源 ----------
problems, notes = [], []


def collect():
    """返回 [{名, 种类, 来源, files: {规则包内相对路径: 来源绝对路径}}]"""
    items = []
    sk = os.path.join(DOT, 'skills')
    if os.path.isdir(sk):
        for n in sorted(os.listdir(sk)):
            p = os.path.join(sk, n)
            if n in SKIP_SKILLS or n in SKIP_FILES:
                continue
            if os.path.islink(p):
                problems.append(f'② {tilde(p)} 是链接，导出不收链接')
                continue
            if not os.path.isdir(p):
                notes.append(f'{tilde(p)} 不是文件夹，没收')
                continue
            if n in BAD_NAMES:
                problems.append(f'② 来源里有叫 {n} 的文件夹：{tilde(p)}')
            files = {}
            for r, ds, fs in os.walk(p):
                ds.sort()
                for dn in ds:
                    q = os.path.join(r, dn)
                    if dn in BAD_NAMES:
                        problems.append(f'② 来源里有叫 {dn} 的文件夹：{tilde(q)}')
                    if os.path.islink(q):
                        problems.append(f'② {tilde(q)} 是链接，导出不收链接')
                for fn in sorted(fs):
                    q = os.path.join(r, fn)
                    if fn in SKIP_FILES:
                        continue
                    if fn in BAD_NAMES:
                        problems.append(f'② 来源里有叫 {fn} 的文件：{tilde(q)}')
                    if os.path.islink(q):
                        problems.append(f'② {tilde(q)} 是链接，导出不收链接')
                        continue
                    files['skills/' + os.path.relpath(q, sk)] = q
            if not os.path.isfile(os.path.join(p, 'SKILL.md')):
                notes.append(f'{tilde(p)} 里没有 SKILL.md（照收）')
            items.append({'名': f'skills/{n}', '种类': '技能', '来源': tilde(p), 'files': files})
    for sub, ext, kind in (('agents', '.md', '子代理'), ('hooks', '.py', '钩子')):
        d = os.path.join(DOT, sub)
        if not os.path.isdir(d):
            continue
        for n in sorted(os.listdir(d)):
            p = os.path.join(d, n)
            if n in SKIP_FILES:
                continue
            if os.path.isdir(p) and not os.path.islink(p):
                notes.append(f'{tilde(p)} 是文件夹，没收（只收 {sub}/*{ext}）')
                continue
            if not n.endswith(ext):
                continue
            if n in BAD_NAMES:
                problems.append(f'② 来源里有叫 {n} 的文件：{tilde(p)}')
            if os.path.islink(p):
                problems.append(f'② {tilde(p)} 是链接，导出不收链接')
                continue
            items.append({'名': f'{sub}/{n}', '种类': kind, '来源': tilde(p), 'files': {f'{sub}/{n}': p}})
    return items


# ---------- 改路径写法 ----------
PY_STR = re.compile(r'(?<![A-Za-z0-9_])(["\'])' + re.escape(HOME_STR) + r'/([^"\'\n]*)\1')
HOOK_CMD = re.compile(re.escape(HOME_STR) + r'/(\.claude/hooks/[^\s"\']+)')


def has_import_os(s):
    for m in re.finditer(r'^[ \t]*import[ \t]+([^\n#]+)', s, re.M):
        for part in m.group(1).split(','):
            w = part.strip().split()
            if w and (w[0] == 'os' or w[0].startswith('os.')) and len(w) == 1:
                return True
    return False


def convert(rel, b):
    """返回 (新字节, 改了几处)"""
    try:
        s = b.decode('utf-8')
    except UnicodeDecodeError:
        return b, 0
    if rel.endswith('.py'):
        s2, n = PY_STR.subn(lambda m: f'os.path.expanduser({m.group(1)}~/{m.group(2)}{m.group(1)})', s)
        if n and not has_import_os(s2):
            problems.append(f'{rel} 改了 {n} 处，但文件里没有 import os')
        return s2.encode('utf-8'), n
    n = s.count(HOME_STR + '/')
    return s.replace(HOME_STR + '/', '~/').encode('utf-8'), n


def convert_hooks(h):
    cnt = [0]

    def walk(x):
        if isinstance(x, dict):
            out = {}
            for k, v in x.items():
                if k == 'command' and isinstance(v, str):
                    v, n = HOOK_CMD.subn(r'"$HOME/\1"', v)
                    cnt[0] += n
                    out[k] = v
                else:
                    out[k] = walk(v)
            return out
        if isinstance(x, list):
            return [walk(v) for v in x]
        return x
    return walk(h), cnt[0]


def build():
    """在内存里算出规则包：返回 (expected {相对路径: 字节}, manifest, item_index)"""
    items = collect()
    expected, manifest_items, index = {}, [], {}
    for it in items:
        src_rows, out_rows, file_rows, total = {}, {}, [], 0
        for rel, src in sorted(it['files'].items()):
            b = read(src)
            nb, n = convert(rel, b)
            expected[rel] = nb
            inner = os.path.relpath(rel, it['名']) if it['种类'] == '技能' else os.path.basename(rel)
            src_rows[inner], out_rows[inner] = sha(b), sha(nb)
            file_rows.append({'路径': rel, '来源sha': sha(b), '规则包sha': sha(nb), '改了几处路径': n})
            total += n
        e = {'名': it['名'], '种类': it['种类'], '来源': it['来源'],
             '来源sha': files_sha(src_rows) if it['种类'] == '技能' else file_rows[0]['来源sha'],
             '规则包sha': files_sha(out_rows) if it['种类'] == '技能' else file_rows[0]['规则包sha'],
             '改了几处路径': total}
        if it['种类'] == '技能':
            e['文件'] = file_rows
        manifest_items.append(e)
        index[it['名']] = {'files': set(it['files']), 'srcs': list(it['files'].values())}
    # 钩子登记
    if os.path.isfile(SETTINGS):
        try:
            st = json.loads(read(SETTINGS).decode('utf-8'))
        except Exception as ex:
            problems.append(f'读不了 {tilde(SETTINGS)}：{ex}')
            st = {}
        h = st.get('hooks')
        if h is not None:
            nh, n = convert_hooks(h)
            nb = (json.dumps({'hooks': nh}, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
            expected['钩子登记.json'] = nb
            manifest_items.append({'名': '钩子登记.json', '种类': '钩子登记', '来源': tilde(SETTINGS) + ' 的 hooks 一段',
                                   '来源sha': sha(json.dumps(h, ensure_ascii=False, sort_keys=True).encode('utf-8')),
                                   '规则包sha': sha(nb), '改了几处路径': n})
            index['钩子登记.json'] = {'files': {'钩子登记.json'}, 'srcs': [SETTINGS]}
        else:
            notes.append(f'{tilde(SETTINGS)} 里没有 hooks 一段，钩子登记.json 不写')
    snap = read(SNAP) if os.path.isfile(SNAP) else None
    manifest = {
        '说明': '导出.sh 生成，别手改；原件在本机 ~/.claude/。全局规则不在规则包里，用 _底座/全局规则_快照.md。',
        '导出时间': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '全局规则': {'来源': '~/.claude/CLAUDE.md', '规则包里用': '~/claude/_底座/全局规则_快照.md',
                     '快照sha': sha(snap) if snap is not None else '无'},
        '项': manifest_items,
    }
    return expected, manifest, index


def manifest_bytes(m):
    return (json.dumps(m, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def checks(expected, manifest, fp_start):
    fails = list(problems)
    # ① 判的是导出这台电脑的家目录绝对路径（第二级 11/03 17:07 补定，不按字面 /Users/ 判）
    hits = []
    needle = HOME_STR.encode('utf-8')
    allb = dict(expected)
    allb['清单.json'] = manifest_bytes(manifest)
    for rel, b in sorted(allb.items()):
        if needle in b:
            for ln, line in enumerate(b.split(b'\n'), 1):
                if needle in line:
                    hits.append(f'{rel}:{ln}')
    if hits:
        fails.append(f'① 改完以后规则包里还有本机家目录的绝对路径 {len(hits)} 处：' + '、'.join(hits))
    # ③
    if not os.path.isfile(GLOBAL) or not os.path.isfile(SNAP):
        fails.append(f'③ 找不到 {tilde(GLOBAL)} 或 {tilde(SNAP)}')
    elif read(GLOBAL) != read(SNAP):
        fails.append(f'③ {tilde(GLOBAL)} 和 {tilde(SNAP)} 不一致：先照整理纠正同步快照（本脚本不改快照）')
    # ④
    fp_end = source_fingerprint()
    if fp_end[0] != fp_start[0]:
        fails.append('④ 导出期间本机来源有改动（开头和结尾的 sha 不同），重跑一次')
    if fp_end[1] != fp_start[1]:
        fails.append(f'④ 导出期间 {tilde(SETTINGS)} 变了')
    return fails


def pack_files(d):
    out = {}
    for r, ds, fs in os.walk(d):
        for n in fs:
            q = os.path.join(r, n)
            out[os.path.relpath(q, d)] = read(q)
    return out


def item_of(rel):
    parts = rel.split('/')
    if parts[0] == 'skills' and len(parts) >= 3:
        return 'skills/' + parts[1]
    return rel


# ---------- 主流程 ----------
fp_start = source_fingerprint()
expected, manifest, index = build()
n_items, n_paths = len(manifest['项']), sum(e['改了几处路径'] for e in manifest['项'])

if CMP:
    bad = []
    have = pack_files(PACK) if os.path.isdir(PACK) else None
    if have is None:
        bad.append(f'还没有规则包：{tilde(PACK)}')
    else:
        old_manifest = have.pop('清单.json', None)
        exp_items = {item_of(r) for r in expected}
        have_items = {item_of(r) for r in have}
        for it in sorted(exp_items - have_items):
            bad.append(f'本机新增：{it}（来源修改时间 {mtime(index[it]["srcs"])}）')
        for it in sorted(have_items - exp_items):
            bad.append(f'本机删了：{it}')
        for it in sorted(exp_items & have_items):
            ef = {r for r in expected if item_of(r) == it}
            hf = {r for r in have if item_of(r) == it}
            diff = sorted(r for r in ef | hf if expected.get(r) != have.get(r))
            if diff:
                bad.append(f'内容变了：{it}（来源修改时间 {mtime(index[it]["srcs"])}；{len(diff)} 个文件）')
        if old_manifest is None:
            bad.append('规则包里没有 清单.json')
        elif not bad:  # 逐项已经报了差异时，清单跟着不同，不另报

            try:
                om = json.loads(old_manifest.decode('utf-8'))
                if om.get('项') != manifest['项'] or om.get('全局规则') != manifest['全局规则']:
                    bad.append('清单.json 和本机现在算出的对不上（来源 sha 或快照 sha 变了）')
            except Exception as ex:
                bad.append(f'清单.json 读不了：{ex}')
    fails = checks(expected, manifest, fp_start)
    for f in fails:
        bad.append('检查不过：' + f)
    print('快照：' + ('和 ~/.claude/CLAUDE.md 一致' if not any(f.startswith('③') for f in fails) else '和 ~/.claude/CLAUDE.md 不一致'))
    if os.path.isfile(REPL):
        try:
            rep = json.loads(read(REPL).decode('utf-8'))
            each = rep.get('逐条', []) if isinstance(rep, dict) else rep
            gen = rep.get('通用', {}).get('目标', []) if isinstance(rep, dict) else []
            off = []
            for k, e in enumerate(each, 1):  # 原句里的 {旧家} 在本机（旧环境）就是本机家目录
                t = os.path.join(REPO, e['目标'])
                c = read(t).decode('utf-8').count(e['原句'].replace('{旧家}', HOME_STR)) if os.path.isfile(t) else -1
                if c != 1:
                    off.append(f'逐条第 {k} 条（{e["目标"]}）' + ('找不到文件' if c < 0 else f'出现 {c} 次'))
            for t in gen:
                if not os.path.isfile(os.path.join(REPO, t)):
                    off.append(f'通用（{t}）找不到文件')
            if off:
                bad.append('路径替换.json 对不上：' + '；'.join(off) + '。要在旧环境重新生成')
            print(f'路径替换.json：逐条 {len(each)} 条、通用 {len(gen)} 个文件，'
                  + ('逐条原句都恰好出现 1 次，通用的文件都在' if not off else f'{len(off)} 处对不上'))
        except Exception as ex:
            bad.append(f'路径替换.json 读不了：{ex}')
    else:
        print('路径替换.json：还没有，跳过')
    for n in notes:
        print('提醒：' + n)
    if bad:
        for b in bad:
            print('  ' + b)
        print(f'不一致：{len(bad)} 处（规则包 {tilde(PACK)}）')
        sys.exit(1)
    print(f'规则包和本机一致（{n_items} 项）')
    sys.exit(0)

# 预演、执行：先打印每项
print(f'来源：{tilde(DOT)}；写到：{tilde(PACK)}')
for e in manifest['项']:
    k = len(e.get('文件', [None]))
    print(f'  {e["名"]}：{k} 个文件，改了 {e["改了几处路径"]} 处路径')
print(f'  清单.json：{n_items} 项')
for n in notes:
    print('提醒：' + n)
fails = checks(expected, manifest, fp_start)
if fails:
    print('检查不过，一个文件都没写：')
    for f in fails:
        print('  ' + f)
    print(f'检查不过（{len(fails)} 条），没写任何文件')
    sys.exit(3)
if not DO:
    print(f'预演：{n_items} 项，改了 {n_paths} 处路径；检查全过，没写任何文件（加 --执行 才写）')
    sys.exit(0)

for p in (NEW, OLD):
    if os.path.exists(p):
        die(f'上次导出没跑完，留下了 {tilde(p)}；先看一眼再删，然后重跑', 3)
allb = dict(expected)
allb['清单.json'] = manifest_bytes(manifest)
try:
    for rel, b in allb.items():
        q = os.path.join(NEW, rel)
        os.makedirs(os.path.dirname(q), exist_ok=True)
        with open(q, 'wb') as f:
            f.write(b)
    if pack_files(NEW) != allb:
        raise RuntimeError('写出的 规则包.新/ 和算出的不一致')
    fp_end = source_fingerprint()
    if fp_end != fp_start:
        raise RuntimeError('④ 写的时候本机来源有改动')
except Exception as ex:
    shutil.rmtree(NEW, ignore_errors=True)
    print(f'没写成，已删掉 规则包.新/：{ex}')
    sys.exit(3)
if os.path.exists(PACK):
    os.rename(PACK, OLD)
os.rename(NEW, PACK)
shutil.rmtree(OLD, ignore_errors=True)
if pack_files(PACK) != allb:
    print('换上以后核对不一致，请看规则包')
    sys.exit(3)
print(f'已写：{tilde(PACK)}，{n_items} 项，改了 {n_paths} 处路径')
PY
