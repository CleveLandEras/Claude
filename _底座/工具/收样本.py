#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""收样本.py —— Dk 判过的稿入账（合格样本／漏拦），总验收人判有问题的稿抽样快照。

用法（都在 ~/claude/_底座/工具/ 下跑）：
  python3 收样本.py                 扫任务文件，状态以「已完成」「退回」开头且还没登记的，快照成品到
                                    考试/原稿/<日期>_<任务名>/，在 考试/样本登记.md 加一行，最后输出对账。
  python3 收样本.py --只看          只列出会做什么，不复制、不写。
  python3 收样本.py --被拦 <任务文件> <成品路径> <意见出处>
                                    总验收人判有问题、返工之前跑：快照到 考试/原稿/被拦_<日期>_<名>/，
                                    在 考试/被拦稿抽样.md 加一行；当天已有 3 行就只快照。
可选（测试用）：--抽样文件 <路径>  --登记文件 <路径>  --原稿目录 <路径>  --任务目录 <路径>  --今天 YYYY-MM-DD
依据：任务/用好Claude/2026-10-29_自循环闭环_查顶尖做法并建起来/思考页.md 第 4.2 节③、第 12 节第 1 条。
"""
import argparse
import datetime
import os
import re
import shutil
import sys

BASE = '/Users/decheng.huang/claude/_底座'
ROOT = '/Users/decheng.huang/claude'
TASK_DIR = BASE + '/任务'
EXAM_DIR = BASE + '/考试'
SRC_DIR = EXAM_DIR + '/原稿'
REG_FILE = EXAM_DIR + '/样本登记.md'
BLOCK_FILE = EXAM_DIR + '/被拦稿抽样.md'
JIAN_CE_START = datetime.date(2026, 10, 31)   # 机检脚本从这天起才有，之前的件不计漏跑
DAY_CAP = 3                                    # 被拦稿抽样每天最多记几行

REG_HEAD = '| 日期 | 任务文件 | 快照 | 验收结论 | Dk 结论 | Dk 原话 | 用途 |\n|---|---|---|---|---|---|---|\n'
BLOCK_HEAD = '| 日期 | 任务文件 | 快照 | 总验收人判有问题的理由 | Dk 判了没有 | Dk 原话 |\n|---|---|---|---|---|---|\n'


# ---------- 读任务文件 ----------
def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def status_of(text):
    for line in text.splitlines()[:12]:
        m = re.match(r'^状态[：:]\s*(.*)$', line)
        if m:
            return m.group(1).strip()
    return None


def sections(text):
    """按 '## ' 二级标题切，返回 [(标题, 正文行列表)]。"""
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith('## '):
            cur = (line[3:].strip(), [])
            out.append(cur)
        elif cur is not None:
            cur[1].append(line)
    return out


def section(text, prefix):
    for title, body in sections(text):
        if title.startswith(prefix):
            return body
    return None


def stem_parts(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    m = re.match(r'^(\d{4}-\d{2}-\d{2})_(.+)$', stem)
    if m:
        return m.group(1), m.group(2), stem
    return None, stem, stem


def update_date(text, path):
    m = re.search(r'^最后更新[：:]\s*(\d{4}-\d{2}-\d{2})', text, re.M)
    if m:
        return datetime.date.fromisoformat(m.group(1))
    return datetime.date.fromtimestamp(os.path.getmtime(path))


def to_review_date(text, path):
    """改成待验收的日期：交接记录里最后一条「状态改…待验收」的 MM/DD；没有就取最后更新日。"""
    best = None
    year = update_date(text, path).year
    for line in text.splitlines():
        m = re.match(r'^\s*[-*]\s*(\d{1,2})/(\d{1,2})\b', line)
        if m and re.search(r'状态[^。；，,\n]{0,6}待验收', line):
            try:
                best = datetime.date(year, int(m.group(1)), int(m.group(2)))
            except ValueError:
                pass
    return best or update_date(text, path)


def find_tasks(task_dir):
    """任务文件＝日期开头的 .md，第 3 行附近有「状态：」；跳过同名文件夹里的思考页等和 附件、_ 开头的文件夹。"""
    found = []
    for dp, dns, fns in os.walk(task_dir):
        rel = os.path.relpath(dp, task_dir)
        parts = [] if rel == '.' else rel.split(os.sep)
        if any(p == '附件' or p.startswith('_') for p in parts):
            dns[:] = []
            continue
        # 同名文件夹：父目录里有 <本目录名>.md，就是任务文件的附属文件夹，整个跳过
        if parts and os.path.exists(os.path.join(os.path.dirname(dp), parts[-1] + '.md')):
            dns[:] = []
            continue
        for fn in sorted(fns):
            if not fn.endswith('.md') or not re.match(r'^\d{4}-\d{2}-\d{2}_', fn):
                continue
            p = os.path.join(dp, fn)
            try:
                text = read(p)
            except Exception:
                continue
            st = status_of(text)
            if st is None:
                continue
            found.append(dict(path=p, rel=os.path.relpath(p, task_dir), text=text, status=st))
    return found


def product_path(text):
    """「## 交付」里「成品：」指的路径；找不到返回 None。"""
    body = section(text, '交付')
    if not body:
        return None
    for i, line in enumerate(body):
        if re.search(r'成品\**[：:]', line):
            seg = line.split('：', 1)[-1] if '：' in line else line.split(':', 1)[-1]
            seg = seg + ' ' + (body[i + 1] if i + 1 < len(body) else '')
            for m in re.finditer(r'`([^`]+)`', seg):
                c = m.group(1).strip()
                if c.startswith('/') or c.startswith('~') or '/' in c:
                    return norm_path(c)
            m = re.search(r'((?:/Users/|~/)[^\s`（(，,。;；]+)', seg)
            if m:
                return norm_path(m.group(1))
            return None
    return None


