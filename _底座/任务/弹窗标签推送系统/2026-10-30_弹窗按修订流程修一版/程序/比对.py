#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比对.py  改前改后比对和守卫（思考页第 7 节风险①、第 8 节第 2 项）

子命令：
  存底本 [--目录 DIR] [--重存] [--不存基线]
        把「受管文件」复制到 改前底本/修改前/（默认）并记 sha256 和时间；同时存 改前底本/已定基线.json（一致性.py 已定用）。
        已有底本时拒绝覆盖，除非 --重存。第二级在第 3 波审完改法表、开第 4 波前跑一次。
        --目录 用于试跑（不写正式底本、不存基线）。
  守卫 [--对 修改时间|修改前]
        第 4 波前跑。查有没有「不是本任务改的变动」。默认：有底本就和底本的 sha256 比，没有就和 改前底本/修改时间.txt（第 1 波前记的）比；
        第 0 步加过列的 9 个文件，按「删掉新加列后与 第0步前 逐字相同」判。有外部变动返回 1，报第一级。
  比对 [--目录 DIR]
        改后与底本比：改动块 N、落在影响项清单内 N、清单外 0；影响项每行有问题#，每个问题# 在任务文件修订记录里有一行（反过来也查）；
        第 0 步：底本里 9 个文件删掉新加列后与 第0步前 逐字相同；需求评审版_图/ 里新于底本的 jpg 都在影响项的页面内。结果同时写 本夹/比对结果.txt。

受管文件（改了要有影响项清单里的行才算数）：
  功能框架_脑图.md、需求评审版源.html、需求评审版_原型/ 下 10*、11_*、13_*、14_*、19_* 的 html，
  原夹的七张卡、功能清单、面包板、控件回指表、框架随待拍板变的节点。
影响项清单：本夹/影响项清单.md 里的表，列「问题#｜文件｜行号或控件编号｜改法#」。「行号或控件编号」可写：
  L120、L120–130、框L239（同行号）、字段编号（B1-F03，按所在卡的编号列找行）、控件编号（P4-05，按回指表／面包板行找）、页名（整页算）、留空（整个文件算）。
  文件列写文件名（带「需求评审版_原型/」之类路径前缀也行，比对时只取最后一段；「原型控件（回指表）」＝控件回指表.md＋面包板.md）。纯插入的块，算插入点前后两行。
