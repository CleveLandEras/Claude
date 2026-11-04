"""记录和核对页。用 fake 后端跑一遍合成集，核对条数和手机号。合成集以外的句子是这里自造的。"""
import json
import re
import zipfile
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path

import pytest

from autoreply import collectlog
from autoreply.classify import AUTO, SOURCE_RULES, Decision, classify
from autoreply.dataset_stats import load_rows
from autoreply.guards import QUEUE, REMIND, SEND, GuardConfig, Guards
from autoreply.model import FakeBackend
from autoreply.notify import build_reminder
from autoreply.records import (
    AUTO_ROW_CLASS,
    CHECK_WRONG,
    RecordError,
    add_record,
    day_file,
    mark_check,
    page_file,
    parent_code,
    read_day,
    render_check_page,
    records_dir,
    write_check_page,
)
from autoreply.rules import HANDOFF

DATASET = Path(__file__).resolve().parents[1] / "测试集" / "合成.jsonl"
FAKE_THRESHOLD = 0.6
PLACEHOLDER_REPLY = "（测试占位回复）"
PLACEHOLDER_SOURCE = "（测试占位出处）"
DAY = date(2026, 11, 4)
MORNING = datetime(2026, 11, 4, 8, 0, 0)

_FULL_WIDTH = str.maketrans("０１２３４５６７８９", "0123456789")
_SEPARATORS = re.compile(r"[-－—– \t　]")
_PHONE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")


def normalize_digits(text):
    return _SEPARATORS.sub("", text.translate(_FULL_WIDTH))


def phones_in(text):
    return set(_PHONE.findall(normalize_digits(text)))


def files_containing_phones(root, phones):
    """逐个文件搜；zip 也拆开搜。独立于 redact，换写法的手机号也搜得到。"""
    found = {}
    for path in Path(root).rglob("*"):
        if not path.is_file():
            continue
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as archive:
                content = "".join(
                    archive.read(name).decode("utf-8") for name in archive.namelist()
                )
        else:
            content = path.read_text(encoding="utf-8")
        hits = {phone for phone in phones if phone in normalize_digits(content)}
        if hits:
            found[path] = hits
    return found


class _RowCounter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.auto_rows = 0
        self.scripts = 0

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.scripts += 1
        if tag == "tr" and dict(attrs).get("class") == AUTO_ROW_CLASS:
            self.auto_rows += 1


def count_auto_rows(page_text):
    counter = _RowCounter()
    counter.feed(page_text)
    return counter.auto_rows


def auto_decision(category="上课时间"):
    return Decision(AUTO, category, "模型层", 0.97, {category: 0.97})


def add_auto(tmp_path, text="下节课几点", at=MORNING, **kwargs):
    kwargs.setdefault("reply", PLACEHOLDER_REPLY)
    kwargs.setdefault("source", PLACEHOLDER_SOURCE)
    return add_record(
        SEND, "测试家长甲", text, auto_decision(), at,
        directory=tmp_path / "记录", log_directory=tmp_path / "日志", **kwargs,
    )


def run_dataset(rows, root):
    """合成集走一遍：连发合并、分类、防出错、提醒内容、记录。只走逻辑，不收发真实消息。"""
    clock_now = [MORNING]
    guards = Guards(GuardConfig(holidays=frozenset({date(2026, 10, 1)})), lambda: clock_now[0])
    backend = FakeBackend()
    records = root / "记录"
    logs = root / "日志"
    counts = {SEND: 0, REMIND: 0, QUEUE: 0}
    for index, row in enumerate(rows):
        parent = f"测试家长{index}"
        guards.add_parent_message(parent, row["text"])
        clock_now[0] += timedelta(seconds=45)
        merged = guards.pop_ready()
        assert [message.parent for message in merged] == [parent]
        message = merged[0]
        decision = classify(message.text, backend, FAKE_THRESHOLD, known_names=[parent])
        if decision.decision == AUTO:
            verdict = guards.check_send(parent)
            action = verdict.action
            if verdict.paused_now:
                guards.resume()
        else:
            action = REMIND
        if action == REMIND:
            build_reminder(parent, message.text, decision, message.first_at)
        reply, source = (PLACEHOLDER_REPLY, PLACEHOLDER_SOURCE) if action == SEND else (None, None)
        add_record(
            action, parent, message.text, decision, clock_now[0], reply=reply, source=source,
            directory=records, log_directory=logs,
        )
        if action == SEND:
            guards.record_sent(parent)
        counts[action] += 1
        clock_now[0] += timedelta(seconds=15)
    page = write_check_page(DAY, clock_now[0], directory=records, log_directory=logs)
    return counts, page


