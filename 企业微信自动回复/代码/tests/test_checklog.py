"""日志、自检、收集日志、核对日志这条线。zip 都是现造的样例，不碰真实日志。"""
import zipfile
from datetime import datetime

import pytest

from autoreply import applog, checklog, collectlog, selfcheck

STAMP = "2026-11-04 10:00:00"
BOTH_OK = f"{STAMP} selfcheck package ok\n{STAMP} selfcheck log ok\n"


def make_zip(path, members):
    with zipfile.ZipFile(path, "w") as archive:
        for name, text in members.items():
            archive.writestr(name, text)
    return path


def first_line(capsys):
    return capsys.readouterr().out.splitlines()[0]


# ---- 核对 zip ----


def test_both_records_ok_prints_two_of_two(tmp_path, capsys):
    sample = make_zip(tmp_path / "样例.zip", {"autoreply.log": BOTH_OK})
    assert checklog.main([str(sample)]) == 0
    assert first_line(capsys) == "自检记录 2/2"


def test_failed_item_counts_as_not_passed(tmp_path, capsys):
    text = f"{STAMP} selfcheck package fail: 缺少 autoreply_window.exe\n{STAMP} selfcheck log ok\n"
    sample = make_zip(tmp_path / "s.zip", {"autoreply.log": text})
    assert checklog.main([str(sample)]) == 1
    output = capsys.readouterr().out
    assert output.splitlines()[0] == "自检记录 1/2"
    assert "打包：不通过（缺少 autoreply_window.exe）" in output


def test_missing_record_counts_as_not_passed(tmp_path, capsys):
    sample = make_zip(tmp_path / "s.zip", {"autoreply.log": f"{STAMP} selfcheck log ok\n"})
    assert checklog.main([str(sample)]) == 1
    output = capsys.readouterr().out
    assert output.splitlines()[0] == "自检记录 1/2"
    assert "打包：没有记录" in output


def test_latest_result_wins(tmp_path, capsys):
    text = (
        f"{STAMP} selfcheck package fail: 第一次没过\n"
        f"{STAMP} selfcheck log fail: 第一次没过\n" + BOTH_OK
    )
    sample = make_zip(tmp_path / "s.zip", {"autoreply.log": text})
    assert checklog.main([str(sample)]) == 0
    assert first_line(capsys) == "自检记录 2/2"


def test_pass_then_fail_is_not_passed(tmp_path, capsys):
    text = BOTH_OK + f"{STAMP} selfcheck package fail: 后来坏了\n"
    sample = make_zip(tmp_path / "s.zip", {"autoreply.log": text})
    assert checklog.main([str(sample)]) == 1
    assert first_line(capsys) == "自检记录 1/2"


def test_record_words_inside_other_lines_do_not_count(tmp_path, capsys):
    text = f"{STAMP} error in window: selfcheck package ok\n{STAMP} selfcheck log ok\n"
    sample = make_zip(tmp_path / "s.zip", {"autoreply.log": text})
    assert checklog.main([str(sample)]) == 1
    assert first_line(capsys) == "自检记录 1/2"


def test_toast_and_paste_records_are_listed(tmp_path, capsys):
    text = BOTH_OK + (
        f"{STAMP} toast shown\n"
        f"{STAMP} paste received 9 chars\n"
        f"{STAMP} paste received 17 chars\n"
    )
    sample = make_zip(tmp_path / "s.zip", {"autoreply.log": text})
    assert checklog.main([str(sample)]) == 0
    output = capsys.readouterr().out
    assert "弹窗记录 toast shown：1 行" in output
    assert "粘贴记录：2 次，字数依次 9、17" in output


def test_mac_metadata_entries_are_ignored(tmp_path, capsys):
    sample = make_zip(
        tmp_path / "s.zip",
        {"autoreply.log": BOTH_OK, "__MACOSX/._autoreply.log": "\x00\x05binary"},
    )
    assert checklog.main([str(sample)]) == 0


def test_zip_without_log_exits_two(tmp_path, capsys):
    sample = make_zip(tmp_path / "s.zip", {"说明.txt": "没有日志"})
    assert checklog.main([str(sample)]) == 2
    assert "没有 .log" in capsys.readouterr().out


def test_not_a_zip_exits_two(tmp_path, capsys):
    fake = tmp_path / "不是压缩包.zip"
    fake.write_text("hello", encoding="utf-8")
    assert checklog.main([str(fake)]) == 2