def norm_path(c):
    c = os.path.expanduser(c)
    if not c.startswith('/'):
        c = os.path.join(ROOT, c)
    return os.path.normpath(c)


def first_sentence(s):
    s = s.strip()
    return re.split(r'(?<=[。！？])', s)[0].strip()


def verdict_lines(text):
    """「## 验收结论」里的有效行：去掉空行、Dk 验收那一行。返回 (原始第一行, 验收结论第一句, 机检用行)。"""
    body = section(text, '验收结论')
    if not body:
        return None, '任务文件没记', None
    raw = [l.strip() for l in body if l.strip()]
    core = [l for l in raw if not re.match(r'^[-*•]?\s*\**Dk 验收', l)]
    first_raw = core[0] if core else (raw[0] if raw else None)
    sent = '任务文件没记'
    if core:
        s = core[0].lstrip('-*• ').lstrip('#').strip().strip('*').strip()
        sent = first_sentence(s)[:160] or '任务文件没记'
    # 机检用行：第一条有效行（标题行连同下一行）
    jian = None
    if core:
        jian = core[0]
        if core[0].startswith('#') and len(core) > 1:   # 第一行只是标题时，连同紧接着的内容行一起看
            jian = core[0] + ' ' + core[1]
    return first_raw, sent, jian


def dk_quote(text):
    """交接记录里最后一条 Dk 验收／退回的原话（「」里的）；找不到写「任务文件没记」。"""
    cand = []
    body = section(text, '交接记录') or []
    for line in reversed(body):
        m = re.search(r'Dk[^「。\n]{0,12}?(验收|退回)', line)
        if m:
            qs = re.findall(r'「([^」]+)」', line[m.start():])
            if qs:
                cand = qs
                break
    if not cand:
        for line in section(text, '验收结论') or []:
            m = re.search(r'Dk 验收[^「\n]{0,40}[：:]\s*「([^」]+)」', line)
            if m:
                cand = [m.group(1)]
                break
    return '「' + '」「'.join(cand) + '」' if cand else '任务文件没记'


# ---------- 登记表 ----------
def cell(s, n=140):
    s = re.sub(r'\s+', ' ', str(s)).replace('|', '｜').strip()
    return s if len(s) <= n else s[:n - 1] + '…'


def table_rows(path):
    """返回数据行的单元格列表（跳过表头和分隔线）。"""
    rows = []
    if not os.path.exists(path):
        return rows
    for line in read(path).splitlines():
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if not cells or cells[0] in ('日期',) or set(cells[0]) <= set('-: '):
            continue
        rows.append(cells)
    return rows