@pytest.fixture(scope="module")
def dataset_rows():
    return load_rows(str(DATASET))


@pytest.fixture(scope="module")
def dataset_run(dataset_rows, tmp_path_factory):
    root = tmp_path_factory.mktemp("合成集")
    counts, page = run_dataset(dataset_rows, root)
    return root, counts, page


# ---- 跑一遍合成集 ----


def test_dataset_run_covers_auto_and_handoff(dataset_rows, dataset_run):
    _, counts, _ = dataset_run
    assert counts[SEND] > 0
    assert counts[REMIND] > 0
    assert sum(counts.values()) == len(dataset_rows)


def test_check_page_rows_equal_auto_sent(dataset_run):
    _, counts, page = dataset_run
    page_text = page.read_text(encoding="utf-8")
    assert count_auto_rows(page_text) == counts[SEND]
    assert f'<b id="auto-count">{counts[SEND]}</b>' in page_text


def test_every_message_has_one_record(dataset_rows, dataset_run):
    root, counts, _ = dataset_run
    records = read_day(DAY, root / "记录")
    assert len(records.rows) == len(dataset_rows)
    assert records.bad_lines == 0
    assert sum(row["action"] == SEND for row in records.rows) == counts[SEND]


def test_dataset_really_contains_phones_and_scanner_finds_them(dataset_rows, tmp_path):
    phones = set().union(*(phones_in(row["text"]) for row in dataset_rows))
    assert len(phones) >= 5
    leak = tmp_path / "漏了.jsonl"
    leak.write_text("回放发到 130-0000-0005\n", encoding="utf-8")
    assert files_containing_phones(tmp_path, {"13000000005"}) == {leak: {"13000000005"}}


def test_written_files_contain_no_dataset_phone(dataset_rows, dataset_run):
    root, _, _ = dataset_run
    phones = set().union(*(phones_in(row["text"]) for row in dataset_rows))
    written = [path for path in root.rglob("*") if path.is_file()]
    assert {path.suffix for path in written} == {".jsonl", ".html", ".log"}
    assert files_containing_phones(root, phones) == {}


def test_collected_log_zip_contains_no_dataset_phone(dataset_rows, dataset_run, tmp_path):
    root, _, _ = dataset_run
    phones = set().union(*(phones_in(row["text"]) for row in dataset_rows))
    target = collectlog.collect(root / "日志", tmp_path)
    assert target.suffix == ".zip"
    assert files_containing_phones(tmp_path, phones) == {}


# ---- 去标识化 ----


@pytest.mark.parametrize(
    "written_phone",
    ["13000000009", "130-0000-0009", "130 0000 0009", "+86 13000000009", "１３０００００００９"],
)
def test_phone_in_any_form_is_removed_from_all_files(tmp_path, written_phone):
    add_auto(tmp_path, f"回放发到 {written_phone}", reply=f"已发到 {written_phone}")
    write_check_page(DAY, MORNING, directory=tmp_path / "记录", log_directory=tmp_path / "日志")
    assert files_containing_phones(tmp_path, {"13000000009"}) == {}


