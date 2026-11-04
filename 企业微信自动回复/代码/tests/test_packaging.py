"""打包文件的静态检查：bat 在 Mac 上跑不了，能用程序判的都在这里判。还测安装的复制逻辑。"""
import re
import runpy
import subprocess
import zipfile
from pathlib import Path

import pytest

from autoreply import install

CODE_ROOT = Path(__file__).resolve().parents[1]
PACKAGING = CODE_ROOT / "packaging"
BATCH_NAMES = ["打包.bat", "安装.bat", "自检.bat", "收集日志.bat"]


@pytest.fixture(params=BATCH_NAMES)
def batch_bytes(request):
    return (PACKAGING / request.param).read_bytes()


def decoded_lines(raw):
    return raw.decode("utf-8").split("\r\n")


def test_uses_crlf_only_and_ends_with_newline(batch_bytes):
    assert batch_bytes.count(b"\n") == batch_bytes.count(b"\r\n")
    assert batch_bytes.count(b"\r") == batch_bytes.count(b"\r\n")
    assert batch_bytes.endswith(b"\r\n")


def test_has_no_bom_and_starts_with_codepage_switch(batch_bytes):
    assert batch_bytes.startswith(b"@echo off\r\nchcp 65001 >nul\r\n")


def test_chinese_appears_only_on_echo_lines(batch_bytes):
    for line in decoded_lines(batch_bytes):
        if not line.isascii():
            assert line.startswith("echo "), line


def test_echo_lines_have_no_cmd_special_characters(batch_bytes):
    for line in decoded_lines(batch_bytes):
        if line.startswith("echo ") and line != "echo.":
            assert not re.search(r"[&|<>^%()]", line), line


def test_every_goto_has_its_label(batch_bytes):
    lines = decoded_lines(batch_bytes)
    labels = {line[1:] for line in lines if line.startswith(":")}
    targets = re.findall(r"goto :(\w+)", "\n".join(lines))
    assert targets
    assert set(targets) <= labels


def test_script_folder_is_always_quoted_and_never_a_bare_trailing_backslash(batch_bytes):
    for line in decoded_lines(batch_bytes):
        for match in re.finditer(r"%~dp0", line):
            before = line[: match.start()]
            assert before.count('"') % 2 == 1, line
        # 「"%~dp0"」作为参数传给程序时，结尾的反斜杠会吃掉引号；cd 是内部命令不受影响
        if '"%~dp0"' in line:
            assert line.startswith("cd /d "), line


def test_batch_files_never_touch_wecom_or_admin(batch_bytes):
    text = batch_bytes.decode("utf-8").lower()
    for word in ("wxwork", "runas", "reg add", "sendkeys"):
        assert word not in text


def test_spec_compiles_and_names_every_shipped_batch_file():
    source = (PACKAGING / "autoreply.spec").read_text(encoding="utf-8")
    compile(source, "autoreply.spec", "exec")
    for name in ("安装.bat", "自检.bat", "收集日志.bat"):
        assert name in source
        assert (PACKAGING / name).exists()
    assert 'name="autoreply_window"' in source
    assert "console=False" in source


def test_build_tool_version_matches_pyproject():
    pin = (PACKAGING / "requirements-build.txt").read_text(encoding="utf-8").strip()
    assert re.fullmatch(r"pyinstaller==[\d.]+", pin)
    assert f'"{pin}"' in (CODE_ROOT / "pyproject.toml").read_text(encoding="utf-8")


def test_source_zip_keeps_chinese_names_and_crlf(tmp_path):
    script = runpy.run_path(str(PACKAGING / "做源码包.py"))
    zip_path = script["build"](CODE_ROOT, tmp_path)
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        info = archive.getinfo("自动回复源码/packaging/打包.bat")
        assert info.flag_bits & 0x800, "中文文件名要标 UTF-8，否则到 Windows 上变乱码"
        assert b"\r\n" in archive.read(info)
    assert "自动回复源码/autoreply/app.py" in names
    assert "自动回复源码/packaging/autoreply.spec" in names
    assert not [name for name in names if ".venv" in name or "__pycache__" in name or "测试集" in name]


# ---- 安装的复制逻辑 ----


def make_program_folder(path):
    (path / "_internal").mkdir(parents=True)
    (path / "autoreply.exe").write_text("new", encoding="utf-8")
    (path / "_internal" / "lib.dll").write_text("new", encoding="utf-8")
    return path


def ok_runner(_script):
    return subprocess.CompletedProcess([], 0, b"", b"")


def test_install_copies_folder_and_overwrites_old_version(tmp_path, capsys):
    source = make_program_folder(tmp_path / "打包结果")
    target = tmp_path / "自动回复" / "程序"
    target.mkdir(parents=True)
    (target / "autoreply.exe").write_text("old", encoding="utf-8")
    code = install.run(source, target, tmp_path / "桌面", ok_runner)
    assert code == 0
    assert (target / "autoreply.exe").read_text(encoding="utf-8") == "new"
    assert (target / "_internal" / "lib.dll").exists()
    assert "安装完成" in capsys.readouterr().out


def test_install_into_itself_is_harmless(tmp_path):
    source = make_program_folder(tmp_path / "程序")
    assert install.run(source, source, tmp_path / "桌面", ok_runner) == 0
    assert (source / "autoreply.exe").read_text(encoding="utf-8") == "new"


def test_shortcut_failure_does_not_fail_install(tmp_path, capsys):
    source = make_program_folder(tmp_path / "打包结果")

    def failing_runner(_script):
        raise OSError("PowerShell 被禁用")

    code = install.run(source, tmp_path / "目标", tmp_path / "桌面", failing_runner)
    assert code == 0
    assert "没建成" in capsys.readouterr().out


def test_shortcut_targets_exist_in_shipped_folder():
    shipped = {"自检.bat", "收集日志.bat"}
    bat_targets = {target for _, target in install.SHORTCUTS if target.endswith(".bat")}
    assert bat_targets == shipped
    exe_targets = {target for _, target in install.SHORTCUTS if target.endswith(".exe")}
    assert exe_targets == {"autoreply_window.exe"}


def test_shortcut_script_escapes_apostrophe_in_path():
    script = install.shortcut_script(Path("/桌面/a'b.lnk"), Path("/程序/自检.bat"))
    assert "a''b.lnk" in script
    assert "\n" not in script
    assert "CreateShortcut" in script
