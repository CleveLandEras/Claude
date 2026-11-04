#!/bin/bash
# 装上：分角色验收上场、旧验收官退场。
# 任务 ~/claude/_底座/任务/用好Claude/2026-11-02_分角色验收上场_验收官退场.md；写法照思考页 §7.4「脚本要求」1–7。
#
# 改什么（逐处见同文件夹 改动清单.md）：
#   ~/.claude/ 下：6 个文件换成同文件夹「候选/home/dot-claude/」里的版本；新建 2 个（agents/总验收人.md、skills/验收考试/SKILL.md）；
#                 移走 2 处（agents/验收官.md、skills/验收官考试/，移进备份夹，不删）。
#   ~/claude/ 下：19 个文件按「候选/替换对.json」逐句替换；_底座/全局规则_快照.md 换成新的全局规则；新建 _底座/工具/README.md。
#   不碰 ~/.claude/settings.json（钩子文件名不变，不用重新登记）。
#
# 用法：
#   bash 装上.sh                      预览：逐个文件打印改前改后的差异，不改任何文件
#   bash 装上.sh --执行               先做完全部检查，任一不过就一个文件都不改；都过了先备份、再改、改完逐个核
#   bash 装上.sh --撤回 <备份夹>       把备份拷回去、删掉新建的文件
#   bash 装上.sh --根 <目录> ...      只供测试：把 ~ 换成 <目录>
#   bash 装上.sh --算sha              候选改过以后，打印要抄回脚本「写死的值」的新 sha256（不改任何文件）
D="$(cd "$(dirname "$0")" && pwd -P)"
exec /usr/bin/python3 -I - "$D" "$@" <<'PY'
import datetime, difflib, hashlib, json, os, shutil, sys

HERE, ARGS = sys.argv[1], sys.argv[2:]
SCRIPT = os.path.join(HERE, '装上.sh')

# ---------- 写死的值（11/03 现取；改了候选就跑 --算sha 重取，并同步 候选/A类清单.json）----------
SHA_替换对 = '043c986f72fc4dcc75fce36d8e72b5391524120b77ab188dbf806025bfc17575'
# A 类：目标（相对 ~）｜动作｜改前整份 sha256（文件夹＝里面唯一的 SKILL.md）｜候选（相对本文件夹）｜候选 sha256
A = [
    ('.claude/CLAUDE.md', '改',
     'd35780b74795bd86a1c64113d38eb64acf61ca75193387c84b64e667ffc74171',
     '候选/home/dot-claude/CLAUDE.md', 'f3f17ff40c39e0eeab98112d1d51ac1d4be1bb79979c1816ac536655c8af99a0'),
    ('.claude/agents/验收官.md', '移走',
     '69208dfc8bb5836cf41ac925eb46dd9afbb5fc752d0dda0b37ca643401b91de1', None, None),
    ('.claude/agents/总验收人.md', '新建', None,
     '候选/home/dot-claude/agents/总验收人.md', '6e35cda8dde69aa5dc59368b2f35f3bc063bdf6bade6baf2c32d0d468b15f886'),
    ('.claude/agents/流程抽查员.md', '改',
     '7772248c245f77ea2c85cea382a8c95eb375d11ad581e61d0d3c4715084e36da',
     '候选/home/dot-claude/agents/流程抽查员.md', '67a0a2c0cba68671786e4db7b8bc9146804387dccc53ed4de7f0edbe8dcccb6e'),
    ('.claude/skills/开工/SKILL.md', '改',
     '2718109e0f7e0b5249bb2693eeb57b49d5246b05e0974a987847478015f52b01',
     '候选/home/dot-claude/skills/开工/SKILL.md', '71b191a808d0b3d8d487a6da668e594ecf59e63ec75c2292943c9773e9627b1c'),
    ('.claude/skills/整理纠正/SKILL.md', '改',
     'b03d1d4d1658c4e57e3b04d1ab62c8d32a69c4b68eb7fc1b39ddd134b42fce12',
     '候选/home/dot-claude/skills/整理纠正/SKILL.md', '5ff5f5a4c850c3f452cbd9cd17bd935e96dc0f175c13e0258262ffa0c4d845bf'),
    ('.claude/skills/验收官考试', '移走',
     '2be9428b9af0331f60f64bd8db3838928f488d1c27aee441040f25ce7c5411bc', None, None),
    ('.claude/skills/验收考试/SKILL.md', '新建', None,
     '候选/home/dot-claude/skills/验收考试/SKILL.md', '7e601d2dccff61f87394aa37c37717f3a46899aeda45e0f8897ae96e9e0adba5'),
    ('.claude/hooks/delivery_gate.py', '改',
     'bcd10b439d2d8cc9a0c6f1c4a865f1697acf10c37a134a8e79a7842299f0a3b5',
     '候选/home/dot-claude/hooks/delivery_gate.py', '5e139082eb1cfed1984cb5137a77e3862ca65ab2610f63fb669bbf2a927a3f23'),
    ('.claude/hooks/correction_capture.py', '改',
     'fa05e659f9a8e9c1dc0c05c5cf9c1bca6bbe51515ab2a5f354001deeb915fc37',
     '候选/home/dot-claude/hooks/correction_capture.py', '6d4840d13b41a2af77727643e7cbc45d8c2fdf913cb231343754ab9294ea8500'),
]
NEW_BC = {'候选/claude/_底座/工具/README.md': '5f7731aeff01f0706867921f3990a52b0f72769394404d444c60c2126afaa439'}
GLOBAL = '.claude/CLAUDE.md'
SNAPSHOT = 'claude/_底座/全局规则_快照.md'   # 整份换成新的全局规则；改前要和旧全局规则逐字节相同
SETTINGS = '.claude/settings.json'          # 只核它前后没变
MANIFEST = '装上记录.json'


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
        print(f'{name} 后面要跟一个目录')
        sys.exit(2)
    return ARGS[i + 1]


