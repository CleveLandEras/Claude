"""弹窗提醒：用假后端验证日志那一行，用假 runner 验证发给 PowerShell 的内容。Mac 上不弹窗。"""
import subprocess

import pytest

from autoreply import applog, toast, winutil


class RecordingBackend:
    def __init__(self):
        self.calls = []

    def show(self, title, body):
        self.calls.append((title, body))


class FailingBackend:
    def show(self, title, body):
        raise toast.ToastError("系统不让弹\n第二行")


def log_lines(directory):
    return applog.log_path(directory).read_text(encoding="utf-8").splitlines()


def test_show_logs_toast_shown_with_replaceable_backend(tmp_path):
    backend = RecordingBackend()
    assert toast.show(backend=backend, directory=tmp_path) is True
    assert backend.calls == [("测试提醒", toast.TEST_BODY)]
    lines = log_lines(tmp_path)
    assert len(lines) == 1
    assert lines[0].endswith(" toast shown")


def test_failure_logs_reason_and_not_shown(tmp_path):
    assert toast.show(backend=FailingBackend(), directory=tmp_path) is False
    lines = log_lines(tmp_path)
    assert len(lines) == 1
    assert "toast failed: 系统不让弹 第二行" in lines[0]
    assert "toast shown" not in lines[0]


def test_default_backend_follows_platform():
    assert isinstance(toast.default_backend("win32"), toast.PowerShellBalloon)
    assert isinstance(toast.default_backend("darwin"), toast.NoPopup)


def test_non_windows_default_never_claims_shown(tmp_path):
    assert toast.show(backend=toast.NoPopup(), directory=tmp_path) is False
    assert "toast shown" not in applog.log_path(tmp_path).read_text(encoding="utf-8")


def test_powershell_backend_passes_title_and_body():
    scripts = []

    def runner(script):
        scripts.append(script)
        return subprocess.CompletedProcess([], 0, b"", b"")

    toast.PowerShellBalloon(runner).show("测试提醒", "看到了吗")
    assert "$n.BalloonTipTitle = '测试提醒'" in scripts[0]
    assert "$n.BalloonTipText = '看到了吗'" in scripts[0]
    assert "\n" not in scripts[0]


def test_powershell_failure_becomes_toast_failed(tmp_path):
    def runner(_script):
        return subprocess.CompletedProcess([], 1, b"", b"blocked")

    backend = toast.PowerShellBalloon(runner)
    assert toast.show(backend=backend, directory=tmp_path) is False
    assert "toast failed: PowerShell" in log_lines(tmp_path)[0]


def test_powershell_timeout_becomes_toast_failed(tmp_path):
    def runner(_script):
        raise subprocess.TimeoutExpired("powershell", 30)

    backend = toast.PowerShellBalloon(runner)
    assert toast.show(backend=backend, directory=tmp_path) is False
    assert "toast failed" in log_lines(tmp_path)[0]


def test_empty_body_is_rejected_before_calling_powershell():
    with pytest.raises(toast.ToastError):
        toast.balloon_script("测试提醒", "")


def test_single_quote_is_escaped_for_powershell():
    assert winutil.ps_quote("it's") == "'it''s'"


def test_powershell_command_uses_plain_command_argument():
    command = winutil.powershell_command("Write-Output 1")
    assert command[0].endswith("powershell.exe")
    assert command[-2:] == ["-Command", "Write-Output 1"]