def test_parent_name_and_known_child_name_are_not_written(tmp_path):
    decision = classify("思涵最近成绩不好，我要投诉", None, None)
    add_record(
        REMIND, "王小测妈妈", "我是王小测妈妈，思涵最近成绩不好，我要投诉", decision, MORNING,
        known_names=["思涵"], directory=tmp_path / "记录", log_directory=tmp_path / "日志",
    )
    add_auto(tmp_path)
    write_check_page(DAY, MORNING, directory=tmp_path / "记录", log_directory=tmp_path / "日志")
    for path in tmp_path.rglob("*"):
        if path.is_file():
            content = path.read_text(encoding="utf-8")
            for name in ("王小测", "思涵", "测试家长甲"):
                assert name not in content


def test_parent_code_is_stable_and_differs_between_parents():
    assert parent_code("测试家长甲") == parent_code("测试家长甲")
    assert parent_code("测试家长甲") != parent_code("测试家长乙")
    assert "测试家长" not in parent_code("测试家长甲")


def test_log_lines_have_events_only(tmp_path):
    add_auto(tmp_path, "下节课几点")
    log_text = (tmp_path / "日志" / "autoreply.log").read_text(encoding="utf-8")
    assert "record added" in log_text
    assert "下节课几点" not in log_text


# ---- 记录字段 ----


def test_record_has_all_plan_columns(tmp_path):
    record_id = add_auto(tmp_path)
    row = read_day(DAY, tmp_path / "记录").rows[0]
    assert row["id"] == record_id
    assert row["time"] == "2026-11-04 08:00:00"
    assert row["parent"] == parent_code("测试家长甲")
    assert row["text"] == "下节课几点"
    assert row["category"] == "上课时间"
    assert row["confidence"] == 0.97
    assert row["action"] == SEND
    assert row["reply"] == PLACEHOLDER_REPLY
    assert row["source"] == PLACEHOLDER_SOURCE
    assert row["check"] is None


@pytest.mark.parametrize(
    "reply,source", [(None, "出处"), ("回复", None), ("", ""), (None, None)]
)
def test_auto_record_without_reply_or_source_is_refused(tmp_path, reply, source):
    with pytest.raises(RecordError):
        add_auto(tmp_path, reply=reply, source=source)
    assert not day_file(DAY, tmp_path / "记录").exists()


def test_handoff_and_queue_records_need_no_reply(tmp_path):
    decision = Decision(HANDOFF, "退费", SOURCE_RULES)
    for action in (REMIND, QUEUE):
        add_record(
            action, "测试家长甲", "我要退费", decision, MORNING,
            directory=tmp_path, log_directory=tmp_path,
        )
    assert [row["action"] for row in read_day(DAY, tmp_path).rows] == [REMIND, QUEUE]


def test_unknown_action_is_refused(tmp_path):
    with pytest.raises(RecordError):
        add_record(
            "乱写", "测试家长甲", "下节课几点", auto_decision(), MORNING,
            directory=tmp_path, log_directory=tmp_path,
        )


def test_records_dir_follows_env(tmp_path):
    assert records_dir({"AUTOREPLY_RECORDS_DIR": str(tmp_path)}) == tmp_path


# ---- 核对页 ----


def make_page(tmp_path, now=MORNING, **kwargs):
    path = write_check_page(
        DAY, now, directory=tmp_path / "记录", log_directory=tmp_path / "日志", **kwargs
    )
    return path.read_text(encoding="utf-8")


def test_page_lists_only_today_auto_sent(tmp_path):
    add_auto(tmp_path, "今天的自动回复")
    add_auto(tmp_path, "昨天的自动回复", at=MORNING - timedelta(days=1))
    add_record(
        REMIND, "测试家长甲", "今天转二讲的", Decision(HANDOFF, "退费", SOURCE_RULES), MORNING,
        directory=tmp_path / "记录", log_directory=tmp_path / "日志",
    )
    add_record(
        QUEUE, "测试家长甲", "今天排队的", auto_decision(), MORNING,
        directory=tmp_path / "记录", log_directory=tmp_path / "日志",
    )
    page = make_page(tmp_path)
    assert count_auto_rows(page) == 1
    assert "今天的自动回复" in page
    assert "昨天的自动回复" not in page
    assert "今天转二讲的" not in page
    assert "今天排队的" not in page
    assert '<b id="auto-count">1</b>' in page
    assert "转二讲 1 条" in page
    assert "排队 1 条" in page


