"""在测试集上评分类效果，写一份 JSON 报告。

在 代码/ 目录下运行：
    python3 -m autoreply.eval --set 测试集/合成.jsonl --out 报告/eval.json
选项：
    --backend cloud|fake|rules-only   默认 cloud。读不到密钥就报错退出，不会静默退回 rules-only
    --no-rules                        关掉规则层，单独评模型层（定阈值时用）
    --threshold 0.95                  不写就读 本机配置.ini 的 [classify] threshold

口径（思考页 7.1 ⑧、里程碑 2「11/04 第二级改」）：
- misfire：标成转二讲 5 类或「都不是／拿不准」、却被判成自动的条数。
- 自动回复率：判成自动的文字消息 ÷ 全部文字消息（纯图片、语音等不算文字）。
  只算到分类这一步，第 4 步素材查找还没做，所以是上限。
- 漏答率：标成自动 4 类、却转了二讲的条数 ÷ 标成自动 4 类的条数。
- auto_wrong_category：标成自动类、被判成另一个自动类的条数。不算 misfire，但会发错答案，单列。
- misfire 以留出集为准，合成集结果只作参考。

退出码：0 跑完（misfire 大于 0 也是 0，门槛由看报告的人判）；2 参数、配置或文件有错；
3 有模型调用出错，这些条按转二讲算，没真正判过，misfire 不能当数（报告照样写出）。
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from .classify import AUTO, Decision, classify
from .config import CONFIG_PATH, ConfigError, load_model_config, load_threshold, parse_threshold
from .dataset_stats import AUTO_LABELS, HANDOFF_LABELS, UNSURE_LABEL, DatasetError, load_rows
from .model import Backend, CloudBackend, FakeBackend
from .redact import redact
from .rules import is_pure_non_text

BACKENDS = ("cloud", "fake", "rules-only")
BACKEND_NOTES = {
    "cloud": "云端模型",
    "fake": "假后端：看到几个词就判那一类，把握度由校验和决定。只验证流程能跑，数字没有含义",
    "rules-only": "没有模型：规则层没拦下的都判转二讲，所以 misfire 恒为 0、自动回复率恒为 0，不说明判得准",
}
AUTO_REPLY_NOTE = "只算到分类这一步，第 4 步素材查找还没做，所以是上限"
_SHOULD_HAND_OFF = HANDOFF_LABELS + (UNSURE_LABEL,)


def _rate(part: int, whole: int) -> Optional[float]:
    return round(part / whole, 4) if whole else None


def _detail(row: dict, decision: Decision) -> dict:
    # 报告里只放去标识化后的文字：以后可能换成真实消息。
    return {
        "id": row["id"],
        "label": row["label"],
        "predicted": decision.category,
        "confidence": decision.confidence,
        "mixed": row["mixed"],
        "tricky": row["tricky"],
        "text": redact(row["text"]),
    }


def summarize(rows: Sequence[dict], decisions: Sequence[Decision]) -> dict:
    """算 misfire、自动回复率、漏答率。eval 和 tune 共用同一套口径。"""
    misfires: Dict[str, List[dict]] = {label: [] for label in _SHOULD_HAND_OFF}
    wrong_category: List[dict] = []
    text_total = auto_text = should_auto = missed = 0
    for row, decision in zip(rows, decisions):
        is_auto = decision.decision == AUTO
        if not is_pure_non_text(row["text"]):
            text_total += 1
            auto_text += is_auto
        if row["label"] in AUTO_LABELS:
            should_auto += 1
            if not is_auto:
                missed += 1
            elif decision.category != row["label"]:
                wrong_category.append(_detail(row, decision))
        elif is_auto:
            misfires[row["label"]].append(_detail(row, decision))

    errors = Counter(decision.error for decision in decisions if decision.error)
    return {
        "misfire": sum(len(items) for items in misfires.values()),
        "misfire_by_label": misfires,
        "auto_reply_rate": _rate(auto_text, text_total),
        "auto_reply_count": auto_text,
        "text_message_count": text_total,
        "auto_reply_note": AUTO_REPLY_NOTE,
        "miss_rate": _rate(missed, should_auto),
        "miss_count": missed,
        "should_auto_count": should_auto,
        "auto_wrong_category": len(wrong_category),
        "auto_wrong_category_details": wrong_category,
        "model_errors": {"count": sum(errors.values()), "by_kind": dict(errors)},
    }


def evaluate(
    rows: Sequence[dict],
    backend: Optional[Backend],
    threshold: Optional[float],
    use_rules: bool = True,
) -> Tuple[List[Decision], List[float]]:
    decisions, seconds = [], []
    for row in rows:
        started = time.perf_counter()
        decisions.append(classify(row["text"], backend, threshold, use_rules=use_rules))
        seconds.append(time.perf_counter() - started)
    return decisions, seconds


def build_report(
    dataset: str,
    rows: Sequence[dict],
    decisions: Sequence[Decision],
    seconds: Sequence[float],
    backend_name: str,
    threshold: Optional[float],
    use_rules: bool,
) -> dict:
    report = {
        "dataset": Path(dataset).name,
        "dataset_size": len(rows),
        "backend": backend_name,
        "backend_note": BACKEND_NOTES[backend_name],
        "threshold": threshold,
        "rules_enabled": use_rules,
    }
    report.update(summarize(rows, decisions))
    report["latency_ms"] = {
        "median": round(statistics.median(seconds) * 1000, 3) if seconds else None,
        "max": round(max(seconds) * 1000, 3) if seconds else None,
    }
    return report


def threshold_arg(value: str) -> float:
    try:
        return parse_threshold(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from None


def make_backend(name: str, config_path: Path) -> Optional[Backend]:
    """读不到密钥时抛 ConfigError，让调用方报错退出。"""
    if name == "cloud":
        return CloudBackend(load_model_config(config_path))
    if name == "fake":
        return FakeBackend()
    return None


def load_dataset_or_report(path: str) -> Optional[List[dict]]:
    try:
        return load_rows(path)
    except DatasetError as exc:
        print("测试集读不了或格式有错：", file=sys.stderr)
        for problem in exc.problems:
            print(f"  {problem}", file=sys.stderr)
        return None


def model_error_message(errors: dict, total: int) -> str:
    message = (
        f"有 {errors['count']}/{total} 条模型调用出错（{errors['by_kind']}）。"
        "这些条按转二讲算，没有真正判过，这份结果不能当数。"
    )
    if "http_401" in errors["by_kind"]:
        message += "http_401 多半是密钥填错，查 本机配置.ini 的 api_key。"
    return message


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python3 -m autoreply.eval", description="在测试集上评分类效果")
    parser.add_argument("--set", dest="dataset", required=True, help="测试集 JSONL")
    parser.add_argument("--out", required=True, help="报告写到哪")
    parser.add_argument("--backend", choices=BACKENDS, default="cloud")
    parser.add_argument("--no-rules", action="store_true", help="关掉规则层，单独评模型层")
    parser.add_argument("--threshold", type=threshold_arg, help="把握度阈值，不写就读本机配置")
    return parser


def main(argv=None, config_path: Path = CONFIG_PATH) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.no_rules and args.backend == "rules-only":
        parser.error("rules-only 没有模型，再关掉规则层就没有东西可评了")

    try:
        backend = make_backend(args.backend, config_path)
        threshold = None
        if backend is not None:
            threshold = args.threshold if args.threshold is not None else load_threshold(config_path)
    except ConfigError as exc:
        print(exc, file=sys.stderr)
        return 2

    rows = load_dataset_or_report(args.dataset)
    if rows is None:
        return 2

    use_rules = not args.no_rules
    decisions, seconds = evaluate(rows, backend, threshold, use_rules)
    report = build_report(args.dataset, rows, decisions, seconds, args.backend, threshold, use_rules)

    out = Path(args.out)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"报告写不了 {out}：{exc}", file=sys.stderr)
        return 2

    print(
        f"{report['dataset']}（{report['dataset_size']} 条）后端 {args.backend} 阈值 {threshold} "
        f"规则层{'开' if use_rules else '关'}：misfire={report['misfire']} "
        f"自动回复率={report['auto_reply_rate']} 漏答率={report['miss_rate']} "
        f"自动类判错类={report['auto_wrong_category']} "
        f"耗时中位数={report['latency_ms']['median']}ms 最大={report['latency_ms']['max']}ms"
    )
    print(f"报告：{out}")
    if report["model_errors"]["count"]:
        print(model_error_message(report["model_errors"], len(rows)), file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
