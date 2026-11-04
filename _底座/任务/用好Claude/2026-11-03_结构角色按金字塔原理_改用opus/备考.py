#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""备考：结构角色单考出考试材料（任务 2026-11-03_结构角色按金字塔原理_改用opus，思考页第 7 节 M2-3 加第 10 节）。

用法（用系统自带的 python3，不加 -I，否则读不了 pptx）：
  /usr/bin/python3 备考.py --组 甲            出甲组 7 份（现行说明，对照组）
  /usr/bin/python3 备考.py --组 乙            出乙组 7 份（候选说明 T/候选/结构.md）；先在 /private/tmp/结构考_1103_方法乙/ 建候选方法目录
  --试跑     材料和方法目录都放进草稿目录，不动 /private/tmp/分角色验收/ 下的正式夹，也不写 派活表.txt（调试脚本用）
  --重出     正式夹已有、派活表里有已派出的行时，也删了重出（只有第二级能决定）

做的事（按顺序，任何一步不过就停，返回码不为 0）：
  1. 核指纹：1102 试卷第 10.3、10.4 节里题54–57、样1 的五张卡和原稿；题58、59 的卡、当时摘录、当时清单、成品
     （成品对 来源.md 里的 sha256；卡和摘录对本脚本里钉死的 sha256）。甲组还核现行 角色/结构.md 是不是对照组那一版。
  2. 出 7 份材料：用 备评审材料.py 的 build()，输出根 /private/tmp/分角色验收/结构考_1103_<甲|乙>。
     题58、59 出完后，用 试卷_卡/ 下的「当时摘录」覆盖 对齐卡摘录.md，「当时清单」覆盖 验收清单原文.md。
  3. 核材料：每份打印「已剔除 N 句」（N 不是 0 就列出剔了什么）；除 成品/ 外 HARD_RE 0 命中；
     派活/结构.md 填值后和模板一致；派活里引用的材料夹路径都在；题58、59 摘录里的读者、可用时间和派活里的一致。
  4. 甲、乙两组都已出时，逐文件对照（除 派活/结构.md 外只许差材料夹路径）。
  5. 写 派活表.txt：每题一行「题|组|1|待派|材料夹路径」。第 2 轮由第二级派考时自己加行。
"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import re
import shutil
import sys
from pathlib import Path

B = Path('/Users/decheng.huang/claude/_底座')
T = B / '任务/用好Claude/2026-11-03_结构角色按金字塔原理_改用opus'
K1102 = B / '任务/用好Claude/2026-11-02_分角色验收上场_验收官退场/试卷_卡'
SHI1102 = B / '任务/用好Claude/2026-11-02_分角色验收上场_验收官退场/试卷.md'
KA = T / '试卷_卡'
O = B / '考试/原稿'
O7 = O / '2026-11-03_结构单考_弹窗场景第7版'
W = B / '任务/弹窗标签推送系统/2026-11-02_弹窗汇报给主管'
OUT = Path('/private/tmp/分角色验收')
METHOD_B = Path('/private/tmp/结构考_1103_方法乙')
CAND = T / '候选/结构.md'
TABLE = T / '派活表.txt'
SCRATCH = Path('/private/tmp/claude-502/-Users-decheng-huang-claude/a8ab360d-c0c4-4713-b657-6c0dba95ac78/scratchpad/备考试跑')

# 对照组（甲）用的现行 结构.md；换成别的就不再是对照组
CURRENT_JIEGOU_SHA = 'a2bf14330e537d4fea560fb86812279806436c5c5c197f0d2254b99c5fd74f83'
# 题58、59 的输入，11/03 11:10 前后第二级核过、复制好的那一版
PINS = {
    '卡_题58_弹窗第7版_还原.md': '00bcb64f3eb910279ad1698ef3a65758cfb78625e5f1060ae9b2d097a503283c',
    '卡_题59_场景第7版.md': 'ea9cb0d298490c0282373706f236a1be17916bfb91245ed383bca9a8e17ab421',
    '当时摘录_题58_弹窗.md': 'f17ac3a56072772142ff03997687b2e6044015ee1f6a5119c5a5cd2939e7f165',
    '当时摘录_题59_场景.md': 'eb1d07b72656b4b8f051d925bba8fe1f20206d75c09b48d1cfc2fccac388bbc0',
    '当时清单_题58_弹窗.md': 'e90540d89e43dcb625ef12a77b9b249c44312010c068bb51b3dea3af1b80bad5',
    '当时清单_题59_场景.md': 'e90540d89e43dcb625ef12a77b9b249c44312010c068bb51b3dea3af1b80bad5',
}