def test_empty_day_page_says_so(tmp_path):
    page = make_page(tmp_path)
    assert count_auto_rows(page) == 0
    assert "今天还没有自动回复" in page
    assert page_file(DAY, tmp_path / "记录").is_file()


def test_page_escapes_html_in_parent_text(tmp_path):
    add_auto(tmp_path, '<script>alert("x")</script>', reply="<img src=x onerror=alert(1)>")
    page = make_page(tmp_path)
    counter = _RowCounter()
    counter.feed(page)
    assert counter.scripts == 0
    assert "<img" not in page
    assert "&lt;script&gt;" in page


def test_page_shows_placeholders_as_text(tmp_path):
    add_auto(tmp_path, "回放发到 13000000009")
    assert "&lt;手机号&gt;" in make_page(tmp_path)


def test_each_auto_row_has_recall_notice_unverified_by_default(tmp_path):
    add_auto(tmp_path)
    page = make_page(tmp_path)
    assert "撤回提醒" in page
    assert "撤回时限未查实" in page


def test_recall_notice_uses_configured_window(tmp_path):
    add_auto(tmp_path)
    within = make_page(tmp_path, MORNING + timedelta(seconds=60), recall_window_seconds=120)
    assert "08:02:00 前手动撤回" in within
    after = make_page(tmp_path, MORNING + timedelta(seconds=121), recall_window_seconds=120)
    assert "已过撤回时限" in after


def test_page_is_self_contained(tmp_path):
    add_auto(tmp_path)
    page = make_page(tmp_path)
    assert "http://" not in page
    assert "https://" not in page
    assert '<meta charset="utf-8">' in page


# ---- 核对结果 ----


def test_mark_check_updates_only_that_row_and_shows_on_page(tmp_path):
    first = add_auto(tmp_path, "第一条")
    second = add_auto(tmp_path, "第二条")
    assert "未核对" in make_page(tmp_path)

    mark_check(second, CHECK_WRONG, DAY, tmp_path / "记录")

    rows = {row["id"]: row for row in read_day(DAY, tmp_path / "记录").rows}
    assert rows[first]["check"] is None
    assert rows[second]["check"] == CHECK_WRONG
    assert f"<td>{CHECK_WRONG}</td>" in make_page(tmp_path)


@pytest.mark.parametrize("record_id,result", [("没有这条", "对"), (None, "可能吧")])
def test_mark_check_refuses_bad_input(tmp_path, record_id, result):
    real_id = add_auto(tmp_path)
    with pytest.raises(RecordError):
        mark_check(record_id or real_id, result, DAY, tmp_path / "记录")


def test_mark_check_on_day_without_records_is_refused(tmp_path):
    with pytest.raises(RecordError):
        mark_check("abc", "对", DAY, tmp_path)


# ---- 读不了的行 ----


def test_bad_line_is_reported_not_counted_and_survives_mark_check(tmp_path):
    record_id = add_auto(tmp_path)
    path = day_file(DAY, tmp_path / "记录")
    with path.open("a", encoding="utf-8") as handle:
        handle.write('{"写到一半断电\n')

    records = read_day(DAY, tmp_path / "记录")
    assert (len(records.rows), records.bad_lines) == (1, 1)
    page = render_check_page(records, DAY, MORNING)
    assert count_auto_rows(page) == 1
    assert "有 1 行记录读不了" in page

    mark_check(record_id, "对", DAY, tmp_path / "记录")
    assert '{"写到一半断电' in path.read_text(encoding="utf-8")


def test_jsonl_lines_are_one_record_each_even_with_newlines_in_text(tmp_path):
    add_auto(tmp_path, "老师\n下节课\n几点")
    lines = day_file(DAY, tmp_path / "记录").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["text"] == "老师\n下节课\n几点"