UNDO_ARG, ROOT_ARG = flag_value('--撤回'), flag_value('--根')
for a in ARGS:
    if a.startswith('--') and a not in ('--执行', '--撤回', '--根', '--算sha'):
        print(f'不认识的参数：{a}')
        sys.exit(2)
DO = '--执行' in ARGS
if DO and UNDO_ARG:
    print('--执行 和 --撤回 不能一起用')
    sys.exit(2)
ROOT = os.path.abspath(os.path.expanduser(ROOT_ARG or '~'))


def T(rel):            # 目标的真实路径
    return os.path.join(ROOT, rel)


def S(rel):            # 打印用
    return '~/' + rel


def B(rel):            # 备份夹里的相对路径：.claude 记作 dot-claude，免得备份里的说明和技能被当成现行的加载
    return 'dot-claude/' + rel[len('.claude/'):] if rel.startswith('.claude/') else rel


def files_under(d):
    out = []
    for r, _ds, fs in os.walk(d):
        for f in fs:
            out.append(os.path.relpath(os.path.join(r, f), d))
    return sorted(out)


def undo_cmd(bk):
    extra = f' --根 {ROOT}' if ROOT_ARG else ''
    return f'bash {SCRIPT} --撤回 {bk}{extra}'


# ---------- --算sha ----------
if '--算sha' in ARGS:
    rows = [(c, s) for (_t, _a, _p, c, s) in A if c] + list(NEW_BC.items()) + [('候选/替换对.json', SHA_替换对)]
    for c, s in rows:
        p = os.path.join(HERE, c)
        now = sha(read(p)) if os.path.isfile(p) else '（不在）'
        print(f'{"同" if now == s else "变"}  {now}  {c}')
    print('「变」的那几行，把新值抄回脚本「写死的值」和 候选/A类清单.json；没改任何文件')
    sys.exit(0)