块的比法：difflib 逐行比，连续不同的行算一块；块的行号范围取底本行和新行两套，和影响项的行号范围有重叠就算在清单内。
"""
import re, sys, shutil, hashlib, difflib, time, json, importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
BEN = HERE.parent
spec = importlib.util.spec_from_file_location('zl', HERE / '追链.py')
z = importlib.util.module_from_spec(spec); spec.loader.exec_module(z)

PROTO = z.FRAME.parent / '需求评审版_原型'
IMG = z.FRAME.parent / '需求评审版_图'
DEFAULT_DIR = BEN / '改前底本/修改前'
TASKFILE = BEN.parent / (BEN.name + '.md')


def tracked():
    out = {}
    out[z.FRAME] = '框架'
    out[z.SRC_HTML] = '源html'
    for pat in ('10*.html', '11_*.html', '13_*.html', '14_*.html', '19_*.html'):
        for f in sorted(PROTO.glob(pat)):
            out[f] = '原型'
    for k in z.CARD_KEYS:
        out[z.card_file(z.DIG, k)] = '卡与清单'
    out[z.DIG / '功能清单.md'] = '卡与清单'
    out[z.ORIG / '面包板.md'] = '卡与清单'
    out[z.ORIG / '控件回指表.md'] = '卡与清单'
    out[z.ORIG / '框架随待拍板变的节点.md'] = '卡与清单'
    return {p: g for p, g in out.items() if p and Path(p).exists()}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def opt(args, name):
    if name in args:
        i = args.index(name)
        return args[i + 1]
    return None


# ------------------------------------------------------------ 存底本
def cmd_save(args):
    d = Path(opt(args, '--目录')) if opt(args, '--目录') else DEFAULT_DIR
    trial = opt(args, '--目录') is not None
    if d.exists() and any(d.iterdir()) and '--重存' not in args:
        print('底本已存在：%s（要覆盖加 --重存）' % d); return 1
    if d.exists() and '--重存' in args:
        shutil.rmtree(d)
    lines = []
    for p, g in tracked().items():
        (d / g).mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, d / g / Path(p).name)
        lines.append('%s｜%s' % (sha(p), p))
    (d / '_sha256.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (d / '_时间.txt').write_text('%s\n%d\n' % (time.strftime('%F %T'), int(time.time())), encoding='utf-8')
    if not trial and '--不存基线' not in args:
        sp = importlib.util.spec_from_file_location('yz', HERE / '一致性.py')
        yz = importlib.util.module_from_spec(sp); sp.loader.exec_module(yz)
        print('已定基线 →', yz.save_base())
    print('已存底本 %d 个文件 → %s' % (len(lines), d))
    return 0


# ------------------------------------------------------------ 第 0 步检查
def step0_check(base_dir):
    """底本（存底本时）里 9 个文件删掉新加列后，与 第0步前 逐字相同"""
    bad, n = [], 0
    pre = z.PRE
    for old in sorted(pre.glob('*.md')):
        cand = list(Path(base_dir).glob('卡与清单/' + old.name))
        if not cand:
            bad.append('底本里没有 ' + old.name); continue
        a, b = z.rd(old), z.rd(cand[0])
        if len(a) != len(b):
            bad.append('%s 行数不同（第0步前 %d，底本 %d）' % (old.name, len(a), len(b))); continue
        card = old.name.startswith('卡')
        for i, (x, y) in enumerate(zip(a, b)):
            if x == y:
                continue
            if card:
                zz = y[4:] if y.startswith('|---') else y[2 + len(z.cells(y)[0]) + 1:]
            else:
                zz = y.rstrip()[:-1].rsplit('|', 1)[0] + '|'
            if zz != x:
                bad.append('%s 第 %d 行删列后与第0步前不同' % (old.name, i + 1))
        n += 1
    return n, bad


# ------------------------------------------------------------ 守卫
def cmd_guard(args):
    base = opt(args, '--对')
    ext = []
    if base == '修改前' or (base is None and (DEFAULT_DIR / '_sha256.txt').exists()):
        src = DEFAULT_DIR / '_sha256.txt'
        want = {}
        for l in z.rd(src):
            if '｜' in l:
                h, p = l.split('｜', 1); want[p] = h
        for p, h in want.items():
            if not Path(p).exists():
                ext.append('文件没了：' + p); continue
            if sha(p) != h:
                ext.append('变了：' + p)
        mode = '对 改前底本/修改前 的 sha256'
    else:
        want = {}
        for l in z.rd(BEN / '改前底本/修改时间.txt'):
            if l.startswith('#') or '｜' not in l:
                continue
            _, h, p = l.split('｜', 2); want[p] = h
        nine = {p.name for p in z.PRE.glob('*.md')}
        for p, h in want.items():
            if not Path(p).exists():
                ext.append('文件没了：' + p); continue
            if Path(p).name in nine and Path(p).parent.name in ('里程碑1_底稿', z.ORIG.name):
                continue
            if sha(p) != h:
                ext.append('变了：' + p)
        bad, n = step0_check_live()
        ext += ['第 0 步文件被动过：' + b for b in bad]
        mode = '对 改前底本/修改时间.txt（第 1 波前）的 sha256；9 个加列文件按「删列后同第0步前」判'
    print('守卫（%s）：不是本任务改的变动 %d 个' % (mode, len(ext)))
    for e in ext:
        print('  ', e)
    return 1 if ext else 0


def step0_check_live():
    bad, n = [], 0
    for old in sorted(z.PRE.glob('*.md')):
        cur = (z.DIG / old.name) if old.name.startswith(('卡', '功能清单')) else (z.ORIG / old.name)
        a, b = z.rd(old), z.rd(cur)
        if len(a) != len(b):
            bad.append('%s 行数不同' % old.name); continue
        card = old.name.startswith('卡')
        for i, (x, y) in enumerate(zip(a, b)):
            if x == y:
                continue
            if card:
                zz = y[4:] if y.startswith('|---') else y[2 + len(z.cells(y)[0]) + 1:]
            else:
                zz = y.rstrip()[:-1].rsplit('|', 1)[0] + '|'
            if zz != x:
                bad.append('%s 第 %d 行' % (old.name, i + 1)); break
        n += 1
    return bad, n


# ------------------------------------------------------------ 影响项清单
def parse_impact():
    p = BEN / '影响项清单.md'
    rows = []
    if not p.exists():
        return None
    for l in z.rd(p):
        if not l.startswith('|') or l.startswith('|---'):
            continue
        c = z.cells(l)
        if len(c) < 4 or c[0] in ('问题#', '问题', '#'):
            continue
        rows.append(dict(q=c[0], file=c[1], loc=c[2], fix=c[3]))
    return rows


def code_lines(code, files_now, files_base):
    """字段编号或控件编号 → [(文件名片段, 行号)]（现文件和底本各找一次）"""
    out = []
    for lines_by_file in (files_now, files_base):
        for fname, L in lines_by_file.items():
            for i, l in enumerate(L):
                if re.match(r'^\| %s \|' % re.escape(code), l):
                    out.append((fname, i + 1))
    return out


def load_lines(paths):
    return {Path(p).name: z.rd(p) for p in paths}


ALIAS = {'原型控件（回指表）': ['控件回指表.md', '面包板.md'], '原型控件(回指表)': ['控件回指表.md', '面包板.md']}


def norm_file(s):
    """文件列统一：去路径前缀（需求评审版_原型/、程序/ 等）、去空白；别名展开"""
    s = s.strip().strip('`')
    s = s.split('/')[-1].strip()
    return ALIAS.get(s, [s])


def cover_ranges(imp, now_lines, base_lines):
    """影响项 → {文件名: [(a,b) 或 'ALL']}"""
    cov = {}
    allnames = set(now_lines) | set(base_lines)
    for r in imp:
        loc = r['loc'].replace(' ', '').replace('控件', '').replace('行', '')
        fnames = []
        for fn in norm_file(r['file']):
            hit = [n for n in allnames if fn and (n == fn or fn in n)]
            fnames += hit or [fn]
        toks = [t for t in re.split(r'[、，,；;]', loc) if t]
        if not toks:
            for f in fnames:
                cov.setdefault(f, []).append('ALL')
            continue
        for t in toks:
            m = re.match(r'^(?:框|源|板)?L?(\d+)(?:[–\-~～]L?(\d+))?$', t)
            if m:
                a = int(m.group(1)); b = int(m.group(2) or a)
                for f in fnames:
                    cov.setdefault(f, []).append((a, b))
            elif re.match(r'^(?:A[1-4]|B[1-5]|C)-(?:F\d{2}|E\d+)$|^[GP]\d*-\d+[a-z]?$', t):
                for f, ln in code_lines(t, now_lines, base_lines):
                    cov.setdefault(f, []).append((ln, ln))
            else:   # 页名等：整个文件
                for f in fnames:
                    cov.setdefault(f, []).append('ALL')
    return cov


def covered(fname, a, b, cov):
    for rng in cov.get(fname, []):
        if rng == 'ALL':
            return True
        if not (b < rng[0] or a > rng[1]):
            return True
    return False


# ------------------------------------------------------------ 比对
def cmd_diff(args):
    d = Path(opt(args, '--目录')) if opt(args, '--目录') else DEFAULT_DIR
    if not (d / '_sha256.txt').exists():
        print('没有底本：先跑 存底本'); return 2
    out = []
    P = out.append
    imp = parse_impact()
    base_files = {}
    for g in ('框架', '源html', '原型', '卡与清单'):
        for f in (d / g).glob('*'):
            base_files[f.name] = f
    now_files = {Path(p).name: p for p in tracked()}
    now_lines = {n: z.rd(p) for n, p in now_files.items()}
    base_lines = {n: z.rd(p) for n, p in base_files.items()}
    cov = cover_ranges(imp, now_lines, base_lines) if imp else {}
    blocks = []
    for name in sorted(set(base_lines) | set(now_lines)):
        a = base_lines.get(name, []); b = now_lines.get(name, [])
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                continue
            # 纯插入：底本范围取插入点前后两行；纯删除：新文件范围取前后两行（插入在某行之后，算该行的影响范围）
            ba, bb = (max(i1, 1), i1 + 1) if tag == 'insert' else (i1 + 1, i2)
            na, nb = (max(j1, 1), j1 + 1) if tag == 'delete' else (j1 + 1, j2)
            blocks.append((name, ba, bb, na, nb))
    n_in = n_out = 0
    outs = []
    for (name, i1, i2, j1, j2) in blocks:
        ok = covered(name, i1, i2, cov) or covered(name, j1, j2, cov)
        if ok:
            n_in += 1
        else:
            n_out += 1; outs.append('%s 底本第 %d–%d 行／新第 %d–%d 行' % (name, i1, i2, j1, j2))
    P('== 比对（底本：%s）==' % d)
    if imp is None:
        P('影响项清单.md 还没有：所有改动块都算清单外。')
    P('改动块 %d；落在影响项清单内 %d；清单外 %d' % (len(blocks), n_in, n_out))
    for o in outs[:60]:
        P('   清单外：' + o)
    # 影响项 ↔ 修订记录
    if imp is not None:
        noq = [r for r in imp if not r['q'].strip()]
        P('影响项共 %d 行；没写问题# 的 %d 行' % (len(imp), len(noq)))
        qs = {x for r in imp for x in re.split(r'[、，,\s]+', r['q'].strip()) if x}
        rec = set()
        if TASKFILE.exists():
            on = False
            for l in z.rd(TASKFILE):
                if l.startswith('## 修订记录'):
                    on = True; continue
                if on and l.startswith('## '):
                    break
                if on and re.match(r'^\| \d+ \|', l):
                    rec.add(z.cells(l)[0])
        miss = sorted(q for q in qs if q.lstrip('#') not in {x.lstrip('#') for x in rec})
        extra = sorted(x for x in rec if x.lstrip('#') not in {q.lstrip('#') for q in qs})
        P('问题# 共 %d 个；任务文件修订记录里没有对应行的 %d 个 %s；修订记录里有、影响项清单里没有的 %d 个 %s' % (len(qs), len(miss), miss, len(extra), extra))
    else:
        P('（影响项清单、修订记录检查：待影响项清单出来后再跑）')
    # 第 0 步
    n0, bad0 = step0_check(d)
    P('第 0 步：底本里 %d 个加列文件删掉新加列后与第0步前逐字相同：%s' % (n0, '是' if not bad0 else '否 ' + '；'.join(bad0[:5])))
    # jpg
    t0 = int(z.rd(d / '_时间.txt')[1])
    newer = [f for f in sorted(IMG.glob('*.jpg')) if f.stat().st_mtime > t0]
    pages = {Path(r['file']).stem for r in (imp or [])}
    pages |= {x for r in (imp or []) for x in re.split(r'[、，,；;]', r['loc']) if re.match(r'^\d', x)}
    notin = [f.name for f in newer if not any(f.stem == pg or f.stem.startswith(pg) or pg.startswith(f.stem) for pg in pages)]
    P('需求评审版_图/ 里新于底本的 jpg %d 张；不在影响项页面内的 %d 张 %s' % (len(newer), len(notin), notin[:10]))
    txt = '\n'.join(out)
    print(txt)
    (BEN / '比对结果.txt').write_text(txt + '\n', encoding='utf-8')
    return 0 if (n_out == 0 and not bad0 and not notin) else 1


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 0
    cmd, args = argv[1], argv[2:]
    if cmd == '存底本':
        return cmd_save(args)
    if cmd == '守卫':
        return cmd_guard(args)
    if cmd == '比对':
        return cmd_diff(args)
    print(__doc__); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
