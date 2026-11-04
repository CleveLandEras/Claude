"""评测、调阈值、本机配置。配置一律用临时文件，不读本机真实配置。"""
import json
import runpy
import shutil
from pathlib import Path

import pytest

from autoreply import eval as evaluation
from autoreply import tune
from autoreply.config import (
    DEFAULT_THRESHOLD,
    TEMPLATE_NAME,
    ConfigError,
    load_model_config,
    load_threshold,
    parse_threshold,
)
from autoreply.dataset_stats import ALL_LABELS, UNSURE_LABEL, load_rows
from autoreply.model import CloudBackend, FakeBackend, ModelError, predict

CODE_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC = CODE_ROOT / "测试集" / "合成.jsonl"
TEMPLATE = CODE_ROOT / TEMPLATE_NAME
KEY = "test-key-not-real"


def scores_json(**overrides):
    scores = {label: 0.0 for label in ALL_LABELS}
    scores.update(overrides)
    return json.dumps({"scores": scores}, ensure_ascii=False)


def row(row_id, text, label, mixed=False, tricky=False, parts=()):
    return {
        "id": row_id,
        "text": text,
        "label": label,
        "mixed": mixed,
        "tricky": tricky,
        "parts": list(parts),
        "note": "",
    }


# 文字 -> 模型答复。覆盖判对、判错类、漏答、误发（转二讲类和拿不准）、纯非文字。
SCRIPT = {
    "下节课几点": ("上课时间", {"上课时间": 0.99}),
    "回放呢": ("回放链接", {"上课时间": 0.99}),
    "作业哪天交": ("作业截止", {"作业截止": 0.3}),
    "你们这课真行": ("带情绪", {"上课时间": 0.99}),
    "在吗": (UNSURE_LABEL, {"回放链接": 0.99}),
    "[图片]": (UNSURE_LABEL, {UNSURE_LABEL: 0.9}),
}
ROWS = [row(f"t-{i}", text, label) for i, (text, (label, _)) in enumerate(SCRIPT.items())]


def scripted():
    return FakeBackend(lambda text: scores_json(**SCRIPT[text][1]))


def write_rows(path, rows):
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    return path


def write_config(path, key=KEY, threshold="0.9"):
    path.write_text(
        f"[model]\napi_key = {key}\nbase_url = https://example.invalid\nmodel = some-model\n"
        f"[classify]\nthreshold = {threshold}\n",
        encoding="utf-8",
    )
    return path


# ---- 报告口径 ----


def test_report_numbers_follow_the_definitions():
    decisions, seconds = evaluation.evaluate(ROWS, scripted(), 0.9, use_rules=False)
    report = evaluation.build_report("目录/小集.jsonl", ROWS, decisions, seconds, "fake", 0.9, False)

    assert report["misfire"] == 2
    assert [item["id"] for item in report["misfire_by_label"]["带情绪"]] == ["t-3"]
    assert [item["id"] for item in report["misfire_by_label"][UNSURE_LABEL]] == ["t-4"]
    assert report["misfire_by_label"]["退费"] == []

    # 文字 5 条（[图片] 不算），判自动 4 条
    assert (report["auto_reply_count"], report["text_message_count"], report["auto_reply_rate"]) == (4, 5, 0.8)
    # 自动类 3 条，漏答 1 条
    assert (report["miss_count"], report["should_auto_count"], report["miss_rate"]) == (1, 3, 0.3333)
    # 回放问成上课时间：不算误发，单列
    assert report["auto_wrong_category"] == 1
    assert report["auto_wrong_category_details"][0]["id"] == "t-1"

    assert report["dataset"] == "小集.jsonl"
    assert report["dataset_size"] == 6
    assert (report["backend"], report["threshold"], report["rules_enabled"]) == ("fake", 0.9, False)
    assert report["latency_ms"]["median"] >= 0
    assert report["latency_ms"]["max"] >= report["latency_ms"]["median"]
    assert report["model_errors"] == {"count": 0, "by_kind": {}}


