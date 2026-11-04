"""防出错规则：每条规则都有触发和不触发的用例。全部用模拟时钟，不真的等待。"""
from datetime import date, datetime, time, timedelta

import pytest

from autoreply.config import ConfigError
from autoreply.guards import (
    QUEUE,
    REASON_HOLIDAY,
    REASON_NIGHT,
    REASON_NO_HOLIDAY_LIST,
    REASON_PAUSED,
    REASON_RATE_ALL,
    REASON_RATE_PARENT,
    REASON_TEACHER,
    RECALL_EXPIRED,
    RECALL_OPEN,
    RECALL_UNVERIFIED,
    REMIND,
    SEND,
    GuardConfig,
    Guards,
    load_guard_config,
    recall_notice,
)

NATIONAL_DAY = date(2026, 10, 1)
WEDNESDAY_NOON = datetime(2026, 11, 4, 12, 0, 0)


class FakeClock:
    def __init__(self, start=WEDNESDAY_NOON):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += timedelta(seconds=seconds)

    def set(self, moment):
        self.now = moment


def make_guards(start=WEDNESDAY_NOON, **overrides):
    overrides.setdefault("holidays", frozenset({NATIONAL_DAY}))
    clock = FakeClock(start)
    return Guards(GuardConfig(**overrides), clock), clock


def test_default_numbers_match_plan():
    config = GuardConfig()
    assert config.merge_seconds == 45
    assert config.teacher_active_seconds == 300
    assert (config.night_start, config.night_end) == (time(22, 0), time(7, 30))
    assert (config.max_per_parent_per_hour, config.max_all_per_hour) == (3, 30)


def test_ordinary_daytime_message_can_send():
    guards, _ = make_guards()
    assert guards.check_send("甲").action == SEND


# ---- 不抢答 ----


def test_teacher_replied_within_5_minutes_blocks_send():
    guards, clock = make_guards()
    guards.note_teacher_message("甲")
    clock.advance(299)
    verdict = guards.check_send("甲")
    assert (verdict.action, verdict.reason) == (REMIND, REASON_TEACHER)


def test_exactly_5_minutes_still_counts_as_replying():
    guards, clock = make_guards()
    guards.note_teacher_message("甲")
    clock.advance(300)
    assert guards.check_send("甲").action == REMIND


def test_teacher_replied_over_5_minutes_ago_does_not_block():
    guards, clock = make_guards()
    guards.note_teacher_message("甲")
    clock.advance(301)
    assert guards.check_send("甲").action == SEND


def test_teacher_in_another_conversation_does_not_block():
    guards, _ = make_guards()
    guards.note_teacher_message("甲")
    assert guards.check_send("乙").action == SEND


def test_check_again_before_send_catches_teacher_reply():
    guards, _ = make_guards()
    assert guards.check_send("甲").action == SEND
    guards.note_teacher_message("甲")
    assert guards.check_send("甲").action == REMIND


# ---- 一键暂停与恢复 ----


def test_pause_blocks_all_parents():
    guards, _ = make_guards()
    guards.pause()
    assert guards.paused
    for parent in ("甲", "乙"):
        verdict = guards.check_send(parent)
        assert (verdict.action, verdict.reason) == (REMIND, REASON_PAUSED)
        assert verdict.paused_now is False


def test_not_paused_by_default_and_resume_restores():
    guards, _ = make_guards()
    assert not guards.paused
    guards.pause()
    guards.resume()
    assert not guards.paused
    assert guards.check_send("甲").action == SEND


# ---- 夜间、节假日排队 ----


@pytest.mark.parametrize(
    "clock_time",
    [time(22, 0, 0), time(23, 59, 59), time(0, 0, 0), time(7, 29, 59)],
)
def test_night_queues(clock_time):
    guards, _ = make_guards(datetime.combine(date(2026, 11, 4), clock_time))
    verdict = guards.check_send("甲")
    assert (verdict.action, verdict.reason) == (QUEUE, REASON_NIGHT)


@pytest.mark.parametrize("clock_time", [time(7, 30, 0), time(21, 59, 59)])
def test_daytime_edges_do_not_queue(clock_time):
    guards, _ = make_guards(datetime.combine(date(2026, 11, 4), clock_time))
    assert guards.check_send("甲").action == SEND


def test_holiday_queues_in_daytime():
    guards, _ = make_guards(datetime(2026, 10, 1, 12, 0, 0))
    verdict = guards.check_send("甲")
    assert (verdict.action, verdict.reason) == (QUEUE, REASON_HOLIDAY)