def append_row(path, head, cells):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(head)
    text = read(path)
    if text and not text.endswith('\n'):
        text += '\n'
    text += '| ' + ' | '.join(cells) + ' |\n'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


# ---------- 快照 ----------
def snapshot(src, dest, dry):
    """把成品文件或文件夹复制到 dest 目录里；返回 (是否成功, 说明)。"""
    if not src or not os.path.exists(src):
        return False, '原稿丢失'
    if dry:
        return True, '只看，没复制'
    os.makedirs(dest, exist_ok=True)
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(dest, os.path.basename(src.rstrip('/'))), dirs_exist_ok=True)
    else:
        shutil.copy2(src, dest)
    return True, '已复制'


def rel_exam(path):
    """快照路径写成相对 _底座/ 的形式，好读。"""
    p = os.path.normpath(path)
    return os.path.relpath(p, BASE) if p.startswith(BASE) else p


# ---------- 对账 ----------
def reconcile(tasks, reg_path):
    judged = [t for t in tasks if t['status'].startswith(('已完成', '退回'))]
    n = len(judged)
    m = len(table_rows(reg_path))
    # 漏跑机检：10/31 及以后改成待验收的件（现状为待验收／已完成／退回），验收结论第一行不含「机检」
    in_scope, missing, before = [], [], []
    for t in tasks:
        if not t['status'].startswith(('待验收', '已完成', '退回')):
            continue
        d = to_review_date(t['text'], t['path'])
        if d >= JIAN_CE_START:
            in_scope.append(t)
            _, _, jian = verdict_lines(t['text'])
            if not jian or '机检' not in jian:
                missing.append(t)
        else:
            before.append(t)
    return dict(n=n, m=m, diff=n - m, in_scope=in_scope, missing=missing, before=before)


def print_reconcile(r):
    print('判过的件数 %d｜登记件数 %d｜对账差 %d' % (r['n'], r['m'], r['diff']))
    print('漏跑机检 %d 件（只数 10/31 及以后改成待验收的件，共 %d 件）' % (len(r['missing']), len(r['in_scope'])))
    for t in r['missing']:
        print('  缺机检：' + t['rel'])
    print('10/31 前的件不计：%d 件（机检脚本当时还不存在）' % len(r['before']))


# ---------- 主流程 ----------
def run_collect(args):
    tasks = find_tasks(args.任务目录)
    registered = set()
    for cells in table_rows(args.登记文件):
        if len(cells) > 1:
            registered.add(cells[1].strip('` '))
    judged = [t for t in tasks if t['status'].startswith(('已完成', '退回'))]
    todo = [t for t in judged if t['rel'] not in registered]
    # 同一成品被多个任务改过的，提醒快照是当前版本
    by_prod = {}
    for t in judged:
        t['prod'] = product_path(t['text'])
        if t['prod']:
            by_prod.setdefault(t['prod'], []).append(t)
    print('%s扫到任务文件 %d 件；状态已完成／退回 %d 件；已登记 %d 件；这次要登记 %d 件。'
          % ('【只看】' if args.只看 else '', len(tasks), len(judged), len(judged) - len(todo), len(todo)))
    added = 0
    for t in todo:
        d, name, stem = stem_parts(t['path'])
        dest = os.path.join(args.原稿目录, stem)
        ok, why = snapshot(t['prod'], dest, args.只看)
        verdict_kind = '已完成' if t['status'].startswith('已完成') else '退回'
        snap = rel_exam(dest) + '/' if ok else '原稿丢失'
        note = ''
        if t['prod'] and len(by_prod.get(t['prod'], [])) > 1:
            later = sorted(x['rel'] for x in by_prod[t['prod']])
            if t['rel'] != later[-1]:
                note = '；同一成品后来还被「%s」改过，快照是现在的版本，不是当时那版' % stem_parts(later[-1])[1]
        if verdict_kind == '已完成':
            use = '合格样本' if ok else '合格样本（原稿丢失，不能拿来考）'
        else:
            use = '漏拦，待出题' if ok else '漏拦（原稿丢失，不能出题）'
        _, vsent, _ = verdict_lines(t['text'])
        cells = [update_date(t['text'], t['path']).isoformat(), '`' + t['rel'] + '`', cell(snap + note, 200),
                 cell(vsent), verdict_kind, cell(dk_quote(t['text']), 200), use + (note and '，快照非当时版本' or '')]
        print('  %s %s → 快照：%s｜成品：%s｜Dk 结论：%s｜用途：%s'
              % ('要登记' if args.只看 else '已登记', t['rel'], snap, t['prod'] or '「## 交付」里没找到成品路径',
                 verdict_kind, use))
        if note:
            print('    注意：' + note.lstrip('；'))
        if not args.只看:
            append_row(args.登记文件, REG_HEAD, cells)
            added += 1
    r = reconcile(tasks, args.登记文件)
    if args.只看:
        print('（只看：登记件数是现状；真跑后会再登记 %d 件，对账差应为 %d）' % (len(todo), r['diff'] - len(todo)))
    print_reconcile(r)


