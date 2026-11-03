#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查规则预算：规则越攒越多会变成负担，所以每次整理纠正前后都用程序量一遍。

查这些：
  1. ~/.claude/CLAUDE.md 不超过 80 行、不超过 8,000 字（字＝去掉所有空白后的字符数）。
  2. _底座/全局规则_快照.md 与全局规则逐字节相同。
  3. _底座/验收清单.md 条目不超过 25 条；每条末尾括号里有来源；有题号更好（缺题号只提示）。
  4. _底座/失败类型表.md 里「落在哪」列不是「—」的，路径部分要存在
     （还没建＝提示；状态是「待落地」的行，落点还不存在也只提示）。

用法：
  python3 查规则预算.py
  python3 查规则预算.py --全局规则 <路径> --清单 <路径>     （测副本；快照和这份全局规则比）
  另有 --快照 <路径> --失败类型表 <路径> 用来测副本。

输出：逐项「过／不过／提示：原因」，最后一行「预算：过」或「预算：不过」，不过时退出码 1。
"""
import argparse
import glob
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.path.expanduser("~/claude/_底座"))
DEFAULT_GLOBAL = Path(os.path.expanduser("~/.claude/CLAUDE.md"))
DEFAULT_SNAPSHOT = ROOT / "全局规则_快照.md"
DEFAULT_CHECKLIST = ROOT / "验收清单.md"
DEFAULT_FAILTABLE = ROOT / "失败类型表.md"

MAX_LINES = 80
MAX_CHARS = 8000
MAX_ITEMS = 25

DASHES = {"—", "–", "-", "－", "─", "――", "——", ""}
EXT_RE = re.compile(r"\.(md|py|json|sh|html|txt|pptx|yaml|yml|toml|js)$", re.I)


def read_text(p):
    return Path(p).read_text(encoding="utf-8", errors="replace")


def nums(ns, limit=10):
    ns = list(ns)
    s = "、".join(str(n) for n in ns[:limit])
    return s + ("……" if len(ns) > limit else "")


# ---------- 1、2：全局规则与快照 ----------

def check_global(gpath, spath):
    out = []
    g = Path(gpath).expanduser()
    if not g.is_file():
        return [("不过", "全局规则文件不存在：%s" % gpath)]
    text = read_text(g)
    n_lines = len(text.splitlines())
    n_chars = len(re.sub(r"\s", "", text))
    out.append(("过" if n_lines <= MAX_LINES else "不过",
                "全局规则 %d 行（上限 %d 行）" % (n_lines, MAX_LINES)))
    out.append(("过" if n_chars <= MAX_CHARS else "不过",
                "全局规则 %s 字，去掉空白后计（上限 %s 字）" % (format(n_chars, ","), format(MAX_CHARS, ","))))
    s = Path(spath).expanduser()
    if not s.is_file():
        out.append(("不过", "全局规则快照不存在：%s" % spath))
    elif g.read_bytes() == s.read_bytes():
        out.append(("过", "快照与全局规则逐字节相同"))
    else:
        out.append(("不过", "快照与全局规则不是逐字节相同（%s 对 %s）" % (s.name, g.name)))
    return out


# ---------- 3：验收清单 ----------

def check_checklist(cpath):
    c = Path(cpath).expanduser()
    if not c.is_file():
        return [("不过", "验收清单不存在：%s" % cpath)]
    items = []  # (序号, 整行)
    for line in read_text(c).splitlines():
        m = re.match(r"^\s*(\d+)\.\s+(.*\S)\s*$", line)
        if m:
            items.append((int(m.group(1)), m.group(2)))
    out = []
    n = len(items)
    out.append(("过" if n <= MAX_ITEMS else "不过", "验收清单 %d 条（上限 %d 条）" % (n, MAX_ITEMS)))
    no_source, no_qnum = [], []
    for no, body in items:
        m = re.search(r"（([^（）]+)）\s*$", body) or re.search(r"\(([^()]+)\)\s*$", body)
        src = m.group(1).strip() if m else ""
        if not src:
            no_source.append(no)
        elif not re.search(r"题\s*\d+", src):
            no_qnum.append(no)
    if no_source:
        out.append(("不过", "验收清单有 %d 条没有来源（条末括号）：第 %s 条" % (len(no_source), nums(no_source))))
    else:
        out.append(("过", "验收清单每条都有来源"))
    if no_qnum:
        out.append(("提示", "验收清单 %d 条还没有题号（考试题里的题号），缺的是第 %s 条" % (len(no_qnum), nums(no_qnum))))
    return out


# ---------- 4：失败类型表 ----------

def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def path_tokens(cell):
    cell = cell.replace("`", " ")
    toks = re.split(r"[\s＋+、；;，,（）()「」《》|]+", cell)
    out = []
    for t in toks:
        t = re.sub(r"#.*$", "", t)
        t = re.sub(r":\d+$", "", t)
        t = t.strip("：:。.")
        if not t:
            continue
        looks_path = ("/" in t and re.search(r"[^\d/]", t)) or EXT_RE.search(t)
        if looks_path:
            out.append(t)
    return out


def path_exists(tok, table_dir):
    if tok.startswith("~") or tok.startswith("/"):
        cands = [Path(os.path.expanduser(tok))]
    else:  # 相对路径：依次在 _底座、~/claude、~/.claude、失败类型表所在目录下找
        cands = [b / tok for b in (ROOT, ROOT.parent, Path.home() / ".claude", table_dir)]
    for c in cands:
        try:
            if ("*" in tok and glob.glob(str(c))) or ("*" not in tok and c.exists()):
                return True
        except OSError:
            pass
    return False


def check_failtable(fpath):
    f = Path(fpath).expanduser()
    if not f.is_file():
        return [("提示", "失败类型表还没建")]
    lines = read_text(f).splitlines()
    out = []
    bad, soft, checked = [], [], 0
    found_header = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("|") and "落在哪" in line:
            found_header = True
            header = split_row(line)
            col = header.index("落在哪") if "落在哪" in header else next(
                k for k, h in enumerate(header) if "落在哪" in h)
            scol = next((k for k, h in enumerate(header) if h.startswith("状态")), None)
            ncol = 0
            i += 1
            if i < len(lines) and re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", lines[i]):
                i += 1
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = split_row(lines[i])
                i += 1
                if col >= len(cells):
                    continue
                cell = cells[col].strip().strip("`").strip()
                if cell in DASHES:
                    continue
                name = cells[ncol] if ncol < len(cells) else "?"
                status = cells[scol] if scol is not None and scol < len(cells) else ""
                lenient = status.startswith("待落地")
                toks = path_tokens(cell)
                checked += 1
                if not toks:
                    (soft if lenient else bad).append("「%s」落在哪没有可识别的路径（%s）" % (name, cell))
                    continue
                for t in toks:
                    if not path_exists(t, f.parent):
                        (soft if lenient else bad).append("「%s」→ %s" % (name, t))
            continue
        i += 1
    if not found_header:
        return [("不过", "失败类型表里找不到带「落在哪」列的表")]
    if bad:
        out.append(("不过", "失败类型表有 %d 处「落在哪」的路径不存在：%s" % (len(bad), "；".join(bad[:8]))))
    else:
        out.append(("过", "失败类型表 %d 行写了落点，路径都存在" % (checked - len(soft)) if checked else "失败类型表没有写落点的行"))
    if soft:
        out.append(("提示", "失败类型表有 %d 处待落地行的落点还不存在（算已处理，落地后再查）：%s" % (len(soft), "；".join(soft[:8]))))
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(prog="查规则预算.py", description="查全局规则、验收清单、失败类型表有没有超预算。")
    ap.add_argument("--全局规则", dest="glob_rule", default=str(DEFAULT_GLOBAL), help="默认 ~/.claude/CLAUDE.md")
    ap.add_argument("--清单", dest="checklist", default=str(DEFAULT_CHECKLIST), help="默认 _底座/验收清单.md")
    ap.add_argument("--快照", dest="snapshot", default=str(DEFAULT_SNAPSHOT), help="默认 _底座/全局规则_快照.md")
    ap.add_argument("--失败类型表", dest="failtable", default=str(DEFAULT_FAILTABLE), help="默认 _底座/失败类型表.md")
    args = ap.parse_args()
    results = []
    results += check_global(args.glob_rule, args.snapshot)
    results += check_checklist(args.checklist)
    results += check_failtable(args.failtable)
    for s, msg in results:
        print("%s：%s" % (s, msg))
    bad = any(s == "不过" for s, _ in results)
    print("预算：不过" if bad else "预算：过")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
