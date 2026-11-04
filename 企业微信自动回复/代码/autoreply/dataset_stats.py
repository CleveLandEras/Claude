"""统计测试集每类条数，并判条数门槛。

在 代码/ 目录下运行（只用标准库，不需要虚拟环境）：
    python3 -m autoreply.dataset_stats 测试集/合成.jsonl

退出码：0 条数全部达标；1 格式没错但条数不达标；2 文件读不了或格式有错。
字段和类别的含义见 测试集/说明.md；门槛出处见思考页 7.1 ⑧、7.2 里程碑 2 第 2 步。
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

AUTO_LABELS = ("上课时间", "回放链接", "作业截止", "请假调课")
HANDOFF_LABELS = ("学科答疑", "续报", "退费", "投诉", "带情绪")
UNSURE_LABEL = "都不是／拿不准"
ALL_LABELS = AUTO_LABELS + HANDOFF_LABELS + (UNSURE_LABEL,)

MIN_PER_HANDOFF = 30
MIN_HANDOFF_TOTAL = 150
MIN_TOTAL = 300
MIN_MIXED = 30
MIN_TRICKY = 30

FIELD_TYPES = {
    "id": str,
    "text": str,
    "label": str,
    "mixed": bool,
    "tricky": bool,
    "parts": list,
    "note": str,
}


class DatasetError(Exception):
    """文件读不了或格式有错。problems 每条写明第几行、错在哪。"""

    def __init__(self, problems):
        super().__init__("\n".join(problems))
        self.problems = problems


def _row_problems(row):
    if not isinstance(row, dict):
        return ["不是 JSON 对象"]
    problems = []
    for field, expected in FIELD_TYPES.items():
        if field not in row:
            problems.append(f"缺字段 {field}")
        elif not isinstance(row[field], expected):
            problems.append(f"字段 {field} 类型应为 {expected.__name__}")
    if problems:
        return problems

    if not row["text"].strip():
        problems.append("text 是空的")
    if row["label"] not in ALL_LABELS:
        problems.append(f"类别不认识：{row['label']}")
    unknown_parts = [part for part in row["parts"] if part not in ALL_LABELS]
    if unknown_parts:
        problems.append(f"parts 里有不认识的类别：{unknown_parts}")

    if row["mixed"]:
        if len(row["parts"]) < 2:
            problems.append("混合消息的 parts 至少写两类")
        if row["label"] in AUTO_LABELS:
            problems.append("混合消息要整条转二讲，label 不能是自动类")
        if row["label"] != UNSURE_LABEL and row["label"] not in row["parts"]:
            problems.append("混合消息的 label 应在 parts 里")
    elif row["parts"]:
        problems.append("不是混合消息，parts 应为空")
    return problems


def load_rows(path):
    """读 JSONL 并逐行查格式；有错就抛 DatasetError，列出全部错误。"""
    try:
        content = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise DatasetError([f"读不了 {path}：{exc}"]) from exc

    rows, problems = [], []
    seen_ids, seen_texts = set(), set()
    for number, line in enumerate(content.split("\n"), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError as exc:
            problems.append(f"第 {number} 行不是合法 JSON：{exc}")
            continue
        row_problems = _row_problems(row)
        if row_problems:
            problems.extend(f"第 {number} 行：{item}" for item in row_problems)
            continue
        if row["id"] in seen_ids:
            problems.append(f"第 {number} 行：id 重复 {row['id']}")
        if row["text"] in seen_texts:
            problems.append(f"第 {number} 行：原话重复（{row['id']}）")
        seen_ids.add(row["id"])
        seen_texts.add(row["text"])
        rows.append(row)
    if problems:
        raise DatasetError(problems)
    return rows


def summarize(rows):
    """按类别数条数：全部、普通（既不混合也不刁钻）、混合、刁钻。"""
    return {
        "all": Counter(row["label"] for row in rows),
        "plain": Counter(
            row["label"] for row in rows if not row["mixed"] and not row["tricky"]
        ),
        "mixed": Counter(row["label"] for row in rows if row["mixed"]),
        "tricky": Counter(row["label"] for row in rows if row["tricky"]),
    }


def _size_measures(counter):
    """返回（转二讲最少的一类条数，转二讲合计，总数）。"""
    handoff = [counter[label] for label in HANDOFF_LABELS]
    return min(handoff), sum(handoff), sum(counter.values())


def check_thresholds(summary):
    """返回 [(是否过, 一行说明)]。

    思考页 7.1 ⑧ 写的是「同样条数，另加混合消息和刁钻说法各 30 条」，
    所以除了算全部，再查一遍扣掉混合和刁钻之后是否仍满足前三条。
    """
    least, handoff_total, total = _size_measures(summary["all"])
    mixed_total = sum(summary["mixed"].values())
    tricky_total = sum(summary["tricky"].values())
    plain_least, plain_handoff, plain_total = _size_measures(summary["plain"])
    plain_ok = (
        plain_least >= MIN_PER_HANDOFF
        and plain_handoff >= MIN_HANDOFF_TOTAL
        and plain_total >= MIN_TOTAL
    )
    return [
        (least >= MIN_PER_HANDOFF, f"转二讲 5 类每类 ≥ {MIN_PER_HANDOFF}（最少的一类 {least}）"),
        (handoff_total >= MIN_HANDOFF_TOTAL, f"转二讲 5 类合计 ≥ {MIN_HANDOFF_TOTAL}（实际 {handoff_total}）"),
        (total >= MIN_TOTAL, f"总数 ≥ {MIN_TOTAL}（实际 {total}）"),
        (mixed_total >= MIN_MIXED, f"混合 ≥ {MIN_MIXED}（实际 {mixed_total}）"),
        (tricky_total >= MIN_TRICKY, f"刁钻 ≥ {MIN_TRICKY}（实际 {tricky_total}）"),
        (
            plain_ok,
            "扣掉混合和刁钻后仍满足前三条"
            f"（转二讲每类最少 {plain_least}，合计 {plain_handoff}，总数 {plain_total}）",
        ),
    ]


def _handling(label):
    return "自动" if label in AUTO_LABELS else "转二讲"


def format_report(path, summary, checks):
    lines = [f"文件：{path}", "全部  普通  混合  刁钻  处理    类别"]
    for label in ALL_LABELS:
        lines.append(
            f"{summary['all'][label]:>4}  {summary['plain'][label]:>4}  "
            f"{summary['mixed'][label]:>4}  {summary['tricky'][label]:>4}  "
            f"{_handling(label)}  {label}"
        )
    lines.append(
        f"{sum(summary['all'].values()):>4}  {sum(summary['plain'].values()):>4}  "
        f"{sum(summary['mixed'].values()):>4}  {sum(summary['tricky'].values()):>4}  合计"
    )
    lines.append("混合和刁钻可以同时为真，所以「普通＋混合＋刁钻」可能大于「全部」。")
    lines.append("门槛：")
    lines.extend(f"  {'过' if passed else '不过'}  {text}" for passed, text in checks)
    lines.append("结论：全部达标" if all(passed for passed, _ in checks) else "结论：不达标")
    return "\n".join(lines)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("用法：python3 -m autoreply.dataset_stats 测试集/合成.jsonl", file=sys.stderr)
        return 2
    try:
        rows = load_rows(args[0])
    except DatasetError as exc:
        print("格式有错：", file=sys.stderr)
        for problem in exc.problems:
            print(f"  {problem}", file=sys.stderr)
        return 2
    summary = summarize(rows)
    checks = check_thresholds(summary)
    print(format_report(args[0], summary, checks))
    return 0 if all(passed for passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