def extract_reason(src):
    """意见出处（总验收人终判，或旧验收官的意见）：是文件就取第一处「有问题」「不通过」「不过」附近的一两句（「没有问题」不算）；不是文件就当原文用。"""
    if src and os.path.isfile(src):
        lines = [l.strip() for l in read(src).splitlines() if l.strip()]
        pick = None
        for i, l in enumerate(lines):
            if re.search(r'(?<!没)有问题', l) or '不通过' in l or '不过' in l:
                pick = ' '.join(lines[i:i + 2])
                break
        if pick is None:
            pick = next((l for l in lines if not l.startswith('#')), '')
        pick = re.sub(r'[*#`>]', '', pick).strip()
        return cell(pick, 200) + '（出处：' + src + '）'
    return cell(src, 240) + '（出处：口述，没有文件）'


def run_blocked(args):
    task, product, source = args.被拦
    task = norm_path(task)
    product = norm_path(product)
    today = args.今天
    _, name, _ = stem_parts(task)
    dest = os.path.join(args.原稿目录, '被拦_%s_%s' % (today, name))
    k = 2
    base_dest = dest
    while os.path.exists(dest) and not args.只看:
        dest = '%s_%d' % (base_dest, k)
        k += 1
    ok, why = snapshot(product, dest, args.只看)
    snap = rel_exam(dest) + '/' if ok else '原稿丢失'
    n_today = sum(1 for c in table_rows(args.抽样文件) if c and c[0] == today)
    rel_task = os.path.relpath(task, args.任务目录) if task.startswith(args.任务目录) else task
    print('%s被拦稿：%s｜快照：%s（%s）｜今天抽样文件已有 %d 行' % ('【只看】' if args.只看 else '', rel_task, snap, why, n_today))
    if n_today >= DAY_CAP:
        print('今天已满 %d 份，只快照' % DAY_CAP)
        return
    cells = [today, '`' + cell(rel_task, 120) + '`', cell(snap, 200), extract_reason(source), '没判', '—']
    if args.只看:
        print('将在 %s 加一行（当天第 %d 份）' % (args.抽样文件, n_today + 1))
        return
    append_row(args.抽样文件, BLOCK_HEAD, cells)
    print('已在 %s 加一行（当天第 %d 份）' % (args.抽样文件, n_today + 1))


def main():
    ap = argparse.ArgumentParser(description='收样本：Dk 判过的稿入账；总验收人判有问题的稿抽样快照')
    ap.add_argument('--只看', action='store_true', help='只列出会做什么，不复制、不写')
    ap.add_argument('--被拦', nargs=3, metavar=('任务文件', '成品路径', '意见出处'))
    ap.add_argument('--抽样文件', default=BLOCK_FILE)
    ap.add_argument('--登记文件', default=REG_FILE)
    ap.add_argument('--原稿目录', default=SRC_DIR)
    ap.add_argument('--任务目录', default=TASK_DIR)
    ap.add_argument('--今天', default=datetime.date.today().isoformat())
    args = ap.parse_args()
    if args.被拦:
        run_blocked(args)
    else:
        run_collect(args)


if __name__ == '__main__':
    sys.exit(main())
