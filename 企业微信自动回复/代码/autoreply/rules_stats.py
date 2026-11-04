"""统计规则层在测试集上拦下多少。只读，只用标准库。

在 代码/ 目录下运行：
    python3 -m autoreply.rules_stats 测试集/合成.jsonl
    python3 -m autoreply.rules_stats 测试集/合成.jsonl -v   # 另列漏过规则层的转二讲句

口径：
- 拦下＝规则层判转二讲，不管显示的类别和标注是否一致（类别只影响提醒，不影响误发）。
- 转二讲类没拦下的不算误发，它们留给模型层。
- 自动类被拦算「误拦」，只影响漏答，不影响误发。
- 普通事务句＝自动 4 类里既不混合也不刁钻的句子。

退出码：0 正常；2 文件读不了或格式有错。不设比例门槛。
词表参照这份测试集写过，数字不代表真实家长消息上的表现。
"""
from __future__ import annotations

import sys

from .dataset_stats import AUTO_LABELS, HANDOFF_LABELS, UNSURE_LABEL, DatasetError, load_rows
from .rules import HANDOFF, check, is_pure_non_text


def _kind(row):
    if row["mixed"]:
        return "混合"
    if row["tricky"]:
        return "刁钻"
    return "普通"


def _rate(hit, total):
    return f"{hit}/{total}"


def _intercept_line(label, rows, intercepted):
    parts = []
    for kind in ("普通", "刁钻", "混合"):
        subset = [row for row in rows if _kind(row) == kind]
        if subset:
            parts.append(f"{kind} {_rate(sum(row['id'] in intercepted for row in subset), len(subset))}")
    hit = sum(row["id"] in intercepted for row in rows)
    return f"  {label}  {_rate(hit, len(rows))}（{'，'.join(parts)}）"


def _row_line(row, result):
    words = "、".join(hit.word for hit in result.hits) or "无"
    return f"  {row['id']} {row['label']} [{_kind(row)}] 命中：{words}｜{row['text']!r}"


def format_report(path, rows, results, verbose=False):
    intercepted = {row["id"] for row in rows if results[row["id"]].decision == HANDOFF}
    by_label = {
        label: [row for row in rows if row["label"] == label]
        for label in AUTO_LABELS + HANDOFF_LABELS + (UNSURE_LABEL,)
    }

    handoff_rows = [row for label in HANDOFF_LABELS for row in by_label[label]]
    lines = [f"文件：{path}", "转二讲各类被规则层拦下（没拦下的留给模型层）："]
    lines.extend(_intercept_line(label, by_label[label], intercepted) for label in HANDOFF_LABELS)
    lines.append(_intercept_line("合计", handoff_rows, intercepted))

    unsure_rows = by_label[UNSURE_LABEL]
    pure = sum(is_pure_non_text(row["text"]) for row in unsure_rows)
    lines.append("都不是／拿不准（也该转二讲）：")
    lines.append(_intercept_line(UNSURE_LABEL, unsure_rows, intercepted))
    lines.append(f"  其中纯非文字消息 {pure} 条")

    auto_rows = [row for label in AUTO_LABELS for row in by_label[label]]
    plain_auto = [row for row in auto_rows if _kind(row) == "普通"]
    lines.append("自动 4 类被规则层误拦（只影响漏答，不影响误发）：")
    lines.extend(_intercept_line(label, by_label[label], intercepted) for label in AUTO_LABELS)
    lines.append(_intercept_line("合计", auto_rows, intercepted))
    lines.append(
        "普通事务句被误拦："
        + _rate(sum(row["id"] in intercepted for row in plain_auto), len(plain_auto))
    )

    wrongly = [row for row in auto_rows if row["id"] in intercepted]
    if wrongly:
        lines.append("误拦明细：")
        lines.extend(_row_line(row, results[row["id"]]) for row in wrongly)
    if verbose:
        missed = [row for row in handoff_rows if row["id"] not in intercepted]
        lines.append(f"漏过规则层的转二讲句（{len(missed)} 条）：")
        lines.extend(_row_line(row, results[row["id"]]) for row in missed)
    return "\n".join(lines)


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    verbose = "-v" in args
    paths = [arg for arg in args if arg != "-v"]
    if len(paths) != 1:
        print("用法：python3 -m autoreply.rules_stats 测试集/合成.jsonl [-v]", file=sys.stderr)
        return 2
    try:
        rows = load_rows(paths[0])
    except DatasetError as exc:
        print("格式有错：", file=sys.stderr)
        for problem in exc.problems:
            print(f"  {problem}", file=sys.stderr)
        return 2
    results = {row["id"]: check(row["text"]) for row in rows}
    print(format_report(paths[0], rows, results, verbose=verbose))
    return 0


if __name__ == "__main__":
    sys.exit(main())
