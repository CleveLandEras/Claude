import json
import re
from pathlib import Path

from autoreply import dataset_stats as ds

DATASET = Path(__file__).resolve().parent.parent / "测试集" / "合成.jsonl"
PHONE_LIKE = re.compile(r"(?<!\d)1\d{2}[- ]?\d{4}[- ]?\d{4}(?!\d)")
FICTIONAL_PHONE = re.compile(r"^130-?0000-?000\d$")


def make_rows(label, count, start=0, mixed=False, tricky=False, parts=None):
    return [
        {
            "id": f"{label}-{mixed}-{tricky}-{start + index}",
            "text": f"{label} {mixed} {tricky} 第 {start + index} 句",
            "label": label,
            "mixed": mixed,
            "tricky": tricky,
            "parts": parts or [],
            "note": "",
        }
        for index in range(count)
    ]


def enough_rows():
    """刚好达标：普通条满足全部门槛，另加混合、刁钻各 30 条。"""
    rows = []
    for label in ds.HANDOFF_LABELS:
        rows += make_rows(label, ds.MIN_PER_HANDOFF)
    for label in ds.AUTO_LABELS:
        rows += make_rows(label, 38)
    rows += make_rows("带情绪", 30, mixed=True, parts=["上课时间", "带情绪"])
    rows += make_rows("投诉", 30, tricky=True)
    return rows


def write_jsonl(tmp_path, rows):
    path = tmp_path / "集.jsonl"
    lines = [json.dumps(row, ensure_ascii=False) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


def test_summarize_counts_by_label_and_flag():
    rows = make_rows("退费", 2) + make_rows("退费", 1, tricky=True)
    rows += make_rows("带情绪", 1, mixed=True, tricky=True, parts=["上课时间", "带情绪"])
    summary = ds.summarize(rows)
    assert summary["all"]["退费"] == 3
    assert summary["plain"]["退费"] == 2
    assert summary["tricky"]["退费"] == 1
    assert summary["mixed"]["带情绪"] == 1
    assert summary["plain"]["带情绪"] == 0


def test_enough_rows_pass_with_exit_0(tmp_path, capsys):
    assert ds.main([write_jsonl(tmp_path, enough_rows())]) == 0
    assert "结论：全部达标" in capsys.readouterr().out


def test_one_class_short_fails_with_exit_1(tmp_path, capsys):
    rows = [row for row in enough_rows() if row["id"] != "退费-False-False-0"]
    assert ds.main([write_jsonl(tmp_path, rows)]) == 1
    assert "不过  转二讲 5 类每类 ≥ 30（最少的一类 29）" in capsys.readouterr().out


def test_tricky_rows_do_not_fill_the_plain_requirement(tmp_path, capsys):
    rows = [row for row in enough_rows() if row["id"] != "续报-False-False-0"]
    rows += make_rows("续报", 1, tricky=True)
    assert ds.main([write_jsonl(tmp_path, rows)]) == 1
    assert "不过  扣掉混合和刁钻后仍满足前三条" in capsys.readouterr().out


def test_format_errors_exit_2(tmp_path, capsys):
    good = make_rows("退费", 1)[0]
    bad_rows = [
        dict(good, label="闲聊"),
        dict(good, mixed=True, parts=[]),
        dict(good, label="上课时间", mixed=True, parts=["上课时间", "带情绪"]),
        dict(good, parts=["退费"]),
    ]
    for row in bad_rows:
        assert ds.main([write_jsonl(tmp_path, [row])]) == 2
    assert ds.main([write_jsonl(tmp_path, [good, dict(good, id="另一个")])]) == 2
    assert "原话重复" in capsys.readouterr().err
    assert ds.main([str(tmp_path / "没有这个文件.jsonl")]) == 2


def test_synthetic_dataset_meets_all_thresholds():
    summary = ds.summarize(ds.load_rows(DATASET))
    failed = [text for passed, text in ds.check_thresholds(summary) if not passed]
    assert failed == []


def test_synthetic_dataset_only_uses_fictional_phone_numbers():
    numbers = [
        match
        for row in ds.load_rows(DATASET)
        for match in PHONE_LIKE.findall(row["text"])
    ]
    assert numbers, "测试集里应有带手机号的句子，供后面的去标识化用"
    assert [n for n in numbers if not FICTIONAL_PHONE.match(n)] == []
