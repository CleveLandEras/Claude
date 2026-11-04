"""定阈值：关掉规则层跑几组阈值，输出对比表（思考页里程碑 2 第 6 步）。

在 代码/ 目录下运行：
    python3 -m autoreply.tune --set 测试集/合成.jsonl
    python3 -m autoreply.tune --set 测试集/合成.jsonl --backend fake --thresholds 0.6,0.8,0.9 --out 报告/tune.json

- 关规则层是因为规则层会把转二讲句拦掉，阈值就定不出来（11/04 第二级改第 ⑤ 点）。
- 每条只问模型一次，再用不同阈值过门，所以阈值再多也不多花钱。
- 只照合成集调：文件名带「留出」直接拒绝（11/04 第二级改第 ② 点）。
- 推荐标准（11/04 分发改）：硬条件是 misfire==0 且判错自动类（标成自动类、被判成另一个自动类，
  如问回放判成上课时间）==0，因为判错自动类同样会把错误答案自动发给家长；满足的阈值里选自动回复率
  最高，同分取高阈值；自动回复率为 0 的不算。没有阈值满足就输出「没有合格阈值」，不退而求其次。
  不改配置，定了由人写进 本机配置.ini 的 [classify] threshold。

退出码：0 有推荐；1 没有合格阈值；2 参数、配置或文件有错；3 有模型调用出错，不给推荐。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from .classify import decide
from .config import CONFIG_PATH, ConfigError
from .eval import BACKEND_NOTES, load_dataset_or_report, make_backend, model_error_message, summarize, threshold_arg
from .model import predict

DEFAULT_THRESHOLDS = (0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.97, 0.99)
HELD_OUT_MARK = "留出"


def threshold_table(rows: Sequence[dict], results: Sequence, thresholds: Sequence[float]) -> List[dict]:
    table = []
    for threshold in sorted(set(thresholds)):
        summary = summarize(rows, [decide(result, threshold) for result in results])
        table.append(
            {
                "threshold": threshold,
                "misfire": summary["misfire"],
                "misfire_by_label": {
                    label: len(items) for label, items in summary["misfire_by_label"].items() if items
                },
                "auto_reply_rate": summary["auto_reply_rate"],
                "miss_rate": summary["miss_rate"],
                "auto_wrong_category": summary["auto_wrong_category"],
            }
        )
    return table


def recommend(table: Sequence[dict]) -> Optional[float]:
    """硬条件：misfire==0 且判错自动类==0；其中自动回复率最高的。没有就返回 None。"""
    usable = [
        row
        for row in table
        if row["misfire"] == 0 and row["auto_wrong_category"] == 0 and row["auto_reply_rate"]
    ]
    if not usable:
        return None
    return max(usable, key=lambda row: (row["auto_reply_rate"], row["threshold"]))["threshold"]


def format_table(table: Sequence[dict], recommended: Optional[float]) -> str:
    lines = ["阈值   misfire  判错自动类  自动回复率  漏答率"]
    for row in table:
        mark = "  <- 推荐" if row["threshold"] == recommended else ""
        lines.append(
            f"{row['threshold']:<6} {row['misfire']:<8} {row['auto_wrong_category']:<11} "
            f"{row['auto_reply_rate']!s:<11} {row['miss_rate']!s}{mark}"
        )
    return "\n".join(lines)


def _thresholds_arg(value: str) -> List[float]:
    return [threshold_arg(part) for part in value.split(",") if part.strip()]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python3 -m autoreply.tune", description="跑几组阈值，输出对比表")
    parser.add_argument("--set", dest="dataset", required=True, help="测试集 JSONL，只用合成集")
    parser.add_argument("--backend", choices=("cloud", "fake"), default="cloud")
    parser.add_argument("--thresholds", type=_thresholds_arg, default=list(DEFAULT_THRESHOLDS), help="逗号分隔")
    parser.add_argument("--out", help="另存一份 JSON（可不写）")
    return parser


def main(argv=None, config_path: Path = CONFIG_PATH) -> int:
    args = _parser().parse_args(argv)
    if HELD_OUT_MARK in Path(args.dataset).name:
        print("留出集不能用来调阈值，只能照合成集调（思考页里程碑 2「11/04 第二级改」第 ② 点）。", file=sys.stderr)
        return 2
    if not args.thresholds:
        print("--thresholds 至少写一个阈值。", file=sys.stderr)
        return 2

    try:
        backend = make_backend(args.backend, config_path)
    except ConfigError as exc:
        print(exc, file=sys.stderr)
        return 2
    rows = load_dataset_or_report(args.dataset)
    if rows is None:
        return 2

    results = [predict(row["text"], backend) for row in rows]
    table = threshold_table(rows, results, args.thresholds)
    errors = summarize(rows, [decide(result, args.thresholds[0]) for result in results])["model_errors"]
    recommended = None if errors["count"] else recommend(table)

    print(f"{Path(args.dataset).name}（{len(rows)} 条）后端 {args.backend}，规则层关")
    if args.backend == "fake":
        print(BACKEND_NOTES["fake"])
    print(format_table(table, recommended))

    if args.out:
        out = Path(args.out)
        payload = {
            "dataset": Path(args.dataset).name,
            "dataset_size": len(rows),
            "backend": args.backend,
            "backend_note": BACKEND_NOTES[args.backend],
            "rules_enabled": False,
            "table": table,
            "recommended_threshold": recommended,
            "model_errors": errors,
        }
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"写不了 {out}：{exc}", file=sys.stderr)
            return 2
        print(f"已存：{out}")

    if errors["count"]:
        print(model_error_message(errors, len(rows)) + "不给推荐。", file=sys.stderr)
        return 3
    if recommended is None:
        print("没有合格阈值：没有一档同时做到 misfire==0、判错自动类==0 且有自动回复，不给推荐。")
        return 1
    print(f"推荐阈值 {recommended}。没有写进配置；定了就写进 本机配置.ini 的 [classify] threshold。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