def test_day_after_holiday_does_not_queue():
    guards, _ = make_guards(datetime(2026, 10, 2, 12, 0, 0))
    assert guards.check_send("甲").action == SEND


def test_no_holiday_list_does_not_send():
    guards, _ = make_guards(holidays=None)
    verdict = guards.check_send("甲")
    assert (verdict.action, verdict.reason) == (QUEUE, REASON_NO_HOLIDAY_LIST)


def test_holiday_list_of_another_year_does_not_send():
    guards, _ = make_guards(datetime(2027, 3, 3, 12, 0, 0))
    verdict = guards.check_send("甲")
    assert (verdict.action, verdict.reason) == (QUEUE, REASON_NO_HOLIDAY_LIST)


def test_queue_is_not_sent_when_morning_comes():
    guards, clock = make_guards(datetime(2026, 11, 4, 23, 0, 0))
    guards.add_parent_message("甲", "下节课几点")
    clock.advance(45)
    message = guards.pop_ready()[0]
    assert guards.check_send("甲").action == QUEUE
    guards.enqueue(message)

    clock.set(datetime(2026, 11, 5, 8, 0, 0))
    assert guards.pop_ready() == []
    assert guards.queued() == (message,)
    assert guards.take_queue() == [message]
    assert guards.queued() == ()


def test_messages_crossing_into_night_are_judged_at_release_time():
    guards, clock = make_guards(datetime(2026, 11, 4, 21, 59, 50))
    guards.add_parent_message("甲", "下节课几点")
    clock.advance(45)
    assert guards.pop_ready()[0].parent == "甲"
    assert guards.check_send("甲").action == QUEUE


# ---- 45 秒连发合并 ----


def test_burst_merges_into_one_and_timer_restarts():
    guards, clock = make_guards()
    guards.add_parent_message("甲", "老师")
    clock.advance(44)
    guards.add_parent_message("甲", "下节课")
    clock.advance(44)
    guards.add_parent_message("甲", "几点")
    clock.advance(44)
    assert guards.pop_ready() == []

    clock.advance(1)
    merged = guards.pop_ready()
    assert len(merged) == 1
    assert merged[0].text == "老师\n下节课\n几点"
    assert merged[0].count == 3
    assert merged[0].first_at == WEDNESDAY_NOON
    assert merged[0].last_at == WEDNESDAY_NOON + timedelta(seconds=88)
    assert guards.pop_ready() == []


def test_messages_45_seconds_apart_do_not_merge():
    guards, clock = make_guards()
    guards.add_parent_message("甲", "下节课几点")
    clock.advance(45)
    first = guards.pop_ready()
    guards.add_parent_message("甲", "回放在哪")
    clock.advance(45)
    second = guards.pop_ready()
    assert [m.text for m in first + second] == ["下节课几点", "回放在哪"]


def test_different_parents_do_not_merge():
    guards, clock = make_guards()
    guards.add_parent_message("甲", "下节课几点")
    clock.advance(10)
    guards.add_parent_message("乙", "回放在哪")
    clock.advance(35)
    assert [m.parent for m in guards.pop_ready()] == ["甲"]
    clock.advance(10)
    assert [m.parent for m in guards.pop_ready()] == ["乙"]


# ---- 频率上限 ----


def send_times(guards, parent, count):
    for _ in range(count):
        assert guards.check_send(parent).action == SEND
        guards.record_sent(parent)


def test_fourth_reply_to_same_parent_pauses_and_alerts():
    guards, clock = make_guards()
    send_times(guards, "甲", 3)
    clock.advance(10)
    verdict = guards.check_send("甲")
    assert (verdict.action, verdict.reason) == (REMIND, REASON_RATE_PARENT)
    assert verdict.paused_now is True
    assert guards.paused
    assert guards.pause_reason == REASON_RATE_PARENT

    other = guards.check_send("乙")
    assert (other.action, other.paused_now) == (REMIND, False)


def test_same_parent_under_limit_after_an_hour():
    guards, clock = make_guards()
    send_times(guards, "甲", 3)
    clock.advance(3600)
    assert guards.check_send("甲").action == SEND
    assert not guards.paused


def test_old_replies_slide_out_one_by_one():
    guards, clock = make_guards()
    send_times(guards, "甲", 1)
    clock.advance(1800)
    send_times(guards, "甲", 2)
    clock.advance(1799)
    assert guards.check_send("甲").action == REMIND
    guards.resume()
    clock.advance(1)
    assert guards.check_send("甲").action == SEND


