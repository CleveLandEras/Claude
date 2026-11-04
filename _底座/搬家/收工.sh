#!/bin/bash
# 收工：换环境前把要留的全部算成一个「快进提交 M」，打印提交号和推送命令。不推送、不动 main、不碰真索引、不写 ~/.claude/。
# 任务 ~/claude/_底座/任务/用好Claude/2026-11-04_今天全部进GitHub.md；做法照同名文件夹 思考页.md 第 7 节和页末「第二级审过」。
#
# 用法：
#   bash 收工.sh --批 1        第一批：除 抖音号/videos/ 大文件外的全部。
#   bash 收工.sh --批 视频     只在第一批的 L 上加 抖音号/videos/（父是第一批的 L）。
#   bash 收工.sh --批 补带     全量重算，接在视频批之后（11/04 弹窗放开 .gitignore 后多带的那批）。
#   bash 收工.sh --批 收工     全量重算（Dk 说「收工」后用）；上一批做过「视频」就含 videos/。
#   --基 <ref>      合并目标（M 的第一父）。默认：--批 1 用 origin/main（旧仓库的，本地有）；--批 视频 用 refs/banjia/M1；
#                   --批 收工 用 refs/banjia/M视频（没有就 M1）。这样第二次推送对新仓库是快进。
#                   形如 <远端>/<分支> 且远端存在时先 git fetch，失败只警告，用本地已有的 ref 并打印提交号。
#   推送目标是新的空仓库，按地址推（不配 remote）；包体估算：--批 1 按 M 的全部对象（整段历史），其余批按上一个 M 到新 M 的增量。
#   --到 <阶段>     只供调试：复制｜快照｜合并 之后停（不写引用、不克隆）。
#   重跑：每步都能重来；复制是 rsync 同步，分片已有且核对一致就跳过。同输入得同一棵树（提交号随时间戳变，以最后打印的为准）。
#
# 步骤：①导出对比 → ②复制（抖音号、消息助手、记忆、定时任务、共享笔记）→ ③录屏分片 → ④临时索引快照 + 密钥扫描
#       → ⑤L 提交 → ⑥合并 M（-X ours，M 的第一父是 基，所以推送是快进）→ ⑦程序检查（含克隆到临时目录真装一遍）→ ⑧打印。
# 失败：①–④ 只多了复制出来的目录和无引用的对象；⑤⑥ 只多了无引用的对象；引用 refs/banjia/* 在 ⑦ 全过后才写。
# 退出码：0 全过；2 用法错；3 某一步不过（停在那一步，不绕过）。
D="$(cd "$(dirname "$0")" && pwd -P)"
exec /usr/bin/python3 -I - "$D" "$@" <<'PY'
import datetime, fnmatch, hashlib, json, os, re, shutil, subprocess, sys, tempfile, threading, time

HERE, ARGS = sys.argv[1], sys.argv[2:]
REPO = os.path.realpath(os.path.join(HERE, '..', '..'))
HOME = os.path.expanduser('~').rstrip('/')
DY = os.path.join(HOME, 'Documents', 'dy')
MSG_HELPER = os.path.join(HOME, 'Documents', '消息助手')
CLAUDE_DIR = os.path.join(HOME, '.claude')
NOTES_DIR = os.path.join(HOME, 'Library', 'Application Support', 'Claude', 'side-session-notes')
EXCL_FILE = os.path.join(HERE, '收工_排除清单.txt')
T0 = time.time()

ENV = dict(os.environ)
for k in ('GIT_INDEX_FILE', 'GIT_DIR', 'GIT_WORK_TREE'):
    ENV.pop(k, None)