def test_details_are_redacted():
    rows = [row("t-0", "我是王小测妈妈，13000000001，下节课几点", "带情绪")]
    backend = FakeBackend(scores_json(上课时间=0.99))
    decisions, seconds = evaluation.evaluate(rows, backend, 0.9, use_rules=False)
    text = json.dumps(evaluation.build_report("小集", rows, decisions, seconds, "fake", 0.9, False), ensure_ascii=False)
    assert "13000000001" not in text and "王小测" not in text


def test_empty_denominators_are_null():
    rows = [row("t-0", "[图片]", UNSURE_LABEL)]
    summary = evaluation.summarize(rows, evaluation.evaluate(rows, None, None)[0])
    assert summary["auto_reply_rate"] is None and summary["miss_rate"] is None


# ---- 命令行 ----


def run_eval(tmp_path, *args, config=None):
    out = tmp_path / "报告" / "eval.json"
    code = evaluation.main(["--out", str(out), *args], config_path=config or tmp_path / "没有这个文件.ini")
    return code, out


def test_rules_only_on_synthetic_set(tmp_path):
    code, out = run_eval(tmp_path, "--set", str(SYNTHETIC), "--backend", "rules-only")
    report = json.loads(out.read_text(encoding="utf-8"))
    assert code == 0
    assert report["misfire"] == 0
    assert report["auto_reply_rate"] == 0
    assert report["miss_rate"] == 1
    assert report["threshold"] is None
    assert report["dataset"] == "合成.jsonl"
    assert report["dataset_size"] == len(load_rows(SYNTHETIC))


def test_rules_only_is_not_the_default(tmp_path, capsys):
    """思考页第 5 步的命令不带 --backend；默认要是 cloud，否则没密钥也会假装通过。"""
    code, out = run_eval(tmp_path, "--set", str(SYNTHETIC))
    assert code == 2
    assert not out.exists()


@pytest.mark.parametrize("key", [None, "", "在这里填密钥"])
def test_cloud_without_key_stops_and_says_which_file(tmp_path, capsys, key):
    config = tmp_path / "本机配置.ini"
    if key is not None:
        write_config(config, key=key)
    code, out = run_eval(tmp_path, "--set", str(SYNTHETIC), "--backend", "cloud", config=config)
    err = capsys.readouterr().err
    assert code == 2
    assert not out.exists()
    assert "本机配置.ini" in err and "api_key" in err


