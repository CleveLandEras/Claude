"""手动粘贴的逻辑：计字和写日志。不打开窗口，也不加载 tkinter。"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

from autoreply import applog, paste

PACKAGING = Path(__file__).resolve().parents[1] / "packaging"


@pytest.mark.parametrize(
    "text, expected",
    [
        ("", 0),
        ("   \n\t ", 0),
        ("今天几点上课", 6),
        ("今天几点上课？", 7),
        ("Zoom 123", 7),
        ("第一行\n第二行", 6),
        ("第一行\r\n第二行\r\n", 6),
        ("全角　空格", 4),
    ],
)
def test_count_chars(text, expected):
    assert paste.count_chars(text) == expected


def test_receive_shows_count_and_logs_it(tmp_path):
    assert paste.receive("今天几点上课？", tmp_path) == "已收到 7 字"
    log = applog.log_path(tmp_path).read_text(encoding="utf-8")
    assert log.rstrip().endswith("paste received 7 chars")


def test_log_never_contains_pasted_text(tmp_path):
    paste.receive("王小明妈妈 13800001111", tmp_path)
    log = applog.log_path(tmp_path).read_text(encoding="utf-8")
    assert "王小明" not in log
    assert "13800001111" not in log


def test_each_paste_gets_its_own_log_line(tmp_path):
    for text in ("一", "一二", "一二三"):
        paste.receive(text, tmp_path)
    lines = applog.log_path(tmp_path).read_text(encoding="utf-8").splitlines()
    assert [line.split()[-2] for line in lines] == ["1", "2", "3"]


def test_receive_says_so_when_log_cannot_be_written(tmp_path):
    blocker = tmp_path / "是文件不是目录"
    blocker.write_text("x", encoding="utf-8")
    message = paste.receive("一二三", blocker)
    assert message.startswith("已收到 3 字（日志没写上")


def test_logic_does_not_load_tkinter():
    code = "import sys, autoreply.paste; sys.exit(1 if 'tkinter' in sys.modules else 0)"
    root = Path(__file__).resolve().parents[1]
    assert subprocess.run([sys.executable, "-c", code], cwd=root).returncode == 0


def test_sample_texts_match_counts_in_trial_notes():
    """测试文字.txt 三段的字数，要和试用说明里写的一致，Dk 才能当场对照。"""
    raw = (PACKAGING / "测试文字.txt").read_text(encoding="utf-8-sig")
    segments = re.findall(r"---第.段---\s*\n(.*?)(?=\n---)", raw, flags=re.S)
    counts = [paste.count_chars(segment) for segment in segments]
    assert len(counts) == 3
    notes = (PACKAGING / "里程碑0试用说明.md").read_text(encoding="utf-8")
    for count in counts:
        assert f"已收到 {count} 字" in notes
