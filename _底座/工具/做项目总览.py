#!/usr/bin/env python3
"""从任务文件头生成 `_底座/项目总览.md`。只用标准库，不调用模型。

读：
  - `_底座/项目登记.md`：每个项目一节（「## 项目名」+「- 键：值」），以及「过渡期归属」表。
  - `_底座/任务/` 下的任务文件：新放法 `任务/<项目目录>/<日期>_<任务名>.md`，
    旧放法 `任务/<日期>_<任务名>.md`（过渡期两种都认）。验收单、自检这类过程文件不算任务。
    每件读文件头的「# 任务：」「状态：」「最后更新：」「项目：」「建卡对话：」，以及「## 交接记录」最后一行。
写：`_底座/项目总览.md`（整份覆盖）。

任务归哪个项目，按这个顺序认：「项目：」一行 → 所在项目子目录 → 过渡期归属表 →
「建卡对话：」一行里出现的项目名或别名。都认不出的，列在「未标项目」。

「久未动」：任务文件和它旁边同名文件夹里最新的修改时间，距现在超过 24 小时。
（任务文件的「最后更新」多数只写日期，不写时刻，所以用修改时间。）

用法：python3 做项目总览.py [--base 底座目录] [--now "YYYY-MM-DD HH:MM"]
"""
import argparse
import datetime as dt
import os
import re
import sys

DEFAULT_BASE = "/Users/decheng.huang/claude/_底座"
ACTIVE = ["进行中", "待拍板", "待验收", "退回"]
CLOSED = ["叫停", "已完成"]
NOT_TASK = re.compile(r"_(验收单|自检|落地清单)(_\d+)?\.md$")
STALE_HOURS = 24
DONE_DAYS = 7
CRON_WARN_DAYS = 6


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_registry(text):
    """返回 (projects, transition)。projects: [{name, 键: 值}]；transition: {任务文件名: 项目名}。"""
    projects, transition = [], {}
    cur = None
    in_transition = False
    for line in text.splitlines():
        if line.startswith("# "):
            in_transition = "过渡期归属" in line
            cur = None
            continue
        if line.startswith("## "):
            cur = {"name": line[3:].strip()}
            projects.append(cur)
            continue
        m = re.match(r"^- ([^：:]+)[：:]\s*(.*)$", line)
        if m and cur is not None:
            cur[m.group(1).strip()] = m.group(2).strip()
            continue
        if in_transition and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[0].endswith(".md"):
                transition[cells[0]] = cells[1]
    projects = [p for p in projects if "任务目录" in p]
    return projects, transition


def clean_path(v):
    return v.strip().strip("`").rstrip("/")


def aliases(p):
    names = [p["name"]] + [a.strip() for a in re.split(r"[、,，]", p.get("别名", "")) if a.strip()]
    return sorted(set(names), key=len, reverse=True)


def header_field(text, key):
    m = re.search(r"^%s[：:]\s*(.+)$" % re.escape(key), text, flags=re.M)
    return m.group(1).strip() if m else ""


def last_handoff(text):
    m = re.search(r"^## 交接记录\s*\n(.*?)(?=^## |\Z)", text, flags=re.S | re.M)
    if not m:
        return ""
    lines = [l.strip()[2:].strip() for l in m.group(1).splitlines() if l.strip().startswith("- ")]
    return lines[-1] if lines else ""


def status_kind(status):
    for k in ACTIVE + CLOSED:
        if status.startswith(k):
            return k
    return "其他"


def latest_mtime(task_path):
    t = os.path.getmtime(task_path)
    folder = task_path[:-3]
    if os.path.isdir(folder):
        for root, _dirs, files in os.walk(folder):
            for f in files:
                try:
                    t = max(t, os.path.getmtime(os.path.join(root, f)))
                except OSError:
                    pass
    return dt.datetime.fromtimestamp(t)


def find_tasks(task_root):
    out = []
    for entry in sorted(os.listdir(task_root)):
        full = os.path.join(task_root, entry)
        if os.path.isfile(full) and entry.endswith(".md") and re.match(r"^\d{4}-\d{2}-\d{2}_", entry):
            if not NOT_TASK.search(entry):
                out.append((full, None))
        elif os.path.isdir(full) and not re.match(r"^\d{4}-\d{2}-\d{2}_", entry) and entry not in ("附件", "_归档"):
            for sub in sorted(os.listdir(full)):
                sp = os.path.join(full, sub)
                if os.path.isfile(sp) and sub.endswith(".md") and re.match(r"^\d{4}-\d{2}-\d{2}_", sub) and not NOT_TASK.search(sub):
                    out.append((sp, entry))
    return out


def assign(task_path, subdir, text, projects, transition):
    by_name = {p["name"]: p for p in projects}
    declared = header_field(text, "项目")
    if declared:
        for p in projects:
            if declared in aliases(p):
                return p["name"], "项目一行"
    if subdir:
        for p in projects:
            if os.path.basename(clean_path(p["任务目录"])) == subdir:
                return p["name"], "子目录"
    fname = os.path.basename(task_path)
    if fname in transition:
        target = transition[fname]
        for p in projects:
            if target in aliases(p):
                return p["name"], "过渡期归属表"
    creator = header_field(text, "建卡对话").replace(" ", "")
    if creator:
        for p in projects:
            for a in aliases(p):
                if a.replace(" ", "") in creator:
                    return p["name"], "建卡对话"
    return None, ""


