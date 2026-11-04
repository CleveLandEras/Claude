"""防出错规则（思考页 7.1 ⑤，第 6 节第 6、7、9 条）。只管判断，不碰企业微信、不弹窗、不真的等待。

时间都从注入的时钟读，单测用模拟时钟。流程这样用：
    guards.add_parent_message(备注名, 原话)     收到家长消息
    guards.note_teacher_message(备注名)         读到二讲自己在这个会话发了消息
    guards.pop_ready()                          取出 45 秒没有新消息的家长，每位合并成一条去分类
    guards.check_send(备注名)                   判成自动才问这一步：SEND 就发，REMIND 只提醒，QUEUE 排队
    guards.record_sent(备注名)                  真的发出去之后记一笔，频率上限只数发出去的
全自动路线发送前再读一次会话：读到二讲已回就 note_teacher_message，再 check_send 一次，会变成 REMIND。

思考页没写死、这里暂按的（可推翻）：
- 超限后暂停的是整个工具，不只是这位家长，要二讲手动恢复。恢复后窗口没过，再超还会再停。
- 「每小时」按滑动 60 分钟算，不按整点。
- 几条同时命中时按「暂停、二讲在回、夜间节假日、频率上限」的次序取第一条；频率上限排最后，
  本来就不会发的消息不触发自动暂停。
- 节假日表思考页没给来源，要配进 [guards] holidays。没配当年的表时算不清今天是不是节假日，按不自动发。
- 撤回时限没查实（recall_window_seconds 为 None）：撤回提醒不写期限，也不说还能撤。
- 这些状态只在内存里，重启就清零。接真实流程时要定暂停状态和计数要不要存盘。
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Callable, Deque, Dict, FrozenSet, List, Optional, Tuple

from .config import CONFIG_PATH, ConfigError, _read

SEND = "自动发"
REMIND = "转二讲"
QUEUE = "排队"

REASON_PAUSED = "已暂停"
REASON_TEACHER = "二讲最近 5 分钟在这个会话发过消息"
REASON_NIGHT = "夜间"
REASON_HOLIDAY = "法定节假日"
REASON_NO_HOLIDAY_LIST = "没配当年的节假日表"
REASON_RATE_PARENT = "同一家长 1 小时内自动回复超限"
REASON_RATE_ALL = "全部家长 1 小时内自动回复超限"

RECALL_UNVERIFIED = "未查实"
RECALL_OPEN = "时限内"
RECALL_EXPIRED = "已过时限"

_RATE_WINDOW_SECONDS = 3600

Clock = Callable[[], datetime]


@dataclass(frozen=True)
class GuardConfig:
    """默认数字照思考页。holidays、recall_window_seconds 还没有查实的值，默认 None，见开头说明。"""

    merge_seconds: int = 45
    teacher_active_seconds: int = 300
    night_start: time = time(22, 0)
    night_end: time = time(7, 30)
    max_per_parent_per_hour: int = 3
    max_all_per_hour: int = 30
    holidays: Optional[FrozenSet[date]] = None
    recall_window_seconds: Optional[int] = None


@dataclass(frozen=True)
class Verdict:
    """action 是 SEND、REMIND 或 QUEUE。reason 是为什么不发。paused_now：这次检查触发了自动暂停，要提醒二讲。"""

    action: str
    reason: Optional[str] = None
    paused_now: bool = False


@dataclass(frozen=True)
class Merged:
    """同一家长连发合并后的一条。text 用换行连接（和测试集写法一致）。"""

    parent: str
    text: str
    first_at: datetime
    last_at: datetime
    count: int


@dataclass(frozen=True)
class RecallNotice:
    """每条自动回复的撤回提醒。工具不代撤，只提醒二讲手动撤回。deadline 只有查实了时限才有。"""

    status: str
    text: str
    deadline: Optional[datetime] = None


def recall_notice(
    sent_at: datetime, now: datetime, window_seconds: Optional[int]
) -> RecallNotice:
    if window_seconds is None:
        return RecallNotice(
            RECALL_UNVERIFIED,
            "撤回时限未查实，不保证还能撤回。发错请马上手动试撤，撤不回就直接联系家长更正。工具不代撤。",
        )
    deadline = sent_at + timedelta(seconds=window_seconds)
    if now <= deadline:
        return RecallNotice(
            RECALL_OPEN,
            f"发错请在 {deadline:%H:%M:%S} 前手动撤回。工具不代撤。",
            deadline,
        )
    return RecallNotice(
        RECALL_EXPIRED, "已过撤回时限。发错请直接联系家长更正。", deadline
    )


class Guards:
    def __init__(self, config: Optional[GuardConfig] = None, clock: Clock = datetime.now):
        self.config = config or GuardConfig()
        self._clock = clock
        self._pause_reason: Optional[str] = None
        self._teacher_last: Dict[str, datetime] = {}
        self._pending: Dict[str, List[Tuple[datetime, str]]] = {}
        self._queue: List[Merged] = []
        self._sent_by_parent: Dict[str, Deque[datetime]] = {}
        self._sent_all: Deque[datetime] = deque()

    # ---- 一键暂停与恢复 ----

    @property
    def paused(self) -> bool:
        return self._pause_reason is not None

    @property
    def pause_reason(self) -> Optional[str]:
        return self._pause_reason

    def pause(self) -> None:
        self._pause_reason = REASON_PAUSED

    def resume(self) -> None:
        self._pause_reason = None

    # ---- 不抢答 ----

    def note_teacher_message(self, parent: str) -> None:
        self._teacher_last[parent] = self._clock()

    def _teacher_active(self, parent: str, now: datetime) -> bool:
        last = self._teacher_last.get(parent)
        if last is None:
            return False
        return (now - last).total_seconds() <= self.config.teacher_active_seconds

    # ---- 连发合并 ----

    def add_parent_message(self, parent: str, text: str) -> None:
        self._pending.setdefault(parent, []).append((self._clock(), text))

    def pop_ready(self) -> List[Merged]:
        """取出最后一条之后已经等够 merge_seconds 的家长。没等够的留着，新消息会重新计时。"""
        now = self._clock()
        ready: List[Merged] = []
        for parent, items in list(self._pending.items()):
            if (now - items[-1][0]).total_seconds() < self.config.merge_seconds:
                continue
            del self._pending[parent]
            ready.append(
                Merged(
                    parent=parent,
                    text="\n".join(text for _, text in items),
                    first_at=items[0][0],
                    last_at=items[-1][0],
                    count=len(items),
                )
            )
        return ready

    # ---- 夜间、节假日排队 ----

    def _quiet_reason(self, now: datetime) -> Optional[str]:
        config = self.config
        clock_time = now.time()
        if clock_time >= config.night_start or clock_time < config.night_end:
            return REASON_NIGHT
        holidays = config.holidays
        if holidays is None or not any(day.year == now.year for day in holidays):
            return REASON_NO_HOLIDAY_LIST
        if now.date() in holidays:
            return REASON_HOLIDAY
        return None

    def enqueue(self, message: Merged) -> None:
        self._queue.append(message)

    def queued(self) -> Tuple[Merged, ...]:
        return tuple(self._queue)

    def take_queue(self) -> List[Merged]:
        """二讲上线时取走排队的消息给她看。队里的不会到点自动发。"""
        taken, self._queue = self._queue, []
        return taken

    # ---- 频率上限 ----

    def _prune(self, sent: Deque[datetime], now: datetime) -> None:
        while sent and (now - sent[0]).total_seconds() >= _RATE_WINDOW_SECONDS:
            sent.popleft()

    def _over_limit(self, parent: str, now: datetime) -> Optional[str]:
        self._prune(self._sent_all, now)
        by_parent = self._sent_by_parent.get(parent)
        if by_parent is not None:
            self._prune(by_parent, now)
            if len(by_parent) >= self.config.max_per_parent_per_hour:
                return REASON_RATE_PARENT
        if len(self._sent_all) >= self.config.max_all_per_hour:
            return REASON_RATE_ALL
        return None

    def record_sent(self, parent: str) -> None:
        now = self._clock()
        self._sent_by_parent.setdefault(parent, deque()).append(now)
        self._sent_all.append(now)

    # ---- 发之前问一次 ----

    def check_send(self, parent: str) -> Verdict:
        """判成自动的消息发之前问这一步。转二讲的消息不用问，直接提醒。"""
        now = self._clock()
        if self._pause_reason is not None:
            return Verdict(REMIND, self._pause_reason)
        if self._teacher_active(parent, now):
            return Verdict(REMIND, REASON_TEACHER)
        quiet = self._quiet_reason(now)
        if quiet is not None:
            return Verdict(QUEUE, quiet)
        over = self._over_limit(parent, now)
        if over is not None:
            self._pause_reason = over
            return Verdict(REMIND, over, paused_now=True)
        return Verdict(SEND)


# ---- 配置 ----


def _parse_window(path: Path, raw: str) -> Optional[int]:
    if raw in ("", RECALL_UNVERIFIED):
        return None
    try:
        window = int(raw)
    except ValueError:
        window = 0
    if window <= 0:
        raise ConfigError(
            f"{path} 的 [guards] recall_window_seconds 要是大于 0 的秒数，没查实就留空"
        )
    return window


def _parse_holidays(path: Path, raw: str) -> Optional[FrozenSet[date]]:
    if not raw:
        return None
    try:
        return frozenset(date.fromisoformat(part.strip()) for part in raw.split(","))
    except ValueError:
        raise ConfigError(
            f"{path} 的 [guards] holidays 要写成逗号隔开的日期，如 2026-10-01,2026-10-02"
        ) from None


def load_guard_config(path: Path = CONFIG_PATH) -> GuardConfig:
    """读本机配置的 [guards]。没有文件或没写这节就用默认，也就是两项都按未查实处理。"""
    path = Path(path)
    if not path.is_file():
        return GuardConfig()
    parser = _read(path)
    window = parser.get("guards", "recall_window_seconds", fallback="").strip()
    holidays = parser.get("guards", "holidays", fallback="").strip()
    return GuardConfig(
        recall_window_seconds=_parse_window(path, window),
        holidays=_parse_holidays(path, holidays),
    )