ENV.update(GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0', LC_ALL='en_US.UTF-8')

# 放进库的根（explicit 路径；根 .gitignore 是同一份白名单）
ROOT_DIRS = ['弹窗标签推送系统', '_底座', '商城', '用好Claude', '团队工作模式', '抖音总结',
             '企业微信自动回复', '竞品跟踪分析', '抖音号', '消息助手']
ROOT_FILES = ['.gitignore', 'README.md', 'CLAUDE.md', 'image.png', '图像.png', '会员价值数据分析报告_v2.md', '方案_目录.html']
ROOT_GLOBS = ['Screenshot_2026-09-03-*.jpg', '新手通行證_*']
MAX_FILE = 99_000_000           # GitHub 单文件上限 100M
WARN_FILE = 50 * 1024 * 1024    # GitHub 的 50 MiB 警告线
SPLIT = 49 * 1024 * 1024        # 49 MiB 一片，避开 50M 警告


class Stop(Exception):
    pass


def P(*a):
    print(f'[{time.time() - T0:6.1f}s]', *a, flush=True)


def die(msg, code=2):
    print(msg, flush=True)
    sys.exit(code)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while True:
            b = f.read(1 << 22)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def run(cmd, env=None, inp=None, check=True, cwd=REPO, timeout=None):
    r = subprocess.run(cmd, cwd=cwd, env=env or ENV, input=inp, capture_output=True, timeout=timeout)
    if check and r.returncode != 0:
        raise Stop(f'命令失败 rc={r.returncode}：{" ".join(str(c) for c in cmd[:6])} … {r.stderr.decode("utf-8", "replace")[-300:]}')
    return r


def git(*args, idx=None, inp=None, check=True, cfg=(), timeout=None):
    env = dict(ENV)
    if idx:
        env['GIT_INDEX_FILE'] = idx
    cmd = ['git']
    for c in cfg:
        cmd += ['-c', c]
    cmd += list(args)
    return run(cmd, env=env, inp=inp, check=check, timeout=timeout)


def gs(*args, **kw):
    return git(*args, **kw).stdout.decode('utf-8', 'replace').strip()


def rev(x):
    r = git('rev-parse', '--verify', '-q', x, check=False)
    return r.stdout.decode().strip() if r.returncode == 0 else None


# ---------- 参数 ----------
BATCH = BASE_REF = UPTO = None
i = 0
while i < len(ARGS):
    a = ARGS[i]
    if a in ('--批', '--基', '--到') and i + 1 < len(ARGS):
        v = ARGS[i + 1]
        if a == '--批':
            BATCH = v
        elif a == '--基':
            BASE_REF = v
        else:
            UPTO = v
        i += 2
    else:
        die(f'不认识的参数：{a}\n用法：bash 收工.sh --批 <1|视频|补带|收工> [--基 <ref>] [--到 复制|快照|合并]')
if BATCH not in ('1', '视频', '补带', '收工'):
    die('用法：bash 收工.sh --批 <1|视频|补带|收工> [--基 <ref>]')
if UPTO not in (None, '复制', '快照', '合并'):
    die('--到 只能是 复制｜快照｜合并')
RUN_DIR = tempfile.mkdtemp(prefix='收工_')
REFB = 'refs/banjia'
LOG = []


def note(s):
    LOG.append(s)
    P(s)


# ---------- 前后状态（完成标准 4）----------
def claude_fingerprint():
    """~/.claude/ 里规则相关项（CLAUDE.md、settings*.json、skills、agents、hooks、commands、scheduled-tasks）的内容指纹，不含对话记录。"""
    ent = []
    for n in ('CLAUDE.md', 'settings.json', 'settings.local.json'):
        p = os.path.join(CLAUDE_DIR, n)
        if os.path.isfile(p):
            ent.append((n, sha_file(p)))
    for d in ('skills', 'agents', 'hooks', 'commands', 'scheduled-tasks'):
        for dp, dn, fn in os.walk(os.path.join(CLAUDE_DIR, d)):
            dn.sort()
            for f in sorted(fn):
                p = os.path.join(dp, f)
                if os.path.isfile(p):
                    ent.append((os.path.relpath(p, CLAUDE_DIR), sha_file(p)))
    ent.sort()
    return sha_bytes(''.join(f'{a}\0{b}\n' for a, b in ent).encode()), len(ent)


def state():
    ix = os.path.join(REPO, '.git', 'index')
    return {'HEAD': rev('HEAD'), 'main': rev('refs/heads/main'),
            'index': sha_file(ix) if os.path.isfile(ix) else None,
            'claude': claude_fingerprint()}


# ---------- ② 复制 ----------
def rsync(src, dst, extra, delete=True):
    os.makedirs(dst, exist_ok=True)
    cmd = ['rsync', '-rtp'] + (['--delete', '--delete-excluded'] if delete else []) + extra + [src.rstrip('/') + '/', dst.rstrip('/') + '/']
    r = run(cmd, check=False)
    if r.returncode not in (0, 23, 24):
        raise Stop(f'rsync 失败 rc={r.returncode}：{src} → {dst}：{r.stderr.decode("utf-8", "replace")[-300:]}')
    if r.returncode != 0:
        note(f'  警告：rsync rc={r.returncode}（部分文件没复制或中途消失）：{src}')


def count_files(d, skip_names=('.DS_Store',)):
    n = s = 0
    for dp, dn, fn in os.walk(d):
        for f in fn:
            if f in skip_names:
                continue
            p = os.path.join(dp, f)
            if os.path.isfile(p) and not os.path.islink(p):
                n += 1
                s += os.path.getsize(p)
    return n, s


def make_dy_filter(videos):
    lst = os.path.join(DY, '换环境_带走清单.rsync')
    if not os.path.isfile(lst):
        raise Stop(f'缺 {lst}')
    lines = open(lst, encoding='utf-8').read().splitlines()
    out, ins = [], False
    extra = ['+ /studio/***'] + (['+ /videos/***'] if videos else [])
    for ln in lines:
        if not ins and ln.startswith('+ '):
            out += extra
            ins = True
        out.append(ln)
    if not ins:
        out += extra
    # 保证 node_modules / .venv / tools/node 一定在前面被排除
    out = ['- .DS_Store', '- /.venv/', '- /tools/node/', '- node_modules/'] + out
    p = os.path.join(RUN_DIR, f'dy_filter_{"videos" if videos else "base"}.rsync')
    open(p, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    return p


def copy_dy(with_videos):
    P('② 复制 抖音号')
    f = make_dy_filter(with_videos)
    rsync(DY, os.path.join(REPO, '抖音号'), [f'--filter=merge {f}'])
    n, s = count_files(os.path.join(REPO, '抖音号'))
    note(f'  抖音号/：{n} 个文件，{s / 1e6:.1f} MB（{"含" if with_videos else "不含"} videos/ 大文件）')


def stage_copy(with_videos):
    P('② 复制')
    copy_dy(with_videos)
    # 消息助手
    rsync(MSG_HELPER, os.path.join(REPO, '消息助手'),
          ['--exclude=.DS_Store', '--exclude=.gradle/', '--exclude=.kotlin/', '--exclude=build/', '--exclude=local.properties', '--exclude=*.lock'])
    n, s = count_files(os.path.join(REPO, '消息助手'))
    note(f'  消息助手/：{n} 个文件，{s / 1e6:.1f} MB')
    # 记忆
    mem_dst = os.path.join(REPO, '_底座', '搬家', '记忆')
    total_src = total_dst = 0
    folders = 0
    for d in sorted(os.listdir(os.path.join(CLAUDE_DIR, 'projects'))):
        src = os.path.join(CLAUDE_DIR, 'projects', d, 'memory')
        if not os.path.isdir(src):
            continue
        n, _ = count_files(src, skip_names=())
        if n == 0:
            continue
        rsync(src, os.path.join(mem_dst, d), [])
        total_src += n
        total_dst += count_files(os.path.join(mem_dst, d), skip_names=())[0]
        folders += 1
    note(f'  记忆：{folders} 个文件夹，来源 {total_src} 个文件，复制后 {total_dst} 个 → _底座/搬家/记忆/')
    if total_src != total_dst:
        raise Stop(f'记忆文件数对不上：来源 {total_src}，复制后 {total_dst}')
    # 定时任务
    rsync(os.path.join(CLAUDE_DIR, 'scheduled-tasks'), os.path.join(REPO, '_底座', '搬家', '定时任务存档'),
          ['--exclude=*.lock', '--exclude=.DS_Store'])
    note(f'  定时任务存档：{count_files(os.path.join(REPO, "_底座", "搬家", "定时任务存档"))[0]} 个文件')
    # 共享笔记
    rsync(NOTES_DIR, os.path.join(REPO, '_底座', '搬家', '共享笔记存档'), ['--exclude=.DS_Store'])
    note(f'  共享笔记存档：{count_files(os.path.join(REPO, "_底座", "搬家", "共享笔记存档"))[0]} 个文件')
    return total_src


# ---------- ③ 录屏分片 ----------
RESTORE_SH = r'''#!/bin/bash
# 还原竞品录屏：把本目录的分片按顺序拼回原件，放到上一级（竞品跟踪分析/），并核 sha256；不符就报错、不留半成品。
# 用法：bash 竞品跟踪分析/录屏分片/还原.sh
set -u
D="$(cd "$(dirname "$0")" && pwd -P)"
OUT="$(cd "$D/.." && pwd -P)"
LISTF="$D/分片sha256.txt"
[ -f "$LISTF" ] || { echo "缺 $LISTF"; exit 2; }
fail=0
# 先核每个分片自己的 sha256
if ! (cd "$D" && grep -v '^原件:' "$LISTF" | grep -v '^#' | shasum -a 256 -c --quiet - ); then
  echo "分片损坏或缺失，停止"; exit 1
fi
while read -r tag sha name size; do
  [ "$tag" = "原件:" ] || continue
  tmp="$OUT/$name.还原中"
  cat "$D/$name".part-* > "$tmp" || { echo "拼接失败 $name"; rm -f "$tmp"; fail=1; continue; }
  got="$(shasum -a 256 "$tmp" | cut -d' ' -f1)"
  if [ "$got" = "$sha" ]; then mv "$tmp" "$OUT/$name"; echo "还原成功 $name"; else echo "sha256 不符 $name"; rm -f "$tmp"; fail=1; fi
done < "$LISTF"
exit $fail
'''


def stage_split():
    P('③ 录屏分片')
    comp = os.path.join(REPO, '竞品跟踪分析')
    outd = os.path.join(comp, '录屏分片')
    os.makedirs(outd, exist_ok=True)
    mp4s = sorted(f for f in os.listdir(comp) if f.lower().endswith('.mp4') and os.path.isfile(os.path.join(comp, f)))
    manifest_p = os.path.join(outd, '分片sha256.txt')
    old = {}
    if os.path.isfile(manifest_p):
        for ln in open(manifest_p, encoding='utf-8').read().splitlines():
            old[ln] = True
    lines = ['# 竞品录屏分片（每片 49 MiB，不压缩）。「原件:」行：sha256 文件名 字节数；其余行：sha256  分片名。还原：bash 还原.sh']
    originals = {}
    for name in mp4s:
        src = os.path.join(comp, name)
        size = os.path.getsize(src)
        osha = sha_file(src)
        originals[name] = (osha, size)
        nparts = max(1, -(-size // SPLIT))
        expect = [f'{name}.part-{k + 1:02d}' for k in range(nparts)]
        part_lines, ok = [], True
        for k, pn in enumerate(expect):
            pp = os.path.join(outd, pn)
            want = min(SPLIT, size - k * SPLIT)
            if not (os.path.isfile(pp) and os.path.getsize(pp) == want):
                ok = False
                break
            part_lines.append((pn, sha_file(pp)))
        if ok:
            # 已有分片：拼起来的 sha 要等于原件（用逐片 sha 在 manifest 里对）
            prev = [ln for ln in old if ln.endswith('  ' + expect[0])]
            ok = all(f'{s}  {pn}' in old for pn, s in part_lines) and f'原件: {osha} {name} {size}' in old
        if not ok:
            for fn in os.listdir(outd):
                if fn.startswith(name + '.part-'):
                    os.remove(os.path.join(outd, fn))
            part_lines = []
            with open(src, 'rb') as f:
                for pn in expect:
                    data = f.read(SPLIT)
                    with open(os.path.join(outd, pn), 'wb') as g:
                        g.write(data)
                    part_lines.append((pn, sha_bytes(data)))
            note(f'  切开 {name}：{size / 1e6:.1f} MB → {nparts} 片')
        else:
            note(f'  {name}：分片已在且 sha 核对一致，跳过')
        lines.append(f'原件: {osha} {name} {size}')
        lines += [f'{s}  {pn}' for pn, s in part_lines]
    open(manifest_p, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    rp = os.path.join(outd, '还原.sh')
    open(rp, 'w', encoding='utf-8').write(RESTORE_SH)
    os.chmod(rp, 0o755)
    return originals


# ---------- 密钥扫描 ----------
NAME_RULES = [
    (re.compile(r'^\.env($|\.)(?!example$|sample$|template$|示例)', re.I), '.env 文件'),
    (re.compile(r'cookie', re.I), '文件名含 cookie'),
    (re.compile(r'\.(pem|p12|pfx|keystore|jks)$', re.I), '证书/私钥文件'),
    (re.compile(r'^id_(rsa|dsa|ecdsa|ed25519)', re.I), 'ssh 私钥'),
    (re.compile(r'secret', re.I), '文件名含 secret'),
    (re.compile(r'\.(sqlite3?|db)$', re.I), '数据库文件'),
    (re.compile(r'^storage_state', re.I), '浏览器登录状态'),
    (re.compile(r'^(Login Data|Cookies|Local State)$'), '浏览器配置'),
]
HIGH = [
    ('sk- 开头的 API key', re.compile(r'(?<![A-Za-z0-9])sk-[A-Za-z0-9_\-]{20,}')),
    ('GitHub token', re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})')),
    ('AWS access key', re.compile(r'AKIA[0-9A-Z]{16}')),
    ('Google API key', re.compile(r'(?<![A-Za-z0-9+/_\-])AIza[0-9A-Za-z_\-]{35}(?![A-Za-z0-9_\-])')),
    ('Slack token', re.compile(r'xox[abprs]-[A-Za-z0-9\-]{10,}')),
    ('私钥头', re.compile(r'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----')),
    ('企业微信 webhook', re.compile(r'qyapi\.weixin\.qq\.com/cgi-bin/webhook/send\?key=[A-Za-z0-9\-]{8,}')),
    ('飞书 webhook', re.compile(r'(?:open\.feishu\.cn|open\.larksuite\.com)/open-apis/bot/v2/hook/[A-Za-z0-9\-]{8,}')),
    ('钉钉 webhook', re.compile(r'oapi\.dingtalk\.com/robot/send\?access_token=[A-Za-z0-9]{8,}')),
    ('Slack webhook', re.compile(r'hooks\.slack\.com/services/T[A-Za-z0-9]+/B[A-Za-z0-9]+/[A-Za-z0-9]+')),
]
GEN = re.compile(
    r'(?<![A-Za-z0-9])(?P<k>api[_\-]?key|apikey|secret(?:[_\-]?key)?|access[_\-]?token|auth[_\-]?token|token|passwd|password|pwd|cookie|'
    r'sessionid|session[_\-]?id|access[_\-]?key|client[_\-]?secret)["\']?[ \t]*[:=][ \t]*(?P<v>["\']?[^\s"\'<>,;)}\]]{1,200})', re.I)
BEARER = re.compile(r'authorization["\']?[ \t]*[:=][ \t]*["\']?bearer[ \t]+(?P<v>[A-Za-z0-9._~+/=\-]{8,200})', re.I)
JWT = re.compile(r'eyJ[A-Za-z0-9_\-]{8,}\.eyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}')
BIN_EXT = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp4', '.mov', '.wav', '.mp3', '.m4a', '.aac', '.zip', '.gz', '.tar', '.pdf',
           '.xlsx', '.xls', '.docx', '.pptx', '.ico', '.ttf', '.otf', '.woff', '.woff2', '.bin', '.jar', '.apk', '.so', '.dylib', '.heic'}
PH_WORDS = ('xxx', 'your', 'example', 'placeholder', 'changeme', 'dummy', 'fake', 'redact', 'todo', 'sample', '示例', '占位',
            '...', '…', '${', '{{', 'null', 'none', 'true', 'false', 'undefined', 'env', 'getenv', 'secret_here', 'token_here')
ID_RE = re.compile(r'^[A-Za-z_][A-Za-z_.\-]*$')
PATHISH = re.compile(r'^[\w./~\-]*[/\\][\w./\-]*$|\.(json|txt|md|py|ini|env|js|ts|html|yaml|yml|cfg|conf|log|csv|pem)$', re.I)


def classify(v):
    """返回 (类别, 形状)；形状只含长度和字符类，不含值。类别：占位｜真｜判不清。"""
    v = v.strip('"\'`')
    shape = f'长度{len(v)}'
    if not v:
        return '占位', shape
    low = v.lower()
    if re.fullmatch(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', v):
        return '占位', shape + '，UUID 形状（会话标识，不是密钥）'
    if len(v) < 8:
        return '占位', shape + '，太短'
    if v[0] in '=$%{<[(@#*' or low.startswith(('os.', 'self.', 'args.', 'config', 'process.', 'request', 'params', 'input', 'http://', 'https://')):
        return '占位', shape
    if any(w in low for w in PH_WORDS):
        return '占位', shape
    if any(ord(c) > 127 for c in v):
        return '占位', shape
    if '(' in v or ')' in v:
        return '占位', shape
    if ID_RE.match(v):
        return '占位', shape
    if PATHISH.search(v):
        return '占位', shape
    has_l, has_d, has_u = bool(re.search(r'[a-z]', v)), bool(re.search(r'\d', v)), bool(re.search(r'[A-Z]', v))
    shape += ('，含字母' if (has_l or has_u) else '') + ('，含数字' if has_d else '')
    if len(v) >= 16 and (has_l or has_u) and has_d:
        return '真', shape
    if len(v) >= 24 and has_l and has_u:
        return '真', shape
    if len(v) >= 40:
        return '真', shape
    return '判不清', shape


def scan_text(text):
    """返回 [(行号, 类型, 档)]，不含值。"""
    hits = []

    def lineno(pos):
        return text.count('\n', 0, pos) + 1
    for name, rx in HIGH:
        for m in rx.finditer(text):
            hits.append((lineno(m.start()), name, '高置信'))
    for m in JWT.finditer(text):
        hits.append((lineno(m.start()), 'JWT', '通用档'))
    for m in BEARER.finditer(text):
        c, shape = classify(m.group('v'))
        if c != '占位':
            hits.append((lineno(m.start()), f'Authorization Bearer（{c}，{shape}）', '通用档'))
    for m in GEN.finditer(text):
        kk = m.group('k')
        if re.fullmatch(r'(?i)session[_\-]?id', kk) and kk not in (kk.lower(), kk.upper()) and not kk.islower():
            continue            # sessionId 驼峰是接口字段（MCP 会话标识），不是登录 cookie 的 sessionid
        c, shape = classify(m.group('v'))
        if c != '占位':
            hits.append((lineno(m.start()), f'{m.group("k").lower()} 赋值（{c}，{shape}）', '通用档'))
    return hits


def blob_info(shas):
    inp = ('\n'.join(shas) + '\n').encode()
    r = git('cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize)', inp=inp)
    out = {}
    for ln in r.stdout.decode().splitlines():
        a = ln.split()
        if len(a) == 3:
            out[a[0]] = (a[1], int(a[2]))
    return out


def scan_entries(entries):
    """entries: [(path, sha)]。返回 (hits{path:[(行,类型,档)]}, 统计)。名字规则也在这里判。"""
    hits, stats = {}, {'扫描': 0, '二进制/大文件未扫': {}, '超大': []}
    info = blob_info(sorted({s for _, s in entries}))
    todo = []
    for path, sh in entries:
        base = os.path.basename(path)
        for rx, why in NAME_RULES:
            if rx.search(base):
                hits.setdefault(path, []).append((0, why, '高置信'))
                break
        ext = os.path.splitext(path)[1].lower()
        if re.search(r'\.part-\d\d$', path):
            ext = '.part'
        sz = info.get(sh, ('blob', 0))[1]
        if sz > MAX_FILE:
            stats['超大'].append((path, sz))
        if ext in BIN_EXT or ext == '.part' or sz > 25_000_000:
            stats['二进制/大文件未扫'][ext or '(无后缀)'] = stats['二进制/大文件未扫'].get(ext or '(无后缀)', 0) + 1
            continue
        todo.append((path, sh, sz))
    if todo:
        p = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=REPO, env=ENV, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        def feed():
            p.stdin.write(('\n'.join(sh for _, sh, _ in todo) + '\n').encode())
            p.stdin.close()
        t = threading.Thread(target=feed)
        t.start()
        for path, sh, sz in todo:
            hdr = p.stdout.readline().split()
            n = int(hdr[2])
            data = p.stdout.read(n)
            p.stdout.readline()
            if b'\0' in data[:8192]:
                stats['二进制/大文件未扫']['(含 NUL 的二进制)'] = stats['二进制/大文件未扫'].get('(含 NUL 的二进制)', 0) + 1
                continue
            stats['扫描'] += 1
            h = scan_text(data.decode('utf-8', 'replace'))
            if h:
                hits.setdefault(path, []).extend(h)
        t.join()
        p.wait()
    return hits, stats


# ---------- 临时索引 ----------
def changed_vs(idx, prev):
    """临时索引相对 prev（提交）的 A/M/T：[(path, mode, sha)]，D：[path]"""
    r = git('diff-index', '--cached', '--raw', '-z', '--no-renames', prev, idx=idx)
    parts = r.stdout.split(b'\0')
    am, de = [], []
    k = 0
    while k + 1 < len(parts):
        meta = parts[k].decode()
        path = parts[k + 1].decode('utf-8', 'replace')
        k += 2
        m = re.match(r':(\d+) (\d+) ([0-9a-f]+) ([0-9a-f]+) (\w)', meta)
        if not m:
            continue
        st = m.group(5)
        if st == 'D':
            de.append(path)
        else:
            am.append((path, m.group(2), m.group(4)))
    return am, de


def read_excl_manual():
    man = set()
    if os.path.isfile(EXCL_FILE):
        for ln in open(EXCL_FILE, encoding='utf-8').read().splitlines():
            a = ln.split('\t')
            if len(a) >= 4 and a[3] == '手工':
                man.add(a[0])
    return man


def revert_paths(idx, prev, paths):
    """把这些路径在临时索引里改回 prev 的版本（prev 里没有就删掉）"""
    if not paths:
        return
    tree = {}
    r = git('ls-tree', '-r', '-z', prev)
    for ent in r.stdout.split(b'\0'):
        if not ent:
            continue
        meta, path = ent.split(b'\t', 1)
        mode, _, sh = meta.decode().split()
        tree[path.decode('utf-8', 'replace')] = (mode, sh)
    lines = []
    for p in paths:
        if p in tree:
            mode, sh = tree[p]
            lines.append(f'{mode} {sh}\t{p}\0')
        else:
            lines.append(f'0 {"0" * 40}\t{p}\0')
    git('update-index', '-z', '--index-info', idx=idx, inp=''.join(lines).encode())


def build_snapshot(prev, mode, idx):
    """mode: full｜videos。返回 (tree, 排除列表[(path,line,type,档,丢了什么)], 扫描统计)"""
    git('read-tree', prev, idx=idx)
    if mode == 'full':
        spec = ROOT_DIRS + ROOT_FILES + ROOT_GLOBS
        # 根目录散放文件在磁盘上必须存在才能当 pathspec
        present = [s for s in spec if os.path.exists(os.path.join(REPO, s)) or '*' in s]
        git('add', '-A', '--', *present, idx=idx)
    else:
        git('add', '-A', '--', '抖音号/videos', idx=idx)
    manual = read_excl_manual()
    excl = []
    stats = None
    for rnd in range(3):
        am, de = changed_vs(idx, prev)
        am = [(p, m, s) for p, m, s in am]
        hits, stats = scan_entries([(p, s) for p, _, s in am])
        bad = set(hits) | (manual & {p for p, _, _ in am})
        if not bad:
            break
        prev_paths = set()
        r = git('ls-tree', '-r', '--name-only', '-z', prev)
        prev_paths = {x.decode('utf-8', 'replace') for x in r.stdout.split(b'\0') if x}
        for p in sorted(bad):
            lost = '今天对该文件的改动（库里仍是上一版）' if p in prev_paths else '整个文件'
            if p in hits:
                for ln, ty, tier in hits[p]:
                    excl.append((p, ln, ty, tier, lost))
            else:
                excl.append((p, 0, '手工排除', '手工', lost))
        revert_paths(idx, prev, bad)
    else:
        raise Stop('密钥扫描三轮后仍有命中')
    return excl, stats


# ---------- 没带走清单 ----------
def du(p):
    if os.path.islink(p):
        return 0
    if os.path.isfile(p):
        return os.path.getsize(p)
    s = 0
    for dp, dn, fn in os.walk(p):
        for f in fn:
            try:
                s += os.lstat(os.path.join(dp, f)).st_size
            except OSError:
                pass
    return s


def mb(n):
    return f'{n / 1e6:.1f} MB' if n >= 1e5 else f'{n / 1e3:.0f} KB'


def write_notcarried(idx, excl, batch, with_videos, originals):
    P('  生成 没带走清单.md')
    L = ['# 没带走的东西（收工脚本生成，每次重算）',
         '',
         f'生成：{datetime.date.today().isoformat()}，第 {batch} 批。新环境靠这份知道缺什么；原因都写在每一项后面。只列名字和大小，不含任何内容。',
         '']
    # 1 对话记录
    n = s = 0
    for dp, dn, fn in os.walk(os.path.join(CLAUDE_DIR, 'projects')):
        for f in fn:
            if f.endswith('.jsonl'):
                n += 1
                s += os.path.getsize(os.path.join(dp, f))
    L += ['## 1. 对话记录（不带，过不去；所有主对话、分发要在新环境重开）',
          f'- `~/.claude/projects/*/*.jsonl`：{n} 个，{s / 1e9:.1f} GB。靠各项目 `先看这里.md` 和 `_底座/任务/` 接手。', '']
    # 2 密钥
    L += ['## 2. 因疑似密钥没进库的文件（只列路径、行号、类型，值没有记录）']
    if excl:
        agg = {}
        for p, ln, ty, tier, lost in excl:
            agg.setdefault(p, []).append((ln, re.sub(r'（.*', '', ty), tier, lost))
        for p, v in agg.items():
            types = '、'.join(sorted({t for _, t, _, _ in v}))
            L.append(f'- `{p}`：共 {len(v)} 处，首处行 {v[0][0]}，类型 {types}，{v[0][2]}；没进库的是：{v[0][3]}')
    else:
        L.append('- 无')
    L += ['']
    # 3 被 .gitignore 挡掉的
    r = git('ls-files', '-o', '-i', '--exclude-standard', '--directory', '-z', '--',
            *[x for x in ROOT_DIRS if os.path.isdir(os.path.join(REPO, x))], idx=idx)
    groups = {}
    for ent in r.stdout.split(b'\0'):
        if not ent:
            continue
        pth = ent.decode('utf-8', 'replace')
        if pth.endswith('.DS_Store') or '/.DS_Store' in pth:
            continue
        parts = pth.rstrip('/').split('/')
        key = '/'.join(parts[:3]) + ('/' if len(parts) > 3 or pth.endswith('/') else '')
        g = groups.setdefault(key, [0, 0])
        g[0] += 1
        g[1] += du(os.path.join(REPO, pth))
    rows = sorted(groups.items(), key=lambda kv: -kv[1][1])
    L += ['## 3. 被各项目 `.gitignore` 挡掉的（按大小，路径取前三级）',
          '原因：根 `.gitignore` 挡运行环境、构建产物、缓存、锁文件和录屏原件；弹窗 `.gitignore` 只挡系统文件和本机设置（11/04 起旧版本、归档、分析、简报都带）。',
          '| 路径 | 项数 | 大小 |', '|---|---|---|']
    for k, (c, sz) in rows[:60]:
        L.append(f'| `{k}` | {c} | {mb(sz)} |')
    if len(rows) > 60:
        L.append(f'| 其余 {len(rows) - 60} 项 | {sum(c for _, (c, _) in rows[60:])} | {mb(sum(sz for _, (_, sz) in rows[60:]))} |')
    L += ['']
    # 4 抖音号
    L += ['## 4. 抖音号（来源 `~/Documents/dy`，进库位置 `抖音号/`）']
    for name, why in (('.venv', '运行环境，重装就有'), ('node_modules', '依赖，重装就有'), ('tools/node', '运行环境（117M node），重装就有')):
        tot = 0
        for dp, dn, fn in os.walk(DY):
            rel = os.path.relpath(dp, DY)
            if name == 'tools/node':
                if rel == 'tools':
                    if 'node' in dn:
                        tot += du(os.path.join(dp, 'node'))
                    continue
                if rel.startswith('tools/node'):
                    dn[:] = []
                    continue
            else:
                if name in dn:
                    tot += du(os.path.join(dp, name))
                    dn.remove(name)
            if rel.startswith('.venv') or '/node_modules' in rel:
                dn[:] = []
        L.append(f'- `{name}`：{mb(tot)}，{why}')
    refer = [f for f in sorted(os.listdir(os.path.join(DY, '参考'))) if f.lower().endswith(('.mp4', '.png'))] if os.path.isdir(os.path.join(DY, '参考')) else []
    L.append(f'- `参考/` 下别人的视频和截帧：{len(refer)} 个文件，{mb(sum(du(os.path.join(DY, "参考", f)) for f in refer))}（`.mp4`、`.png`，笔记 md 留着）')
    if not with_videos:
        v = os.path.join(DY, 'videos')
        L.append(f'- `videos/` 的 mp4、wav、png 等大文件：{mb(du(v)) if os.path.isdir(v) else "无"}，**这一批没带**，后面单独一批（「视频」批）带；清单里的文字和小图已带')
    else:
        L.append('- `videos/` 已随「视频」批带上')
    L += ['']
    # 5 消息助手
    tot = 0
    for dp, dn, fn in os.walk(MSG_HELPER):
        for d in list(dn):
            if d in ('build', '.gradle', '.kotlin'):
                tot += du(os.path.join(dp, d))
                dn.remove(d)
    L += ['## 5. 消息助手（来源 `~/Documents/消息助手`，进库位置 `消息助手/`）',
          f'- 构建产物 `build/`、`.gradle/`、`.kotlin/`、`local.properties`：{mb(tot)}，重新构建就有', '']
    # 6 录屏
    L += ['## 6. 竞品录屏原件（超 100M，改放分片）']
    for name, (osha, size) in sorted(originals.items()):
        L.append(f'- `竞品跟踪分析/{name}`：{mb(size)}，原件不进库，分片在 `竞品跟踪分析/录屏分片/`，还原见 `竞品跟踪分析/先看这里.md`')
    L += ['']
    # 7 家目录其余
    L += ['## 线上页面', '- claude.ai 上 18 个页面：线上原页面不在仓库里，存档已带，在 `_底座/任务/弹窗标签推送系统/线上页面存档_1104/`。', '']
    L += ['## 7. 本机家目录里没带的（只列名字和大小，没读内容）']
    docs = os.path.join(HOME, 'Documents')
    for f in sorted(os.listdir(docs)) if os.path.isdir(docs) else []:
        if f in ('dy', '消息助手') or f == '.DS_Store':
            continue
        L.append(f'- `~/Documents/{f}`：{mb(du(os.path.join(docs, f)))}')
    L.append('- `~/.claude/settings.json`、`settings.local.json`、插件、缓存、对话记录：不带（钩子登记在 `_底座/搬家/规则包/钩子登记.json`，装上.sh 会打印合并命令）')
    L.append('- `~/claude/.claude/`（`launch.json`、`settings.local.json`）：不带')
    L.append('- `~/claude/.claude/worktrees/`、所有 `.venv`、`node_modules`：不带，重装就有')
    L += ['']
    text = '\n'.join(L) + '\n'
    p = os.path.join(REPO, '_底座', '搬家', '没带走清单.md')
    open(p, 'w', encoding='utf-8').write(text)
    git('add', '-f', '--', '_底座/搬家/没带走清单.md', idx=idx)


def write_excl_file(excl):
    lines = ['# 收工脚本生成；不进库（被 .gitignore 挡）。路径\t行号\t类型\t档\t没进库的是什么。值没有记录。「手工」档的行会一直保留。']
    for p, ln, ty, tier, lost in excl:
        lines.append(f'{p}\t{ln}\t{ty}\t{tier}\t{lost}')
    open(EXCL_FILE, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')


# ---------- 合并 ----------
def resolve_base():
    global BASE_REF
    if not BASE_REF:
        BASE_REF = {'1': 'origin/main', '视频': f'{REFB}/M1', '补带': f'{REFB}/M视频',
                    '收工': next((f'{REFB}/{x}' for x in ('M补带', 'M视频') if rev(f'{REFB}/{x}')), f'{REFB}/M1')}[BATCH]
        if BASE_REF.startswith(REFB + '/') and not rev(BASE_REF):
            raise Stop(f'{BASE_REF} 还不存在（上一批没通过检查或没跑过），要么先跑上一批，要么用 --基 指定')
    remotes = gs('remote').split()
    m = re.match(r'^([^/]+)/(.+)$', BASE_REF)
    if m and m.group(1) in remotes:
        P(f'  git fetch {m.group(1)} {m.group(2)}（失败只警告）')
        try:
            r = git('fetch', '--quiet', m.group(1), m.group(2), check=False, timeout=90)
            if r.returncode != 0:
                note(f'  警告：git fetch 失败（rc={r.returncode}），改用本地已有的 {BASE_REF}：{r.stderr.decode("utf-8", "replace")[-200:].strip()}')
        except subprocess.TimeoutExpired:
            note(f'  警告：git fetch 超时，改用本地已有的 {BASE_REF}')
    sha = rev(BASE_REF + '^{commit}')
    if not sha:
        raise Stop(f'--基 {BASE_REF} 在本地解析不出提交')
    note(f'  合并基 {BASE_REF} = {sha}')
    return sha


def two_sided(base_sha, L):
    mb_ = gs('merge-base', L, base_sha) if git('merge-base', L, base_sha, check=False).returncode == 0 else None
    if not mb_:
        return [], None

    def names(a, b):
        r = git('diff', '--name-status', '--no-renames', '-z', a, b)
        parts = r.stdout.split(b'\0')
        d = {}
        for k in range(0, len(parts) - 1, 2):
            d[parts[k + 1].decode('utf-8', 'replace')] = parts[k].decode()
        return d
    mine, theirs = names(mb_, L), names(mb_, base_sha)
    return sorted((p, mine[p], theirs[p]) for p in mine if p in theirs), mb_


def merge(L, base_sha):
    cfg = ['merge.directoryRenames=false']
    # 先不带 -X 跑一遍，数出哪些文件真有冲突片段（只为报告）
    plain = git('merge-tree', '--write-tree', '--name-only', L, base_sha, cfg=cfg, check=False)
    pl = plain.stdout.decode('utf-8', 'replace').split('\n')
    conflicted = []
    if plain.returncode == 1:
        for ln in pl[1:]:
            if ln == '':
                break
            conflicted.append(ln)
    both, mbase = two_sided(base_sha, L)
    rep = []
    for p, a, b in both:
        if p in conflicted:
            tree = pl[0]
            blob = git('cat-file', 'blob', f'{tree}:{p}', check=False).stdout.decode('utf-8', 'replace')
            k = len(re.findall(r'^<<<<<<< ', blob, re.M))
            rep.append(f'{p}｜本机 {a}／GitHub {b}｜{k} 处冲突片段：片段取本机，两边不冲突的改动都留')
        else:
            rep.append(f'{p}｜本机 {a}／GitHub {b}｜自动合并无冲突，两边改动都留')
    r = git('merge-tree', '--write-tree', '-X', 'ours', L, base_sha, cfg=cfg, check=False)
    out = r.stdout.decode('utf-8', 'replace').split('\n')
    if r.returncode != 0:
        names = [x for x in out[1:] if x]
        raise Stop(f'-X ours 后仍有冲突（rc={r.returncode}），停：{names[:20]}')
    return out[0].strip(), rep, mbase


# ---------- ⑦ 检查 ----------
def check_tree(M, base_sha, base_c, excl_paths, with_videos, mode='full'):
    """返回 (问题列表, 信息)"""
    prob, info = [], []
    # a. 嵌套仓库、符号链接
    r = git('ls-tree', '-r', '-z', M)
    ents = [e for e in r.stdout.split(b'\0') if e]
    n160 = sum(1 for e in ents if e.startswith(b'160000 '))
    n120 = sum(1 for e in ents if e.startswith(b'120000 '))
    info.append(f'M 的树：{len(ents)} 个条目；mode 160000：{n160}；mode 120000：{n120}')
    if n160:
        prob.append(f'M 里有 mode 160000（嵌套仓库）{n160} 个')
    if n120:
        prob.append(f'M 里有符号链接 {n120} 个')
    # b. 大文件（新增部分）
    r = git('diff-tree', '-r', '--no-renames', '-z', '--raw', base_sha, M)
    parts = r.stdout.split(b'\0')
    newb = []
    for k in range(0, len(parts) - 1, 2):
        m = re.match(r':(\d+) (\d+) ([0-9a-f]+) ([0-9a-f]+) (\w)', parts[k].decode())
        if m and m.group(5) in 'AMT':
            newb.append((parts[k + 1].decode('utf-8', 'replace'), m.group(4)))
    sizes = blob_info(sorted({s for _, s in newb}))
    big = [(p, sizes[s][1]) for p, s in newb if s in sizes and sizes[s][1] > MAX_FILE]
    warn = [(p, sizes[s][1]) for p, s in newb if s in sizes and WARN_FILE < sizes[s][1] <= MAX_FILE]
    info.append(f'相对 基 新增或改动 {len(newb)} 个文件；超 {MAX_FILE // 1000000}M：{len(big)}；50–99M（只警告）：{len(warn)}')
    for p, sz in warn:
        info.append(f'  50M 以上警告：{p} {mb(sz)}')
    if big:
        prob.append('单文件超 100M：' + '、'.join(p for p, _ in big[:10]))
    # c. 对账
    idxM = os.path.join(RUN_DIR, 'idx_M')
    git('read-tree', M, idx=idxM)
    if mode == 'videos':
        spec = ['抖音号/videos']
    else:
        spec = [x for x in ROOT_DIRS if os.path.isdir(os.path.join(REPO, x))] + ['.gitignore', 'README.md', 'CLAUDE.md']
    r = git('ls-files', '-o', '--exclude-standard', '-z', '--', *spec, idx=idxM)
    others = [x.decode('utf-8', 'replace') for x in r.stdout.split(b'\0') if x]
    base_tree = {}
    for e in git('ls-tree', '-r', '-z', base_c).stdout.split(b'\0'):
        if e:
            meta, path = e.split(b'\t', 1)
            base_tree[path.decode('utf-8', 'replace')] = meta.decode().split()[2]
    up = {x.decode('utf-8', 'replace') for x in git('ls-tree', '-r', '--name-only', '-z', base_sha).stdout.split(b'\0') if x}
    up_gone = [p for p in others if p in base_tree and p not in up]
    h = {}
    if up_gone:
        out = git('hash-object', '--stdin-paths', inp=('\n'.join(up_gone) + '\n').encode()).stdout.decode().split()
        h = dict(zip(up_gone, out))
    n_gone = n_secret = 0
    for p in others:
        if p in excl_paths:
            n_secret += 1
        elif p in base_tree and p not in up:
            if h.get(p) == base_tree[p]:
                n_gone += 1
            else:
                prob.append(f'对账：{p} 在 GitHub 侧已删或改名，但本机内容和旧基线不同（本机改过）')
        else:
            prob.append(f'对账：磁盘上有、M 里没有、也没有写明原因的不带规则：{p}')
    info.append(f'对账：磁盘上不被忽略、M 里没有的 {len(others)} 个 = GitHub 侧已删或改名且本机内容同旧基线 {n_gone} + 密钥排除 {n_secret}；其余 {len(others) - n_gone - n_secret}')
    # 抖音号、消息助手来源侧对账
    miss = []
    excl_dirs = {'.venv', 'node_modules'}
    for dp, dn, fn in os.walk(os.path.join(DY, 'videos') if mode == 'videos' else DY):
        rel = os.path.relpath(dp, DY)
        dn[:] = [d for d in dn if d not in excl_dirs and not (rel == 'tools' and d == 'node')]
        for f in fn:
            if f == '.DS_Store':
                continue
            rp = os.path.normpath(os.path.join(rel, f))
            if os.path.islink(os.path.join(dp, f)):
                continue
            miss.append(rp)
    tree_paths = set(base_tree) | up
    inM = {e.split(b'\t', 1)[1].decode('utf-8', 'replace') for e in ents}
    unexpl = []
    for rp in miss:
        if '抖音号/' + rp in inM:
            continue
        low = rp.lower()
        if rp.startswith('参考/') and low.endswith(('.mp4', '.png')):
            continue
        if low.endswith('.lock'):
            continue            # 清单明写 /.claude/scheduled_tasks.lock 不带，根 .gitignore 也挡 *.lock
        if low.endswith(('.mp4', '.wav', '.png', '.jpg', '.jpeg')) and (not with_videos or not rp.startswith('videos/')):
            continue            # 清单明写不带的媒体（已列进没带走清单）；批 1 时 videos/ 大文件另一批
        if '抖音号/' + rp in {p for p, _ in newb}:
            continue
        if f'抖音号/{rp}' in excl_paths:
            continue
        unexpl.append(rp)
    info.append(f'抖音号来源 {len(miss)} 个文件，M 里有 {sum(1 for rp in miss if "抖音号/" + rp in inM)}；清单明写不带的媒体已在没带走清单；其余未解释 {len(unexpl)}')
    for rp in unexpl[:20]:
        prob.append(f'对账：抖音号来源文件没进 M 又不在不带规则里：{rp}')
    # d. 两个 .gitignore
    gi = git('cat-file', 'blob', f'{M}:弹窗标签推送系统/.gitignore', check=False).stdout.decode('utf-8', 'replace').splitlines()
    for need in ('!归档/记录_至1020/', '!简报/2026-11-*', '!简报/2026-10-3*'):
        if need not in gi:
            prob.append(f'弹窗 .gitignore 缺行：{need}')
    root_blob = git('cat-file', 'blob', f'{M}:.gitignore').stdout
    if root_blob != open(os.path.join(REPO, '.gitignore'), 'rb').read():
        prob.append('M 里的根 .gitignore 和磁盘上的不同')
    info.append('两个 .gitignore：弹窗的同时有 GitHub 那行和本机新加的放行行；根的和磁盘一致' if not any('.gitignore' in x for x in prob) else '两个 .gitignore：有问题')
    return prob, info, newb


def pack_sizes(base_sha, M):
    def total(rng):
        out = git('rev-list', '--disk-usage', '--objects', *rng).stdout.decode().split()
        return int(out[0]), 0
    return total([M, '^' + base_sha])[0], total([M])[0]


def clone_verify(M, mem_src_count, originals, with_videos, base_sha):
    """克隆 M 到临时目录；逐项核；真装一遍再自检。返回 (问题, 信息)"""
    prob, info = [], []
    tmphome = os.path.join(RUN_DIR, 'home')
    clone = os.path.join(tmphome, 'claude')
    os.makedirs(tmphome, exist_ok=True)
    git('update-ref', f'{REFB}/待验', M)
    t = time.time()
    for attempt, flags in enumerate((['--local'], ['--local'], ['--no-hardlinks'])):
        r = run(['git', 'clone'] + flags + ['--no-checkout', '-q', REPO, clone], check=False)
        if r.returncode == 0:
            break
        info.append(f'克隆第 {attempt + 1} 次失败（别的进程可能同时在动 .git/objects），重试：{r.stderr.decode("utf-8", "replace")[-120:].strip()}')
        shutil.rmtree(clone, ignore_errors=True)
    else:
        raise Stop('git clone 三次都失败')
    run(['git', '-C', clone, '-c', 'advice.detachedHead=false', 'checkout', '-q', M])
    info.append(f'克隆并检出 M：{time.time() - t:.0f} 秒')
    st = run(['git', '-C', clone, 'status', '--porcelain'], check=False).stdout.decode().strip()
    if st:
        prob.append('克隆检出后 git status 不干净')

    def ex(rel):
        return os.path.exists(os.path.join(clone, rel))
    need = ['_底座/任务/用好Claude/盯弹窗验收_核对清单.md', '_底座/任务/用好Claude/2026-11-04_今天全部进GitHub.md',
            '_底座/搬家/收工.sh', '_底座/搬家/没带走清单.md', '_底座/搬家/换环境说明.md', '_底座/搬家/装上.sh',
            '弹窗标签推送系统/简报/2026-11-04_给主管讲功能的汇报做法.html', '弹窗标签推送系统/简报/2026-11-04_给主管讲功能的汇报做法',
            '商城/先看这里.md', '用好Claude/先看这里.md', '团队工作模式/先看这里.md', '抖音总结', '企业微信自动回复/先看这里.md',
            '企业微信自动回复/代码/autoreply', '消息助手/relay/src', '抖音号/现状.md', '抖音号/studio/src',
            '竞品跟踪分析/先看这里.md', '竞品跟踪分析/录屏分片/还原.sh', '竞品跟踪分析/录屏分片/分片sha256.txt',
            '方案_目录.html', '图像.png', 'image.png', '会员价值数据分析报告_v2.md', '.gitignore', 'CLAUDE.md']
    for d in ('夜间记录', '考试/原稿', '压缩记录.md'):
        if os.path.exists(os.path.join(REPO, '_底座', d)):
            need.append('_底座/' + d)
    for dp in os.listdir(os.path.join(REPO, '_底座', '考试')):
        if dp.startswith('校准_') and os.path.isdir(os.path.join(REPO, '_底座', '考试', dp, '图')):
            need.append(f'_底座/考试/{dp}/图')
    for name in originals:
        need.append(f'竞品跟踪分析/录屏分片/{name}.part-01')
    if with_videos:
        need.append('抖音号/videos')
    miss = [x for x in need if not ex(x)]
    if miss:
        prob.append('克隆里缺：' + '、'.join(miss))
    pics = len([f for f in os.listdir(os.path.join(clone, '弹窗标签推送系统/简报/2026-11-04_给主管讲功能的汇报做法'))]) if ex('弹窗标签推送系统/简报/2026-11-04_给主管讲功能的汇报做法') else 0
    nmem = count_files(os.path.join(clone, '_底座/搬家/记忆'), skip_names=())[0]
    if nmem != mem_src_count:
        prob.append(f'克隆里记忆文件 {nmem} 个，来源 {mem_src_count} 个')
    root_loose = [f for f in os.listdir(clone) if os.path.isfile(os.path.join(clone, f))]
    info.append(f'克隆里：记忆 {nmem}（来源 {mem_src_count}）；11-04 简报配图文件夹 {pics} 个文件；根目录文件 {len(root_loose)} 个；必带项缺 {len(miss)} 个（共查 {len(need)} 项）')
    # 完成标准 1：录屏还原 sha
    t = time.time()
    r = run(['bash', os.path.join(clone, '竞品跟踪分析/录屏分片/还原.sh')], check=False)
    info.append(f'还原.sh：rc={r.returncode}，{time.time() - t:.0f} 秒')
    if r.returncode != 0:
        prob.append('还原.sh 不过：' + r.stdout.decode('utf-8', 'replace')[-200:])
    for name, (osha, size) in originals.items():
        fp = os.path.join(clone, '竞品跟踪分析', name)
        got = sha_file(fp) if os.path.isfile(fp) else None
        ok = (got == osha) and (osha == sha_file(os.path.join(REPO, '竞品跟踪分析', name)))
        info.append(f'  还原件 sha 和本机原件{"相同" if ok else "不同"}：{name}')
        if not ok:
            prob.append(f'录屏还原后 sha 不等于原件：{name}')
        if os.path.isfile(fp):
            os.remove(fp)
    # 完成标准 2：真装一遍 + 自检（临时 HOME）
    env = dict(ENV, HOME=tmphome)
    inst = os.path.join(clone, '_底座/搬家/装上.sh')
    r1 = run(['bash', inst, '--执行', '--根', tmphome], env=env, check=False, cwd=clone)
    info.append(f'装上.sh --执行：rc={r1.returncode}')
    if r1.returncode != 0:
        prob.append('装上.sh --执行 不过：' + r1.stdout.decode('utf-8', 'replace')[-400:])
    # 装上.sh 不碰 settings.json，只打印一条合并命令让人自己跑（--根 模式下它指向临时 HOME 里的 settings.json）；
    # 新环境里这一步由人跑，这里在临时 HOME 里照跑一遍，⑤ 才能过。命令里的目标路径必须在临时 HOME 下才跑。
    out1 = r1.stdout.decode('utf-8', 'replace')
    mark = '请自己跑这条命令（先备份 settings.json，只合并 hooks 一段）：\n'
    if mark in out1:
        cmd = out1.split(mark, 1)[1].strip()
        if any(f'"{h}/.claude/settings.json"' in cmd for h in (tmphome, os.path.realpath(tmphome))):
            rr = run(['bash', '-c', cmd], env=env, check=False, cwd=clone)
            info.append(f'  按装上.sh 打印的命令在临时 HOME 里合并 hooks：rc={rr.returncode}')
        else:
            prob.append('装上.sh 打印的 settings 合并命令目标不在临时 HOME 下，没敢跑')
    r2 = run(['bash', inst, '--自检', '--根', tmphome], env=env, check=False, cwd=clone)
    out2 = r2.stdout.decode('utf-8', 'replace')
    open(os.path.join(RUN_DIR, '自检输出.txt'), 'w', encoding='utf-8').write(out2)
    info.append(f'装上.sh --自检：rc={r2.returncode}（输出存 {os.path.join(RUN_DIR, "自检输出.txt")}）')
    if r2.returncode != 0:
        prob.append('装上.sh --自检 不过（九项没全过）：' + out2[-600:])
    # 完成标准 3：整棵克隆的高置信样式
    tot_hits = {}
    for dp, dn, fn in os.walk(clone):
        dn[:] = [d for d in dn if d != '.git']
        for f in fn:
            p = os.path.join(dp, f)
            ext = os.path.splitext(f)[1].lower()
            if ext in BIN_EXT or '.part-' in f:
                continue
            try:
                if os.path.getsize(p) > 25_000_000:
                    continue
                data = open(p, 'rb').read()
            except OSError:
                continue
            if b'\0' in data[:8192]:
                continue
            txt = data.decode('utf-8', 'replace')
            for name_, rx in HIGH:
                if rx.search(txt):
                    tot_hits.setdefault(os.path.relpath(p, clone), []).append(name_)
    for dp, dn, fn in os.walk(clone):
        dn[:] = [d for d in dn if d != '.git']
        for f in fn:
            for rx, why in NAME_RULES:
                if rx.search(f):
                    tot_hits.setdefault(os.path.relpath(os.path.join(dp, f), clone), []).append(why)
    info.append(f'整棵克隆的高置信密钥样式命中文件：{len(tot_hits)} 个')
    for p, v in list(tot_hits.items())[:20]:
        prob.append(f'克隆里高置信命中：{p}（{"、".join(sorted(set(v)))}）')
    shutil.rmtree(clone, ignore_errors=True)
    return prob, info


# ---------- 主流程 ----------
def main():
    before = state()
    P(f'批 {BATCH}　基 {BASE_REF or "(按批默认)"}　运行目录 {RUN_DIR}')
    P(f'开始前：HEAD={before["HEAD"][:10]} main={before["main"][:10]} 索引 sha={before["index"][:10]} ~/.claude 指纹={before["claude"][0][:10]}（{before["claude"][1]} 项）')
    # ① 导出对比
    P('① 导出对比')
    ex_sh = os.path.join(HERE, '导出.sh')
    r = run(['bash', ex_sh, '--对比'], check=False)
    if r.returncode == 1:
        note('  规则包和本机不一致，先 导出.sh --执行 再对比')
        r = run(['bash', ex_sh, '--执行'], check=False)
        if r.returncode != 0:
            raise Stop('导出.sh --执行 不过：' + r.stdout.decode('utf-8', 'replace')[-300:])
        r = run(['bash', ex_sh, '--对比'], check=False)
    if r.returncode != 0:
        raise Stop('导出.sh --对比 不过：' + r.stdout.decode('utf-8', 'replace')[-300:])
    P('  ' + r.stdout.decode('utf-8', 'replace').strip().splitlines()[-1])

    # 前一个 L 与 BASE
    base_c = rev(f'{REFB}/BASE') or rev('refs/heads/main')
    if BATCH == '1':
        prev, mode, with_videos = base_c, 'full', False
    elif BATCH == '视频':
        prev = rev(f'{REFB}/L1')
        if not prev:
            raise Stop('还没有第一批的 L（refs/banjia/L1），先跑 --批 1')
        mode, with_videos = 'videos', True
    else:
        prev, mode = base_c, 'full'
        with_videos = bool(rev(f'{REFB}/L视频'))
        if not rev(f'{REFB}/L1'):
            raise Stop('还没有第一批的 L（refs/banjia/L1），先跑 --批 1')
    # 收工批的父：上一个 L，保证第二次不回退第一次
    if BATCH == '补带':
        parent_L = rev(f'{REFB}/L视频')
        if not parent_L:
            raise Stop('还没有视频批的 L（refs/banjia/L视频），先跑 --批 视频')
    elif BATCH == '收工':
        parent_L = rev(f'{REFB}/L补带') or rev(f'{REFB}/L视频') or rev(f'{REFB}/L1')
    else:
        parent_L = prev
    P(f'本批：快照 {mode}，树基 {prev[:10]}，L 的父 {parent_L[:10]}，{"含" if with_videos else "不含"} 抖音号/videos/ 大文件')

    # ② ③
    mem_src = 0
    originals = {}
    if mode == 'full':
        mem_src = stage_copy(with_videos)
        originals = stage_split()
    else:
        copy_dy(True)       # 视频批只复制 抖音号（含 videos/）；其余沿用上一个 L 的树
        mem_src = len([1 for e in git('ls-tree', '-r', '-z', '--name-only', prev, '--', '_底座/搬家/记忆').stdout.split(b'\0') if e])
    if UPTO == '复制':
        P('已按 --到 复制 停下')
        return

    # ④ 快照 + 密钥扫描
    P('④ 临时索引快照 + 密钥扫描')
    idx = os.path.join(RUN_DIR, 'idx_L')
    excl, stats = build_snapshot(prev, mode, idx)
    note(f'  文本文件扫描 {stats["扫描"]} 个；没法扫的（二进制或太大）按类型：' + '、'.join(f'{k}×{v}' for k, v in sorted(stats['二进制/大文件未扫'].items(), key=lambda kv: -kv[1])[:14]))
    note(f'  命中并排除：{len({e[0] for e in excl})} 个文件，{len(excl)} 处')
    byp = {}
    for p, ln, ty, tier, lost in excl:
        byp.setdefault(p, []).append((ln, ty, tier))
    for p, v in byp.items():
        note(f'    排除 {p}　{len(v)} 处　首处行 {v[0][0]}　{v[0][1]}　{v[0][2]}')
    if stats['超大']:
        raise Stop('有单文件超 100M：' + '、'.join(p for p, _ in stats['超大'][:10]))
    write_excl_file(excl)
    # 对 originals 的 mp4 原件：如果是视频批，originals 要从磁盘算
    if not originals:
        comp = os.path.join(REPO, '竞品跟踪分析')
        mf = os.path.join(comp, '录屏分片', '分片sha256.txt')
        if os.path.isfile(mf):
            for ln in open(mf, encoding='utf-8').read().splitlines():
                if ln.startswith('原件:'):
                    _, s, n, z = ln.split()
                    originals[n] = (s, int(z))
    if mode == 'full':
        write_notcarried(idx, excl, BATCH, with_videos, originals)
    else:
        # 视频批：树 = 上一个 L + videos/；不重写没带走清单（那一份写着「视频批才带」，在收工批里改写）
        pass
    tree = gs('write-tree', idx=idx)
    msg = f'搬家快照（批 {BATCH}）：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>'
    L = gs('commit-tree', tree, '-p', parent_L, '-m', msg)
    note(f'⑤ L = {L}（树 {tree[:10]}，父 {parent_L[:10]}）')
    if UPTO == '快照':
        P('已按 --到 快照 停下')
        return

    # ⑥ 合并
    P('⑥ 合并')
    base_sha = resolve_base()
    mt, rep, mbase = merge(L, base_sha)
    note(f'  合并树 {mt}；merge-base {mbase[:10] if mbase else "无"}')
    rp = os.path.join(RUN_DIR, '两边都改的文件.txt')
    open(rp, 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
    note(f'  两边都改过的文件 {len(rep)} 个，取舍写在 {rp}')
    Mmsg = f'搬家合并（批 {BATCH}）：以 {BASE_REF} 为第一父，本机快照 L 为第二父；冲突片段取本机\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>'
    M = gs('commit-tree', mt, '-p', base_sha, '-p', L, '-m', Mmsg)
    note(f'  M = {M}')
    if UPTO == '合并':
        P('已按 --到 合并 停下')
        return

    # ⑦ 检查
    P('⑦ 程序检查')
    excl_paths = {e[0] for e in excl}
    prob, info, newb = check_tree(M, base_sha, base_c, excl_paths, with_videos, mode)
    # 合并后再扫一遍当关卡
    hits, st2 = scan_entries(newb)
    info.append(f'密钥关卡：M 相对 基 新增或改动 {len(newb)} 个文件，扫文本 {st2["扫描"]} 个，命中 {len(hits)} 个')
    for p, v in hits.items():
        prob.append(f'密钥关卡命中：{p}（行 {v[0][0]}，{v[0][1]}）')
    inc, full = pack_sizes(base_sha, M)
    send = full if BATCH == '1' else inc
    info.append(f'包体（对象在磁盘上的压缩大小之和，git rev-list --disk-usage）：整段历史 {full / 1e6:.0f} MB；相对 {BASE_REF} 的增量 {inc / 1e6:.0f} MB；本次推送按 {"整段历史" if BATCH == "1" else "增量"} 算 = {send / 1e6:.0f} MB')
    if send > 1_900_000_000:
        prob.append(f'本次推送 {send / 1e9:.2f} GB 超过 1.9G，要按目录拆成多个 M（思考页 7.7）')
    for x in info:
        note('  ' + x)
    if prob:
        for x in prob:
            P('  不过：' + x)
        git('update-ref', '-d', f'{REFB}/待验', check=False)
        raise Stop(f'程序检查有 {len(prob)} 项不过')
    cprob, cinfo = clone_verify(M, mem_src or count_memory(), originals, with_videos, base_sha)
    for x in cinfo:
        note('  ' + x)
    if cprob:
        for x in cprob:
            P('  不过：' + x)
        git('update-ref', '-d', f'{REFB}/待验', check=False)
        raise Stop(f'克隆核对有 {len(cprob)} 项不过')
    # 完成标准 4
    after = state()
    bad4 = []
    for k in ('HEAD', 'main'):
        if before[k] != after[k]:
            bad4.append(f'{k} 变了')
    if before['claude'] != after['claude']:
        bad4.append('~/.claude/ 指纹变了')
    if bad4:
        git('update-ref', '-d', f'{REFB}/待验', check=False)
        raise Stop('完成标准 4 不过：' + '、'.join(bad4))
    note(f'  完成标准 4：HEAD、main、~/.claude 指纹（{after["claude"][1]} 项）前后相同；真索引 sha {"前后相同" if before["index"] == after["index"] else "前后不同（本脚本没写它，疑是别的对话在 git add/status，不判失败）"}')
    # 写引用
    if not rev(f'{REFB}/BASE'):
        git('update-ref', f'{REFB}/BASE', base_c)
    git('update-ref', f'{REFB}/L{BATCH}', L)
    git('update-ref', f'{REFB}/M{BATCH}', M)
    git('update-ref', '-d', f'{REFB}/待验', check=False)
    # ⑧ 打印
    print('\n' + '=' * 60)
    print(f'批 {BATCH} 算完，全部程序检查通过。')
    print(f'M = {M}')
    print(f'L = {L}')
    print(f'包体：本次推送 {send / 1e6:.0f} MB（{"空仓库，整段历史" if BATCH == "1" else "相对上一个 M 的增量"}）；整段历史 {full / 1e6:.0f} MB；相对基 {BASE_REF}（{base_sha[:10]}）增量 {inc / 1e6:.0f} MB')
    print('推送命令（由第一级跑，Dk 说「通过」之后；可能超过 10 分钟，要放后台跑；脚本不推）：')
    print(f'  git -C "{REPO}" -c http.postBuffer=524288000 push https://CleveLandEras@github.com/CleveLandEras/Claude.git {M}:refs/heads/main')
    print(f'  M 带完整历史（第一父是 {BASE_REF}），推到空仓库可以；之后的批以 M 为基，对新仓库是快进。')
    print(f'运行目录（日志、两边都改的文件、自检输出）：{RUN_DIR}')


def count_memory():
    n = 0
    for d in os.listdir(os.path.join(CLAUDE_DIR, 'projects')):
        src = os.path.join(CLAUDE_DIR, 'projects', d, 'memory')
        if os.path.isdir(src):
            n += count_files(src, skip_names=())[0]
    return n


try:
    main()
except Stop as e:
    print(f'\n停在这一步：{e}', flush=True)
    sys.exit(3)
PY