def cron_note(value, now):
    if (value or "").startswith("不开"):
        return "不开"
    m = re.search(r"(\d{4}-\d{2}-\d{2})", value or "")
    if not m:
        return value or "待补"
    days = (now.date() - dt.date.fromisoformat(m.group(1))).days
    flag = "；超过 %d 天，7 天会过期，该重建" % CRON_WARN_DAYS if days > CRON_WARN_DAYS else ""
    return "%s（%d 天前%s）" % (m.group(1), days, flag)


def short(s, n=90):
    s = re.sub(r"\s+", " ", s)
    return s if len(s) <= n else s[: n - 1] + "…"


def build(base, now):
    reg_path = os.path.join(base, "项目登记.md")
    projects, transition = parse_registry(read(reg_path))
    task_root = os.path.join(base, "任务")
    groups = {p["name"]: [] for p in projects}
    groups[None] = []
    for path, subdir in find_tasks(task_root):
        text = read(path)
        title = header_field(text, "# 任务") or os.path.basename(path)[11:-3]
        status = header_field(text, "状态") or "（没写状态）"
        mt = latest_mtime(path)
        proj, how = assign(path, subdir, text, projects, transition)
        groups[proj].append({
            "file": os.path.relpath(path, base), "title": title, "status": status,
            "kind": status_kind(status), "updated": header_field(text, "最后更新"),
            "mtime": mt, "hours": (now - mt).total_seconds() / 3600,
            "handoff": last_handoff(text), "how": how,
        })

    out = ["# 项目总览", "",
           "由 `_底座/工具/做项目总览.py` 生成，不要手改；改任务状态后重跑。生成时间：%s。" % now.strftime("%Y-%m-%d %H:%M"),
           "按项目列主对话、分发和任务。任务按状态分栏：进行中、待拍板、待验收、退回；叫停只写件数，已完成只算近 %d 天的件数。「久未动」＝超过 %d 小时没有修改。" % (DONE_DAYS, STALE_HOURS),
           ""]

    def emit_tasks(items):
        lines = []
        for kind in ACTIVE + ["其他"]:
            rows = [t for t in items if t["kind"] == kind]
            if not rows:
                continue
            lines.append("**%s（%d）**" % (kind, len(rows)))
            for t in sorted(rows, key=lambda r: r["mtime"], reverse=True):
                stale = "，**久未动 %d 小时**" % t["hours"] if t["hours"] > STALE_HOURS else ""
                how = "；按%s归项目" % t["how"] if t["how"] in ("过渡期归属表", "建卡对话") else ""
                lines.append("- %s｜状态：%s｜最后修改 %s%s｜`%s`%s" % (
                    t["title"], short(t["status"], 60), t["mtime"].strftime("%m-%d %H:%M"), stale, t["file"], how))
                if t["handoff"]:
                    lines.append("  - 交接最后一行：%s" % short(t["handoff"]))
            lines.append("")
        stopped = sum(1 for t in items if t["kind"] == "叫停")
        done = sum(1 for t in items if t["kind"] == "已完成" and t["hours"] <= DONE_DAYS * 24)
        lines.append("叫停 %d 件；近 %d 天已完成 %d 件。" % (stopped, DONE_DAYS, done))
        lines.append("")
        return lines

    for p in projects:
        items = groups[p["name"]]
        active = sum(1 for t in items if t["kind"] in ACTIVE)
        out.append("## %s（在办 %d 件）" % (p["name"], active))
        for role in ("主对话", "分发"):
            num = p.get(role + "编号", "待补")
            name = p.get(role, "待补")
            if name.startswith("不开"):
                out.append("- %s：不开" % role)
                continue
            tail = "（%s）" % num if num not in ("", "未开", "待补") else ("" if num == "未开" else "（编号待补）")
            out.append("- %s：%s%s" % (role, name, tail))
        out.append("- 分发夜间定时创建日期：%s" % cron_note(p.get("分发夜间定时创建日期"), now))
        out.append("")
        out.extend(emit_tasks(items) if items else ["没有任务。", ""])

    if groups[None]:
        out.append("## 未标项目（%d 件）" % len(groups[None]))
        out.append("任务文件里没有「项目：」一行，也不在项目子目录、过渡期归属表里，建卡对话也认不出项目。补上「项目：」一行就会归位。")
        out.append("")
        out.extend(emit_tasks(groups[None]))
    return "\n".join(out).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--now", default="")
    ap.add_argument("--stdout", action="store_true", help="只打印，不写文件")
    a = ap.parse_args()
    now = dt.datetime.strptime(a.now, "%Y-%m-%d %H:%M") if a.now else dt.datetime.now()
    text = build(a.base, now)
    if a.stdout:
        sys.stdout.write(text)
        return
    target = os.path.join(a.base, "项目总览.md")
    with open(target, "w", encoding="utf-8") as f:
        f.write(text)
    print("已写 %s" % target)


if __name__ == "__main__":
    main()