# ---------- --撤回 ----------
def undo():
    bk = os.path.abspath(os.path.expanduser(UNDO_ARG))
    mp = os.path.join(bk, MANIFEST)
    if not os.path.isfile(mp):
        print(f'备份夹里没有 {MANIFEST}：{bk}')
        print('有问题，没改任何文件')
        sys.exit(1)
    man = json.load(open(mp, encoding='utf-8'))
    if os.path.abspath(man['根']) != ROOT:
        print(f'这个备份是在 {man["根"]} 下装的，现在的根是 {ROOT}；要撤回请加 --根 {man["根"]}')
        print('有问题，没改任何文件')
        sys.exit(1)
    bad = []
    for it in man['项']:
        if it['动作'] in ('改', '移走'):
            src = os.path.join(bk, it['备份'])
            if it.get('文件夹'):
                ok = os.path.isdir(src) and files_under(src) == ['SKILL.md'] \
                    and sha(read(os.path.join(src, 'SKILL.md'))) == it['改前sha']
            else:
                ok = os.path.isfile(src) and sha(read(src)) == it['改前sha']
            if not ok:
                bad.append(f'备份里的 {it["备份"]} 不在或和装上前的不一样')
    if bad:
        for b in bad:
            print('不过：' + b)
        print('有问题，没改任何文件')
        sys.exit(1)

    save = os.path.join(bk, '撤回前_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    saved, n_back, n_del, n_mv = [], 0, 0, 0

    def keep(rel, p):      # 装上之后又被改过的，先另存一份再覆盖
        dst = os.path.join(save, B(rel))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        (shutil.copytree if os.path.isdir(p) else shutil.copy2)(p, dst)
        saved.append(S(rel))

    for it in man['项']:
        rel, p = it['目标'], T(it['目标'])
        src = os.path.join(bk, it['备份']) if it.get('备份') else None
        if it['动作'] == '改':
            if os.path.isfile(p) and sha(read(p)) == it['改前sha']:
                continue
            if os.path.exists(p) and (not os.path.isfile(p) or sha(read(p)) != it['改后sha']):
                keep(rel, p)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            shutil.copy2(src, p)
            n_back += 1
        elif it['动作'] == '新建':
            if os.path.isfile(p):
                if sha(read(p)) != it['改后sha']:
                    keep(rel, p)
                os.remove(p)
                n_del += 1
            for d in reversed(it.get('新建的文件夹', [])):
                dp = T(d)
                if os.path.isdir(dp) and not os.listdir(dp):
                    os.rmdir(dp)
        elif it['动作'] == '移走':
            if it.get('文件夹'):
                if os.path.isdir(p) and files_under(p) == ['SKILL.md'] \
                        and sha(read(os.path.join(p, 'SKILL.md'))) == it['改前sha']:
                    continue
                if os.path.exists(p):
                    keep(rel, p)
                    shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
                shutil.copytree(src, p)
            else:
                if os.path.isfile(p) and sha(read(p)) == it['改前sha']:
                    continue
                if os.path.exists(p):
                    keep(rel, p)
                    os.remove(p)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                shutil.copy2(src, p)
            n_mv += 1
    # 撤回后核：改过的、移走的都等于装上前；新建的都不在了
    bad = []
    for it in man['项']:
        p = T(it['目标'])
        if it['动作'] == '新建':
            if os.path.exists(p):
                bad.append(f'{S(it["目标"])} 还在')
        elif it.get('文件夹'):
            if not (os.path.isdir(p) and sha(read(os.path.join(p, 'SKILL.md'))) == it['改前sha']):
                bad.append(f'{S(it["目标"])} 没恢复')
        elif not (os.path.isfile(p) and sha(read(p)) == it['改前sha']):
            bad.append(f'{S(it["目标"])} 没恢复')
    for b in bad:
        print('核对不过：' + b)
    if saved:
        print(f'这 {len(saved)} 个在装上之后又被改过，覆盖前另存在 {save}：' + '、'.join(saved))
    if bad:
        sys.exit(1)
    print(f'已撤回：恢复 {n_back} 个、删掉新建的 {n_del} 个、移回 {n_mv} 处；备份夹留着：{bk}')


if UNDO_ARG:
    undo()
    sys.exit(0)


# ---------- 检查，算出每个文件改后的样子（预览和 --执行 共用）----------
problems, plan = [], []    # plan 项：dict(rel, 动作, old, new, pre, 文件夹)


def cand(rel_c, want):
    p = os.path.join(HERE, rel_c)
    if not os.path.isfile(p):
        problems.append(f'候选不在：{rel_c}')
        return None
    b = read(p)
    if sha(b) != want:
        problems.append(f'候选 {rel_c} 的 sha256 和脚本里写死的不一致（候选在脚本写好后被改过）')
    return b


# A 类清单.json 要和这里写死的一致（两边是同一份数，防止只改了一边）
try:
    aj = json.load(open(os.path.join(HERE, '候选/A类清单.json'), encoding='utf-8'))
    jmap = {it['目标'][2:].rstrip('/'): it for it in aj}
    for rel, act, pre, c, cs in A:
        it = jmap.get(rel)
        if not it or it['动作'] != act or it['改前sha256'] != pre or it.get('候选') != c or it.get('候选sha256') != cs:
            problems.append(f'候选/A类清单.json 里 {S(rel)} 那一项和脚本里写死的不一致')
    if len(jmap) != len(A):
        problems.append('候选/A类清单.json 的项数和脚本里写死的不一致')
except Exception as e:
    problems.append(f'读不了 候选/A类清单.json：{e}')

cand_global = None
for rel, act, pre, c, cs in A:
    p = T(rel)
    if act == '改':
        nb = cand(c, cs)
        if rel == GLOBAL:
            cand_global = nb
        if not os.path.isfile(p):
            problems.append(f'A 类 {S(rel)} 不在')
            continue
        ob = read(p)
        if sha(ob) != pre:
            problems.append(f'A 类 {S(rel)} 在脚本写好之后被改过（整份 sha256 对不上）')
        plan.append(dict(rel=rel, 动作='改', old=ob, new=nb, pre=pre))
    elif act == '新建':
        nb = cand(c, cs)
        if os.path.exists(p):
            problems.append(f'要新建的 {S(rel)} 已经存在')
        plan.append(dict(rel=rel, 动作='新建', old=None, new=nb, pre=None))
    elif act == '移走':
        if os.path.isdir(p):
            fs = files_under(p)
            if fs != ['SKILL.md']:
                problems.append(f'A 类 {S(rel)}/ 里的文件变了：{fs}')
            elif sha(read(os.path.join(p, 'SKILL.md'))) != pre:
                problems.append(f'A 类 {S(rel)}/SKILL.md 在脚本写好之后被改过（整份 sha256 对不上）')
            plan.append(dict(rel=rel, 动作='移走', old=None, new=None, pre=pre, 文件夹=True))
        elif os.path.isfile(p):
            if sha(read(p)) != pre:
                problems.append(f'A 类 {S(rel)} 在脚本写好之后被改过（整份 sha256 对不上）')
            plan.append(dict(rel=rel, 动作='移走', old=None, new=None, pre=pre))
        else:
            problems.append(f'要移走的 {S(rel)} 不在')

# B、C 类
pairs = []
try:
    jb = read(os.path.join(HERE, '候选/替换对.json'))
    if sha(jb) != SHA_替换对:
        problems.append('候选/替换对.json 的 sha256 和脚本里写死的不一致（脚本写好后被改过）')
    pairs = json.loads(jb.decode('utf-8'))
except Exception as e:
    problems.append(f'读不了 候选/替换对.json：{e}')

order, texts, origs = [], {}, {}
for n, it in enumerate(pairs, 1):
    t = it.get('目标', '')
    if not t.startswith('~/'):
        problems.append(f'替换对第 {n} 项的目标不是 ~/ 开头：{t}')
        continue
    rel = t[2:]
    act = it.get('动作', '替换')
    if '原句' in it:
        p = T(rel)
        if rel not in origs:
            if not os.path.isfile(p):
                problems.append(f'第 {n} 项：{S(rel)} 不在')
                origs[rel] = None
                continue
            origs[rel] = read(p).decode('utf-8')
            texts[rel] = origs[rel]
            order.append(rel)
        if origs[rel] is None:
            continue
        c0 = origs[rel].count(it['原句'])
        c1 = texts[rel].count(it['原句'])
        if c0 != 1:
            problems.append(f'第 {n} 项（改动清单第 {it.get("改动清单行")} 行）：原句在 {S(rel)} 里出现 {c0} 次，要恰好 1 次')
        elif c1 != 1:
            problems.append(f'第 {n} 项：依次替换到这一项时，原句在 {S(rel)} 里出现 {c1} 次')
        else:
            texts[rel] = texts[rel].replace(it['原句'], it['新句'], 1)
    elif act == '复制候选 CLAUDE.md':
        if rel != SNAPSHOT:
            problems.append(f'第 {n} 项：复制候选 CLAUDE.md 的目标不是全局规则快照：{t}')
            continue
        p = T(rel)
        if not os.path.isfile(p):
            problems.append(f'{S(rel)} 不在')
            continue
        ob = read(p)
        if sha(ob) != A[0][2]:
            problems.append(f'{S(rel)} 现在和装上前的全局规则不是逐字节相同（脚本写好之后被改过）')
        plan_snap = dict(rel=rel, 动作='改', old=ob, new=None, pre=sha(ob), 快照=True)
        order.append(plan_snap)
    elif act == '新建':
        c = it.get('候选')
        if c not in NEW_BC:
            problems.append(f'第 {n} 项：新建的候选 {c} 不在脚本写死的值里')
            continue
        nb = cand(c, NEW_BC[c])
        if os.path.exists(T(rel)):
            problems.append(f'要新建的 {S(rel)} 已经存在')
        order.append(dict(rel=rel, 动作='新建', old=None, new=nb, pre=None))
    else:
        problems.append(f'第 {n} 项：不认识的动作 {act}')

for x in order:
    if isinstance(x, str):
        plan.append(dict(rel=x, 动作='改', old=origs[x].encode('utf-8'), new=texts[x].encode('utf-8'),
                         pre=sha(origs[x].encode('utf-8'))))
    else:
        if x.get('快照'):
            x['new'] = cand_global
        plan.append(x)

rels = [x['rel'] for x in plan]
if len(set(rels)) != len(rels):
    problems.append('同一个文件出现在两处改动里')
if any(r == SETTINGS or r.endswith('/settings.json') for r in rels):
    problems.append('改动里有 settings.json，不该碰')
for x in plan:
    if x['动作'] in ('改', '新建') and x['new'] is None:
        problems.append(f'{S(x["rel"])} 算不出改后的内容')

n_mod = sum(x['动作'] == '改' for x in plan)
n_new = sum(x['动作'] == '新建' for x in plan)
n_mv = sum(x['动作'] == '移走' for x in plan)
if ROOT_ARG:
    print(f'（测试：~ 换成 {ROOT}）')

# ---------- 预览 ----------
if not DO:
    for x in plan:
        if x['动作'] == '移走':
            print(f'=== 移走 {S(x["rel"])}{"/" if x.get("文件夹") else ""} → 备份夹（不删）')
            continue
        print(f'=== {x["动作"]} {S(x["rel"])}')
        if x['new'] is None:
            continue
        a = x['old'].decode('utf-8').splitlines(keepends=True) if x['old'] is not None else []
        b = x['new'].decode('utf-8').splitlines(keepends=True)
        for line in difflib.unified_diff(a, b, '改前', '改后', n=1):
            sys.stdout.write(line if line.endswith('\n') else line + '\n')
    if problems:
        print(f'检查：有 {len(problems)} 处不过，加 --执行 会整个停下：')
        for pr in problems:
            print('  不过：' + pr)
    else:
        print('检查：全部通过')
    print(f'预览：要改 {n_mod} 个文件、新建 {n_new} 个、移走 {n_mv} 处；没改任何文件')
    sys.exit(0)

# ---------- 执行 ----------
if problems:
    for pr in problems:
        print('不过：' + pr)
    print('有问题，没改任何文件')
    sys.exit(1)

stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
bk = T(f'.claude/backups/验收官退场_{stamp}')
k = 2
while os.path.exists(bk):
    bk = T(f'.claude/backups/验收官退场_{stamp}_{k}')
    k += 1
sp = T(SETTINGS)
settings_before = sha(read(sp)) if os.path.isfile(sp) else None

try:
    # 1. 备份：要改的原样复制，要移走的稍后整个移进来；先写装上记录，撤回靠它
    os.makedirs(bk)
    items = []
    for x in plan:
        it = dict(目标=x['rel'], 动作=x['动作'], 改前sha=x['pre'],
                  改后sha=sha(x['new']) if x['new'] is not None else None)
        if x['动作'] in ('改', '移走'):
            it['备份'] = B(x['rel'])
        if x.get('文件夹'):
            it['文件夹'] = True
        if x['动作'] == '新建':
            dirs, d = [], os.path.dirname(x['rel'])
            while d and not os.path.isdir(T(d)):
                dirs.insert(0, d)
                d = os.path.dirname(d)
            it['新建的文件夹'] = dirs
        items.append(it)
        if x['动作'] == '改':
            dst = os.path.join(bk, B(x['rel']))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(T(x['rel']), dst)
            if sha(read(dst)) != x['pre']:
                raise RuntimeError(f'备份 {S(x["rel"])} 后核对不一致（检查之后被改过）')
    with open(os.path.join(bk, MANIFEST), 'w', encoding='utf-8') as f:
        json.dump(dict(根=ROOT, 时间=stamp, 脚本=SCRIPT, 项=items), f, ensure_ascii=False, indent=1)
    # 2. 移走
    for x in plan:
        if x['动作'] == '移走':
            dst = os.path.join(bk, B(x['rel']))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(T(x['rel']), dst)
    # 3. 改、新建（先写临时文件再换上）
    for x in plan:
        if x['动作'] not in ('改', '新建'):
            continue
        p = T(x['rel'])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + '.装上中'
        with open(tmp, 'wb') as f:
            f.write(x['new'])
        if x['动作'] == '改':
            shutil.copymode(p, tmp)
        os.replace(tmp, p)
except Exception as e:
    print(f'中途出错：{e}')
    print(f'已动过的可以撤回：{undo_cmd(bk)}')
    sys.exit(1)

# 4. 改完逐个核
bad = []
for x in plan:
    p = T(x['rel'])
    if x['动作'] in ('改', '新建'):
        if not os.path.isfile(p) or sha(read(p)) != sha(x['new']):
            bad.append(f'{S(x["rel"])} 改后的 sha256 和预期不一致')
    else:
        dst = os.path.join(bk, B(x['rel']))
        got = os.path.join(dst, 'SKILL.md') if x.get('文件夹') else dst
        if os.path.exists(p) or not os.path.isfile(got) or sha(read(got)) != x['pre']:
            bad.append(f'{S(x["rel"])} 没移进备份夹')
if (sha(read(sp)) if os.path.isfile(sp) else None) != settings_before:
    bad.append('settings.json 变了')
if bad:
    for b in bad:
        print('核对不过：' + b)
    print(f'撤回：{undo_cmd(bk)}')
    sys.exit(1)
print(f'已执行：改 {n_mod} 个、新建 {n_new} 个、移走 {n_mv} 处，备份在 {bk}；撤回：{undo_cmd(bk)}')
PY