THIS = '推送统一后台（弹窗、推播、标签）的产品设计：这是给主管汇报其中一块的材料（范围以对齐卡摘录为准）'
OTHER = '商城的活动配置工具、竞品跟踪、用好 Claude 的工作方式、团队工作模式这几个项目里的事'

# (题号, 卡, 成品, 读者称呼, 当时摘录, 当时清单)
PAPERS = [
    ('54', K1102 / '卡_题54_弹窗5页版.md', [O / '2026-11-02_分角色验收考试/弹窗_5页版_全文.txt'], '主管', None, None),
    ('55', K1102 / '卡_题55_场景1955版.md', [O / '2026-11-02_分角色验收考试/场景_1955版'], '主管', None, None),
    ('56', K1102 / '卡_题56_推播纯表格.md',
     [W / 'Dk退回_1102_2240_纯表格/推播汇报_给主管.pptx', W / 'Dk退回_1102_2240_纯表格/推播汇报_给主管_s01.jpg'], '主管', None, None),
    ('57', K1102 / '卡_题57_脑图2107.md', [W / 'Dk退回_1102_2250_脑图平铺/功能清单_两份汇报_脑图_2107.md'], 'Dk', None, None),
    ('样1', K1102 / '卡_样1_样本一.md',
     [O / '2026-10-30_弹窗内容去留三件改是否跳转/弹窗内容去留_修订1029.pptx', O / '2026-10-30_弹窗内容去留_修订1029_渲染图'], 'Dk', None, None),
    ('58', KA / '卡_题58_弹窗第7版_还原.md',
     [O7 / '弹窗/弹窗功能设计汇报_发给主管版.pptx', O7 / '弹窗/s01.jpg'], '主管',
     KA / '当时摘录_题58_弹窗.md', KA / '当时清单_题58_弹窗.md'),
    ('59', KA / '卡_题59_场景第7版.md',
     [O7 / '场景/弹窗规则_先分场景还是先按人群_发给主管版.pptx', O7 / '场景/s01.jpg'], '主管',
     KA / '当时摘录_题59_场景.md', KA / '当时清单_题59_场景.md'),
]


def label(no):
    return '样1' if no == '样1' else '题' + no


def sha(p):
    h = hashlib.sha256()
    if Path(p).is_dir():
        for q in sorted(Path(p).rglob('*')):
            if q.is_file():
                h.update(str(q.relative_to(p)).encode('utf-8'))
                h.update(q.read_bytes())
    else:
        h.update(Path(p).read_bytes())
    return h.hexdigest()


