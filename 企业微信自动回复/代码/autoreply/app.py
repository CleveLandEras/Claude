"""打包后程序的入口。

autoreply.exe <命令>：命令行版，给 bat 调，命令有 selfcheck、collectlog、install、toast。
autoreply_window.exe：窗口版，不带参数，打开测试窗口。
源码运行：python -m autoreply.app <命令>。
"""
from __future__ import annotations

import sys
from typing import Optional, Sequence

from autoreply import applog

USAGE = "用法：autoreply [window|selfcheck|collectlog|install|toast]"


def _run_window() -> int:
    from autoreply import window

    return window.run()


def _run_selfcheck() -> int:
    from autoreply import selfcheck

    return selfcheck.run()


def _run_collectlog() -> int:
    from autoreply import collectlog

    return collectlog.run()


def _run_install() -> int:
    from autoreply import install

    return install.run()


def _run_toast() -> int:
    from autoreply import toast

    shown = toast.show()
    print("提醒已发出" if shown else "提醒没弹出来，原因写在日志里")
    return 0 if shown else 1


COMMANDS = {
    "window": _run_window,
    "selfcheck": _run_selfcheck,
    "collectlog": _run_collectlog,
    "install": _run_install,
    "toast": _run_toast,
}


def _tolerate_console_encoding() -> None:
    """控制台编码放不下某个字符时用问号代替，不能让程序因此退出。窗口版没有控制台。"""
    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")


def main(argv: Optional[Sequence[str]] = None) -> int:
    _tolerate_console_encoding()
    args = list(sys.argv[1:] if argv is None else argv)
    command = args[0] if args else "window"
    handler = COMMANDS.get(command)
    if handler is None:
        print(USAGE)
        return 2
    try:
        return handler()
    except Exception as exc:
        try:
            applog.write(f"error in {command}: {exc!r}")
        except OSError:
            pass
        raise


if __name__ == "__main__":
    sys.exit(main())