def test_missing_file_and_bad_usage_exit_two(tmp_path, capsys):
    assert checklog.main([str(tmp_path / "没有这个.zip")]) == 2
    assert checklog.main([]) == 2


def test_relative_path_falls_back_to_project_root(tmp_path):
    back_dir = tmp_path / "日志回传"
    back_dir.mkdir()
    sample = make_zip(back_dir / "s.zip", {"autoreply.log": BOTH_OK})
    assert checklog.resolve_zip_path("日志回传/s.zip", tmp_path) == sample


# ---- 日志位置 ----


def test_windows_log_dir_is_under_local_app_data():
    path = applog.log_dir(env={"LOCALAPPDATA": "/fake/local"}, platform="win32")
    assert path.as_posix() == "/fake/local/自动回复/日志"


def test_env_override_wins():
    env = {"LOCALAPPDATA": "/fake/local", applog.ENV_OVERRIDE: "/elsewhere"}
    assert applog.log_dir(env=env, platform="win32").as_posix() == "/elsewhere"


def test_write_creates_folder_and_keeps_one_line_per_call(tmp_path):
    target = tmp_path / "中文 目录" / "日志"
    applog.write("第一行\n还是第一行", target, now=datetime(2026, 11, 4, 10, 0, 0))
    applog.write("第二行", target, now=datetime(2026, 11, 4, 10, 0, 1))
    lines = applog.log_path(target).read_text(encoding="utf-8").splitlines()
    assert lines == ["2026-11-04 10:00:00 第一行 还是第一行", "2026-11-04 10:00:01 第二行"]


# ---- 自检 ----


def packaged_exe(tmp_path):
    """造一个「打包后的程序」文件夹：两个程序都在。"""
    (tmp_path / "autoreply_window.exe").write_text("", encoding="utf-8")
    return str(tmp_path / "autoreply.exe")


def test_selfcheck_packaged_prints_both_passed(tmp_path, capsys):
    log_directory = tmp_path / "日志"
    code = selfcheck.run(log_directory, frozen=True, executable=packaged_exe(tmp_path))
    assert code == 0
    assert first_line(capsys) == "打包 通过／日志 通过"


def test_selfcheck_from_source_fails_package_item(tmp_path, capsys):
    assert selfcheck.run(tmp_path, frozen=False) == 1
    assert first_line(capsys).startswith("打包 不通过（现在跑的是源码")


def test_selfcheck_missing_window_program_fails_package_item(tmp_path, capsys):
    code = selfcheck.run(tmp_path, frozen=True, executable=str(tmp_path / "autoreply.exe"))
    assert code == 1
    assert "缺少 autoreply_window.exe" in first_line(capsys)


def test_selfcheck_unwritable_log_fails_log_item(tmp_path, capsys):
    blocker = tmp_path / "是文件不是目录"
    blocker.write_text("x", encoding="utf-8")
    code = selfcheck.run(blocker, frozen=True, executable=packaged_exe(tmp_path))
    assert code == 1
    assert "日志 不通过（日志写不进去" in first_line(capsys)


# ---- 收集日志 ----


def test_collect_needs_a_log(tmp_path):
    with pytest.raises(collectlog.CollectError):
        collectlog.collect(tmp_path / "空", tmp_path / "桌面")


def test_collect_names_zip_with_time(tmp_path):
    log_directory = tmp_path / "日志"
    applog.write("x", log_directory)
    zip_path = collectlog.collect(
        log_directory, tmp_path / "桌面", now=datetime(2026, 11, 4, 10, 12, 33)
    )
    assert zip_path.name == "自动回复日志_20261104_101233.zip"
    assert zipfile.ZipFile(zip_path).namelist() == ["autoreply.log"]


def test_selfcheck_then_collect_then_check_gives_two_of_two(tmp_path, capsys):
    """Windows 上要跑的整条线，除了真的打包。"""
    log_directory = tmp_path / "日志"
    selfcheck.run(log_directory, frozen=True, executable=packaged_exe(tmp_path))
    collectlog.run(log_directory, tmp_path / "桌面")
    capsys.readouterr()
    zip_path = next((tmp_path / "桌面").glob("*.zip"))
    assert checklog.main([str(zip_path)]) == 0
    assert first_line(capsys) == "自检记录 2/2"
