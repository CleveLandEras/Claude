"""测试窗口：粘贴一段文字看字数，点按钮弹一条测试提醒。逻辑在 paste.py、toast.py。"""
from __future__ import annotations

import threading
import tkinter as tk
from typing import Optional

from autoreply import applog, paste, toast

POLL_MILLISECONDS = 200


class TestWindow:
    def __init__(
        self,
        root: tk.Tk,
        directory: Optional[applog.PathLike] = None,
        backend=None,
    ) -> None:
        self.root = root
        self.directory = directory
        self.backend = backend
        self._toast_done = threading.Event()
        self._toast_ok = False

        root.title("自动回复（测试）")
        root.geometry("520x340")

        buttons = tk.Frame(root)
        buttons.pack(fill="x", padx=12, pady=(12, 6))
        tk.Button(buttons, text="粘贴", width=10, command=self.on_paste).pack(side="left")
        self.toast_button = tk.Button(
            buttons, text=toast.TEST_TITLE, width=10, command=self.on_toast
        )
        self.toast_button.pack(side="left", padx=(8, 0))

        self.toast_status = tk.StringVar(value="")
        tk.Label(root, textvariable=self.toast_status, anchor="w").pack(fill="x", padx=12)

        self.status = tk.StringVar(value="复制好文字后，按 Ctrl+V 或点「粘贴」")
        tk.Label(root, textvariable=self.status, anchor="w", font=("", 13)).pack(
            fill="x", padx=12, pady=6
        )

        self.box = tk.Text(root, height=10, wrap="word", state="disabled")
        self.box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        root.bind("<Control-v>", self.on_paste)
        root.bind("<Control-V>", self.on_paste)

    def on_paste(self, _event=None) -> None:
        try:
            text = self.root.clipboard_get()
        except tk.TclError:  # 剪贴板是空的或不是文字
            text = ""
        self.status.set(paste.receive(text, self.directory))
        self.box.configure(state="normal")
        self.box.delete("1.0", "end")
        self.box.insert("1.0", text)
        self.box.configure(state="disabled")

    def on_toast(self) -> None:
        self.toast_button.configure(state="disabled")
        self.toast_status.set("正在弹提醒，请看屏幕右下角……")
        self._toast_done.clear()
        # 不设成后台线程：关窗口时也等它把日志写完
        threading.Thread(target=self._run_toast).start()
        self.root.after(POLL_MILLISECONDS, self._poll_toast)

    def _run_toast(self) -> None:
        try:
            self._toast_ok = toast.show(backend=self.backend, directory=self.directory)
        except OSError:  # 日志写不进去
            self._toast_ok = False
        self._toast_done.set()

    def _poll_toast(self) -> None:
        if not self._toast_done.is_set():
            self.root.after(POLL_MILLISECONDS, self._poll_toast)
            return
        self.toast_button.configure(state="normal")
        self.toast_status.set(
            "提醒已发出" if self._toast_ok else "提醒没弹出来，原因写在日志里"
        )


def run(directory: Optional[applog.PathLike] = None) -> int:
    root = tk.Tk()
    TestWindow(root, directory)
    root.mainloop()
    return 0