def load_beiliao():
    spec = importlib.util.spec_from_file_location('beiliao', B / '工具/备评审材料.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Halt(Exception):
    pass


# ---------- 1. 核指纹 ----------

def check_fingerprints(arm):
    bad = []
    n = 0

    def one(p, want, name):
        nonlocal n
        n += 1
        if not Path(p).exists():
            bad.append('%s 不存在' % name)
        elif sha(p) != want:
            bad.append('%s 的 sha256 变了（现在 %s…，应为 %s…）' % (name, sha(p)[:16], want[:16]))

    # 1102 试卷第 10.3、10.4 节：题54–57、样1 的卡和原稿（题29 与 5 号稿不在这次卷面里）
    sec = None
    for line in SHI1102.read_text(encoding='utf-8').split('\n'):
        if line.startswith('### 10.3'):
            sec = 'card'
        elif line.startswith('### 10.4'):
            sec = 'orig'
        elif line.startswith('### 10.5') or line.startswith('## 11'):
            sec = None
        if not sec or not line.startswith('| '):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 2 or not re.fullmatch(r'`[0-9a-f]{64}`', cells[1]):
            continue
        want = cells[1].strip('`')
        if sec == 'card':
            f = cells[0].strip('`')
            if '题29' in f:
                continue
            one(K1102 / f, want, '卡 ' + f)
        else:
            if cells[0].startswith('5 号'):
                continue
            rel = re.search(r'`(.+)`', cells[0]).group(1)
            one(B.parent / rel, want, '原稿 ' + rel)
    # 题58、59：卡、当时摘录、当时清单
    for f, want in PINS.items():
        one(KA / f, want, '试卷_卡/' + f)
    # 题58、59 成品：对 来源.md 里的 sha256
    src = (O7 / '来源.md').read_text(encoding='utf-8')
    table = {}
    for line in src.split('\n'):
        m = re.match(r'^\| `([^`]+)` \| `[^`]+` \| [^|]+ \| `([0-9a-f]{64})` \|', line)
        if m:
            table[m.group(1)] = m.group(2)
    for no, _c, prods, _call, _x, _y in PAPERS:
        if no in ('58', '59'):
            for p in prods:
                rel = str(p.relative_to(O7))
                if rel not in table:
                    bad.append('来源.md 里没有 %s' % rel)
                else:
                    one(p, table[rel], '成品 ' + rel)
    if arm == '甲':
        one(B / '分角色验收/角色/结构.md', CURRENT_JIEGOU_SHA, '现行 角色/结构.md（甲组对照）')
    if bad:
        raise Halt('指纹不一致，停：\n  ' + '\n  '.join(bad))
    print('指纹：核了 %d 项，全部一致' % n)


# ---------- 方法目录 ----------

def method_dir_for(arm, m, scratch):
    if arm == '甲':
        return m.METHOD_DIR
    d = (SCRATCH / '方法乙') if scratch else METHOD_B
    if d.exists():
        shutil.rmtree(d)
    (d / '角色').mkdir(parents=True)
    shutil.copy2(m.METHOD_DIR / '总验收人说明.md', d / '总验收人说明.md')
    for r in m.ROLES:
        src = CAND if r == '结构' else (m.METHOD_DIR / '角色' / (r + '.md'))
        shutil.copy2(src, d / '角色' / (r + '.md'))
    cur = (m.METHOD_DIR / '角色/结构.md').read_text(encoding='utf-8')
    cand = CAND.read_text(encoding='utf-8')
    ph = lambda t: sorted(set(re.findall(r'\{[^{}\s]{1,8}\}', t)))
    if ph(cur) != ph(cand):
        raise Halt('候选和现行 结构.md 的占位符不一样：%s / %s' % (ph(cand), ph(cur)))
    if cand.count('{') != len(re.findall(r'\{[^{}\s]{1,8}\}', cand)) or cand.count('}') != cand.count('{'):
        raise Halt('候选里除占位符外还有花括号')
    return d


# ---------- 2. 出材料 ----------

def build_one(m, arm, no, card, prods, call, mdir, root):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            final = m.build(card, prods, out_root=root, exam=no, call=call,
                            this_proj=THIS, other_proj=OTHER, method_dir=mdir)
        except m.Stop as e:
            print(str(e))
            raise Halt('%s 出材料失败（返回码 %s）：\n%s' % (label(no), e.code, buf.getvalue()))
    log = buf.getvalue()
    mm = re.search(r'已剔除 (\d+) 句', log)
    n = int(mm.group(1)) if mm else -1
    removed = [l.strip() for l in log.split('\n') if l.strip().startswith('剔：')]
    warns = [l for l in log.split('\n') if l.startswith('警告') or l.startswith('提示')]
    return final, n, removed, warns


def overwrite_stable(final, 摘录, 清单):
    shutil.copyfile(摘录, final / '对齐卡摘录.md')
    shutil.copyfile(清单, final / '验收清单原文.md')


# ---------- 3. 核材料 ----------

def field_of(text, name):
    m = re.search(r'^- \*\*%s[^*]*\*\*\s*[:：]\s*(.*)$' % name, text, re.M)
    return m.group(1).strip() if m else ''


def check_one(m, arm, no, final, mdir, 摘录, root):
    res = []
    hit_all = []
    for p in sorted(final.rglob('*')):
        if not p.is_file() or not m.is_text(p):
            continue
        rel = p.relative_to(final)
        if rel.parts[0] == '成品':
            continue
        hard, warn = m.scan_text(p.read_text(encoding='utf-8'))
        for ln, w in hard:
            hit_all.append('%s 第 %d 行「%s」' % (rel, ln, w))
        for ln, w in warn:
            res.append('警告词：%s 第 %d 行「%s」' % (rel, ln, w))
    if hit_all:
        raise Halt('%s 除成品外 HARD_RE 有命中：%s' % (label(no), '；'.join(hit_all)))
    res.append('HARD_RE 除成品外 0 命中')
    # 派活/结构.md = 模板填值
    tpl = (Path(mdir) / '角色/结构.md').read_text(encoding='utf-8')
    filled = (final / '派活/结构.md').read_text(encoding='utf-8')
    parts = re.split(r'\{[^{}\s]{1,8}\}', tpl)
    rx = '(?:.*?)'.join(re.escape(p) for p in parts)
    if not re.fullmatch(rx, filled, re.S):
        raise Halt('%s 派活/结构.md 去掉填进去的值后和 %s 不一致' % (label(no), '候选' if arm == '乙' else '现行结构.md'))
    res.append('派活/结构.md 去掉填值后和%s逐句一致' % ('候选' if arm == '乙' else '现行结构.md'))
    # 派活里的路径
    paths = set()
    for p in (final / '派活').glob('*.md'):
        for x in re.findall(re.escape(str(root)) + r'[^\s（）()`「」，、；。]+', p.read_text(encoding='utf-8')):
            paths.add(x.rstrip('/'))
    miss = sorted(x for x in paths if not Path(x).exists())
    if miss:
        raise Halt('%s 派活里引用的路径不存在：%s' % (label(no), miss))
    res.append('派活里引用的 %d 个路径都在' % len(paths))
    # 题58、59：摘录里的读者、可用时间 和派活里的一致
    if 摘录 is not None:
        t = 摘录.read_text(encoding='utf-8')
        want_reader = field_of(t, '读者').rstrip('。 ')
        want_when = field_of(t, '可用时间').rstrip('。 ') or '卡上没写可用时间'
        got_reader = re.search(r'^读者：(.*)$', filled, re.M).group(1).strip()
        got_when = re.search(r'^可用时间：(.*)$', filled, re.M).group(1).strip()
        if want_reader != got_reader or want_when != got_when:
            res.append('警告：摘录和派活的读者／可用时间不一致：摘录「%s」「%s」，派活「%s」「%s」'
                       % (want_reader, want_when, got_reader, got_when))
        else:
            res.append('摘录和派活里的读者、可用时间一致')
        if sha(final / '对齐卡摘录.md') != sha(摘录):
            raise Halt('%s 对齐卡摘录.md 没换成当时摘录' % label(no))
    return res


# ---------- 4. 甲乙对照 ----------

def norm(text, folder):
    return text.replace(str(folder), '<材料夹>')


def compare_arms(roots):
    out = []
    for no, *_ in PAPERS:
        a, b = roots['甲'].get(no), roots['乙'].get(no)
        if not a or not b:
            continue
        fa = {str(p.relative_to(a)): p for p in a.rglob('*') if p.is_file()}
        fb = {str(p.relative_to(b)): p for p in b.rglob('*') if p.is_file()}
        diff = []
        if set(fa) != set(fb):
            diff.append('文件清单不同：%s' % sorted(set(fa) ^ set(fb)))
        for k in sorted(set(fa) & set(fb)):
            if k == '派活/结构.md':
                continue
            ta, tb = fa[k].read_bytes(), fb[k].read_bytes()
            if k.startswith('成品/') or not k.endswith(('.md', '.txt')):
                same = ta == tb
            else:
                same = norm(ta.decode('utf-8'), a) == norm(tb.decode('utf-8'), b)
            if not same:
                diff.append(k)
        out.append('%s：甲乙对照%s' % (label(no), '，除 派活/结构.md 外只差材料夹路径' if not diff else '，有差异：%s' % diff))
        if diff:
            raise Halt('\n'.join(out))
    return out


# ---------- 5. 派活表 ----------

def read_table():
    if not TABLE.exists():
        return []
    return [l for l in TABLE.read_text(encoding='utf-8').split('\n') if l.strip()]


def write_table(arm, rows):
    keep = [l for l in read_table() if l.split('|')[1:2] != [arm]]
    TABLE.write_text('\n'.join(keep + rows) + '\n', encoding='utf-8')


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    ap = argparse.ArgumentParser(prog='备考.py', description='结构角色单考：出考试材料（见文件头说明）')
    ap.add_argument('--组', dest='arm', required=True, choices=['甲', '乙'], help='甲＝现行说明（对照组）；乙＝候选说明')
    ap.add_argument('--试跑', action='store_true', help='材料放草稿目录，不动正式夹和派活表')
    ap.add_argument('--重出', action='store_true', help='已派出的行也不管，删了重出（第二级才能用）')
    a = ap.parse_args()
    arm = a.arm
    try:
        check_fingerprints(arm)
        m = load_beiliao()
        root = (SCRATCH / ('结构考_1103_' + arm)) if a.试跑 else (OUT / ('结构考_1103_' + arm))
        if not a.试跑:
            lines = [l for l in read_table() if l.split('|')[1:2] == [arm]]
            sent = [l for l in lines if l.split('|')[3:4] != ['待派']]
            if sent and not a.重出:
                raise Halt('派活表里 %s 组已有派出的行，不重出（要重出加 --重出）：\n  %s' % (arm, '\n  '.join(sent)))
        if root.exists():
            shutil.rmtree(root)
        mdir = method_dir_for(arm, m, a.试跑)
        print('组：%s　方法目录：%s　输出根：%s%s' % (arm, mdir, root, '（试跑）' if a.试跑 else ''))
        made = {}
        rows = []
        for no, card, prods, call, 摘录, 清单 in PAPERS:
            final, n, removed, warns = build_one(m, arm, no, card, prods, call, mdir, root)
            if 摘录 is not None:
                overwrite_stable(final, 摘录, 清单)
            notes = check_one(m, arm, no, final, mdir, 摘录, root)
            made[no] = final
            print('\n%s　已剔除 %d 句%s' % (label(no), n, '' if n == 0 else '（剔了什么见下）'))
            for r in removed:
                print('  ' + r)
            if 摘录 is not None:
                print('  对齐卡摘录.md 已换成当时摘录（%s），验收清单原文.md 已换成当时清单（%s）' % (摘录.name, 清单.name))
                if n:
                    print('  （上面剔的是按卡生成的那份摘录，已被覆盖；当时摘录自己 0 命中）')
            for w in warns + notes:
                print('  ' + w)
            print('  材料夹：%s' % final)
            rows.append('%s|%s|1|待派|%s' % (label(no), arm, final))
        # 甲乙对照（两组都在正式夹或都在草稿夹时）
        base = SCRATCH if a.试跑 else OUT
        roots = {}
        for g in ('甲', '乙'):
            r = base / ('结构考_1103_' + g)
            if r.exists():
                roots[g] = {}
                for no, *_ in PAPERS:
                    ds = sorted((r / ('考试_' + no)).glob('*')) if (r / ('考试_' + no)).exists() else []
                    if ds:
                        roots[g][no] = ds[-1]
        if '甲' in roots and '乙' in roots:
            print('\n甲乙对照：')
            for l in compare_arms(roots):
                print('  ' + l)
        else:
            print('\n甲乙对照：另一组还没出，跳过')
        if not a.试跑:
            write_table(arm, rows)
            print('\n派活表：%s（%s 组 %d 行）' % (TABLE, arm, len(rows)))
        # 指纹，供写进试卷
        print('\n考前指纹：')
        if arm == '乙':
            print('  候选 结构.md sha256：%s' % sha(CAND))
        print('  备考.py sha256：%s' % sha(Path(__file__).resolve()))
        print('材料夹指纹（前 16 位）：')
        for no, *_ in PAPERS:
            f = made[no]
            print('  %s　摘录 %s　清单 %s　派活/结构 %s　总验收人说明 %s' % (
                label(no), sha(f / '对齐卡摘录.md')[:16], sha(f / '验收清单原文.md')[:16],
                sha(f / '派活/结构.md')[:16], sha(f / '总验收人说明.md')[:16]))
    except Halt as e:
        print('停：' + str(e))
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