def test_cloud_with_key_uses_config_threshold_and_never_prints_key(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(CloudBackend, "complete", lambda self, _text: scores_json(上课时间=0.99))
    rows = write_rows(tmp_path / "小集.jsonl", [row("t-0", "下节课几点", "上课时间")])
    config = write_config(tmp_path / "本机配置.ini", threshold="0.88")
    code, out = run_eval(tmp_path, "--set", str(rows), "--backend", "cloud", config=config)
    captured = capsys.readouterr()
    report_text = out.read_text(encoding="utf-8")
    assert code == 0
    assert json.loads(report_text)["threshold"] == 0.88
    for text in (report_text, captured.out, captured.err):
        assert KEY not in text


def test_model_errors_exit_nonzero_so_misfire_zero_is_not_a_false_pass(tmp_path, monkeypatch, capsys):
    def fail(_self, _text):
        raise ModelError("http_401")

    monkeypatch.setattr(CloudBackend, "complete", fail)
    rows = write_rows(tmp_path / "小集.jsonl", [row("t-0", "下节课几点", "上课时间")])
    config = write_config(tmp_path / "本机配置.ini")
    code, out = run_eval(tmp_path, "--set", str(rows), "--backend", "cloud", config=config)
    report = json.loads(out.read_text(encoding="utf-8"))
    err = capsys.readouterr().err
    assert code == 3
    assert report["misfire"] == 0
    assert report["model_errors"] == {"count": 1, "by_kind": {"http_401": 1}}
    assert "不能当数" in err and "api_key" in err and KEY not in err


def test_fake_no_rules_with_threshold(tmp_path):
    code, out = run_eval(tmp_path, "--set", str(SYNTHETIC), "--backend", "fake", "--no-rules", "--threshold", "0.8")
    report = json.loads(out.read_text(encoding="utf-8"))
    assert code == 0
    assert (report["backend"], report["threshold"], report["rules_enabled"]) == ("fake", 0.8, False)
    assert report["misfire"] > 0  # 假后端判不准，正好走到误发明细
    assert report["misfire"] == sum(len(items) for items in report["misfire_by_label"].values())


def test_rules_only_with_no_rules_is_refused(tmp_path, capsys):
    with pytest.raises(SystemExit) as caught:
        run_eval(tmp_path, "--set", str(SYNTHETIC), "--backend", "rules-only", "--no-rules")
    assert caught.value.code == 2


@pytest.mark.parametrize("value", ["0", "1.5", "abc", "nan"])
def test_bad_threshold_is_refused(tmp_path, capsys, value):
    with pytest.raises(SystemExit) as caught:
        run_eval(tmp_path, "--set", str(SYNTHETIC), "--backend", "fake", "--threshold", value)
    assert caught.value.code == 2


def test_bad_dataset_reports_error(tmp_path, capsys):
    code, out = run_eval(tmp_path, "--set", str(tmp_path / "没有.jsonl"), "--backend", "fake", "--threshold", "0.9")
    assert code == 2
    assert not out.exists()


# ---- 调阈值 ----


def test_threshold_table_and_recommendation():
    rows = [row("a", "下节课几点", "上课时间"), row("b", "你们这课真行", "带情绪"), row("c", "回放呢", "回放链接")]
    replies = {
        "下节课几点": scores_json(上课时间=0.95),
        "你们这课真行": scores_json(上课时间=0.8),
        "回放呢": scores_json(回放链接=0.7),
    }
    backend = FakeBackend(lambda text: replies[text])
    results = [predict(r["text"], backend) for r in rows]
    table = tune.threshold_table(rows, results, [0.7, 0.8, 0.9, 0.99])

    assert [line["misfire"] for line in table] == [1, 1, 0, 0]
    assert [line["auto_reply_rate"] for line in table] == [1.0, 0.6667, 0.3333, 0]
    assert table[0]["misfire_by_label"] == {"带情绪": 1}
    # 0.9 是零误发里自动回复率最高的；0.99 虽然零误发，但一条也不自动
    assert tune.recommend(table) == 0.9
    marked = [line for line in tune.format_table(table, 0.9).split("\n") if "推荐" in line]
    assert len(marked) == 1 and marked[0].startswith("0.9 ")


def tune_row(threshold, misfire, wrong, rate):
    return {"threshold": threshold, "misfire": misfire, "auto_wrong_category": wrong, "auto_reply_rate": rate}


def test_recommend_picks_highest_auto_reply_rate_among_qualified():
    table = [
        tune_row(0.7, 1, 0, 0.9),  # misfire 不为 0
        tune_row(0.8, 0, 0, 0.6),
        tune_row(0.9, 0, 0, 0.4),
        tune_row(0.99, 0, 0, 0),  # 一条也不自动，不算
    ]
    assert tune.recommend(table) == 0.8


def test_recommend_skips_threshold_with_wrong_auto_category_even_if_misfire_is_zero():
    # 用真实打分走一遍：回放被判成上课时间，misfire 为 0，但错误答案会自动发出去
    rows = [row("a", "下节课几点", "上课时间"), row("b", "回放呢", "回放链接")]
    replies = {"下节课几点": scores_json(上课时间=0.95), "回放呢": scores_json(上课时间=0.8)}
    backend = FakeBackend(lambda text: replies[text])
    results = [predict(r["text"], backend) for r in rows]
    table = tune.threshold_table(rows, results, [0.7, 0.9])

    assert [(line["misfire"], line["auto_wrong_category"], line["auto_reply_rate"]) for line in table] == [
        (0, 1, 1.0),
        (0, 0, 0.5),
    ]
    # 0.7 自动回复率更高，但有判错自动类，不能选；只能选 0.9
    assert tune.recommend(table) == 0.9
    assert "判错自动类" in tune.format_table(table, 0.9).split("\n")[0]


def test_recommend_none_when_nothing_qualifies():
    assert tune.recommend([tune_row(0.9, 1, 0, 0.5)]) is None
    assert tune.recommend([tune_row(0.9, 0, 1, 0.5)]) is None
    assert tune.recommend([tune_row(0.9, 0, 0, 0)]) is None


def test_tune_says_no_qualified_threshold_instead_of_picking_one(tmp_path, monkeypatch, capsys):
    # 回放永远被判成上课时间：所有阈值要么判错自动类，要么一条也不自动
    path = write_rows(tmp_path / "小集.jsonl", [row("t-0", "回放呢", "回放链接")])
    monkeypatch.setattr(tune, "make_backend", lambda _name, _path: FakeBackend(lambda _text: scores_json(上课时间=0.95)))
    out = tmp_path / "tune.json"
    code = tune.main(
        ["--set", str(path), "--backend", "fake", "--thresholds", "0.7,0.9,0.99", "--out", str(out)],
        config_path=tmp_path / "无.ini",
    )
    printed = capsys.readouterr().out
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert code == 1
    assert "没有合格阈值" in printed
    assert "推荐阈值" not in printed and "<- 推荐" not in printed
    assert payload["recommended_threshold"] is None
    assert [line["auto_wrong_category"] for line in payload["table"]] == [1, 1, 0]


def test_tune_runs_on_fake_and_asks_the_model_once_per_row(tmp_path, monkeypatch, capsys):
    calls = []
    original = FakeBackend.complete

    def counted(self, text):
        calls.append(text)
        return original(self, text)

    monkeypatch.setattr(FakeBackend, "complete", counted)
    out = tmp_path / "tune.json"
    code = tune.main(
        ["--set", str(SYNTHETIC), "--backend", "fake", "--thresholds", "0.6,0.8,0.95", "--out", str(out)],
        config_path=tmp_path / "没有这个文件.ini",
    )
    printed = capsys.readouterr().out
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert code in (0, 1)
    assert len(calls) == len(load_rows(SYNTHETIC))
    assert [line["threshold"] for line in payload["table"]] == [0.6, 0.8, 0.95]
    assert payload["rules_enabled"] is False
    assert "misfire" in printed and "0.95" in printed and "只验证流程能跑" in printed


def test_tune_refuses_held_out_set_without_opening_it(tmp_path, capsys):
    path = tmp_path / "留出.jsonl"  # 故意不建这个文件：拒绝发生在读文件之前
    assert tune.main(["--set", str(path), "--backend", "fake"], config_path=tmp_path / "无.ini") == 2
    assert "留出集" in capsys.readouterr().err


def test_tune_cloud_without_key_stops(tmp_path, capsys):
    assert tune.main(["--set", str(SYNTHETIC), "--backend", "cloud"], config_path=tmp_path / "无.ini") == 2
    assert "api_key" in capsys.readouterr().err


def test_tune_gives_no_recommendation_when_model_errors(tmp_path, monkeypatch, capsys):
    def fail(_self, _text):
        raise ModelError("timeout")

    monkeypatch.setattr(FakeBackend, "complete", fail)
    rows = write_rows(tmp_path / "小集.jsonl", [row("t-0", "下节课几点", "上课时间")])
    assert tune.main(["--set", str(rows), "--backend", "fake"], config_path=tmp_path / "无.ini") == 3
    assert "不给推荐" in capsys.readouterr().err


# ---- 本机配置 ----


def test_template_alone_is_not_a_key(tmp_path):
    copy = tmp_path / "本机配置.ini"
    shutil.copy(TEMPLATE, copy)
    with pytest.raises(ConfigError) as caught:
        load_model_config(copy)
    assert TEMPLATE_NAME in str(caught.value) and "api_key" in str(caught.value)
    assert load_threshold(copy) == DEFAULT_THRESHOLD


def test_template_filled_in_works(tmp_path):
    text = TEMPLATE.read_text(encoding="utf-8").replace("api_key =\n", f"api_key = {KEY}\n")
    copy = tmp_path / "本机配置.ini"
    copy.write_text(text, encoding="utf-8")
    config = load_model_config(copy)
    assert config.api_key == KEY
    assert config.base_url.startswith("https://")
    assert config.model and config.timeout_seconds > 0


def test_percent_in_key_and_bom_are_fine(tmp_path):
    path = tmp_path / "本机配置.ini"
    path.write_text(
        "﻿[model]\napi_key = ab%cd\nbase_url = https://example.invalid/\nmodel = m\n", encoding="utf-8"
    )
    config = load_model_config(path)
    assert config.api_key == "ab%cd"
    assert config.base_url == "https://example.invalid"
    assert load_threshold(path) == DEFAULT_THRESHOLD


@pytest.mark.parametrize(
    "body, word",
    [
        ("[model]\napi_key = k\nbase_url = http://example.invalid\nmodel = m\n", "base_url"),
        ("[model]\napi_key = k\nmodel = m\n", "base_url"),
        ("[model]\napi_key = k\nbase_url = https://example.invalid\n", "model"),
        ("[model]\napi_key = k\nbase_url = https://example.invalid\nmodel = m\ntimeout_seconds = abc\n", "timeout"),
        ("[model]\napi_key = k\nbase_url = https://example.invalid\nmodel = m\ntimeout_seconds = 0\n", "timeout"),
        ("这不是配置文件\n", "写法有错"),
    ],
)
def test_bad_model_config_is_reported(tmp_path, body, word):
    path = tmp_path / "本机配置.ini"
    path.write_text(body, encoding="utf-8")
    with pytest.raises(ConfigError) as caught:
        load_model_config(path)
    assert word in str(caught.value)


def test_localhost_http_is_allowed_for_local_debugging(tmp_path):
    path = tmp_path / "本机配置.ini"
    path.write_text("[model]\napi_key = k\nbase_url = http://localhost:8000\nmodel = m\n", encoding="utf-8")
    assert load_model_config(path).base_url == "http://localhost:8000"


def test_bad_threshold_in_config_is_reported(tmp_path):
    path = write_config(tmp_path / "本机配置.ini", threshold="2")
    with pytest.raises(ConfigError):
        load_threshold(path)


@pytest.mark.parametrize("value", ["0", "-0.1", "1.01", "nan", "abc"])
def test_parse_threshold_rejects(value):
    with pytest.raises(ValueError):
        parse_threshold(value)


def test_config_file_is_ignored_by_git():
    assert "本机配置.ini" in (CODE_ROOT / ".gitignore").read_text(encoding="utf-8").split("\n")


def test_source_zip_never_contains_local_config(tmp_path):
    root = tmp_path / "代码"
    (root / "autoreply").mkdir(parents=True)
    (root / "packaging").mkdir()
    (root / "pyproject.toml").write_text("", encoding="utf-8")
    (root / "autoreply" / "app.py").write_text("", encoding="utf-8")
    (root / "autoreply" / "本机配置.ini").write_text(f"api_key = {KEY}", encoding="utf-8")
    (root / "packaging" / "本机配置.ini").write_text(f"api_key = {KEY}", encoding="utf-8")
    (root / "本机配置.ini").write_text(f"api_key = {KEY}", encoding="utf-8")

    script = runpy.run_path(str(CODE_ROOT / "packaging" / "做源码包.py"))
    names = [path.name for path in script["source_files"](root)]
    assert "app.py" in names
    assert "本机配置.ini" not in names