def test_31st_reply_across_parents_pauses():
    guards, _ = make_guards()
    for index in range(10):
        send_times(guards, f"家长{index}", 3)
    verdict = guards.check_send("第十一位")
    assert (verdict.action, verdict.reason) == (REMIND, REASON_RATE_ALL)
    assert verdict.paused_now is True


def test_30_replies_across_parents_does_not_pause():
    guards, _ = make_guards()
    for index in range(9):
        send_times(guards, f"家长{index}", 3)
    send_times(guards, "第十位", 2)
    assert guards.check_send("第十一位").action == SEND
    assert not guards.paused


def test_resume_within_window_pauses_again():
    guards, _ = make_guards()
    send_times(guards, "甲", 3)
    assert guards.check_send("甲").paused_now is True
    guards.resume()
    verdict = guards.check_send("甲")
    assert (verdict.action, verdict.paused_now) == (REMIND, True)


def test_unsent_checks_do_not_count_toward_limit():
    guards, _ = make_guards()
    for _ in range(10):
        assert guards.check_send("甲").action == SEND
    assert not guards.paused


# ---- 几条同时命中 ----


def test_rate_limit_does_not_pause_for_messages_that_would_not_send():
    guards, clock = make_guards()
    send_times(guards, "甲", 3)
    clock.set(datetime(2026, 11, 4, 12, 30, 0))
    guards.note_teacher_message("甲")
    assert guards.check_send("甲").reason == REASON_TEACHER
    assert not guards.paused

    guards, clock = make_guards(datetime(2026, 11, 4, 21, 50, 0))
    send_times(guards, "甲", 3)
    clock.set(datetime(2026, 11, 4, 22, 10, 0))
    assert guards.check_send("甲").action == QUEUE
    assert not guards.paused


def test_pause_takes_priority_over_night():
    guards, _ = make_guards(datetime(2026, 11, 4, 23, 0, 0))
    guards.pause()
    assert guards.check_send("甲").action == REMIND


# ---- 撤回提醒 ----


def test_default_recall_window_is_unverified():
    assert GuardConfig().recall_window_seconds is None


def test_unverified_recall_promises_nothing():
    sent = WEDNESDAY_NOON
    notice = recall_notice(sent, sent, None)
    assert notice.status == RECALL_UNVERIFIED
    assert notice.deadline is None
    assert "未查实" in notice.text
    assert "不保证" in notice.text
    assert "不代撤" in notice.text


def test_recall_within_window_shows_deadline():
    notice = recall_notice(WEDNESDAY_NOON, WEDNESDAY_NOON + timedelta(seconds=60), 120)
    assert notice.status == RECALL_OPEN
    assert notice.deadline == WEDNESDAY_NOON + timedelta(seconds=120)
    assert "12:02:00" in notice.text


def test_recall_after_window_says_expired():
    notice = recall_notice(WEDNESDAY_NOON, WEDNESDAY_NOON + timedelta(seconds=121), 120)
    assert notice.status == RECALL_EXPIRED
    assert "联系家长" in notice.text


# ---- 配置 ----


def test_config_defaults_when_file_or_section_missing(tmp_path):
    assert load_guard_config(tmp_path / "没有.ini") == GuardConfig()
    path = tmp_path / "本机配置.ini"
    path.write_text("[model]\napi_key = x\n", encoding="utf-8")
    assert load_guard_config(path) == GuardConfig()


def test_config_reads_guards_section(tmp_path):
    path = tmp_path / "本机配置.ini"
    path.write_text(
        "[guards]\nrecall_window_seconds = 120\nholidays = 2026-10-01, 2026-10-02\n",
        encoding="utf-8",
    )
    config = load_guard_config(path)
    assert config.recall_window_seconds == 120
    assert config.holidays == frozenset({date(2026, 10, 1), date(2026, 10, 2)})


@pytest.mark.parametrize("value", ["", "未查实"])
def test_config_unverified_window_stays_none(tmp_path, value):
    path = tmp_path / "本机配置.ini"
    path.write_text(f"[guards]\nrecall_window_seconds = {value}\n", encoding="utf-8")
    assert load_guard_config(path).recall_window_seconds is None


@pytest.mark.parametrize(
    "line",
    [
        "recall_window_seconds = 0",
        "recall_window_seconds = -5",
        "recall_window_seconds = 两分钟",
        "holidays = 10月1日",
    ],
)
def test_config_bad_values_are_reported(tmp_path, line):
    path = tmp_path / "本机配置.ini"
    path.write_text(f"[guards]\n{line}\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_guard_config(path)
