"""在 Mac 上把要带到 Windows 的文件打成一个 zip。代码有改动就重跑一次。

在 代码/ 目录下运行（只用标准库）：
    python3 packaging/做源码包.py

输出 packaging/输出/自动回复源码.zip。Mac 访达的「压缩」不标文件名编码，中文文件名到
中文 Windows 上会变乱码；Python 的 zipfile 会标 UTF-8，所以用这个脚本打。
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[1]
TOP_FOLDER = "自动回复源码"
OUTPUT_DIR_NAME = "输出"
ZIP_NAME = "自动回复源码.zip"
SKIP_DIR_NAMES = {"__pycache__", "build", "dist", ".venv-windows", OUTPUT_DIR_NAME}
SKIP_FILE_NAMES = {"本机配置.ini"}  # 里面有密钥，绝不进包


def source_files(code_root: Path = CODE_ROOT):
    yield code_root / "pyproject.toml"
    for folder in ("autoreply", "packaging"):
        for path in sorted((code_root / folder).rglob("*")):
            parts = path.relative_to(code_root).parts
            if not path.is_file() or path.name.startswith(".") or path.name in SKIP_FILE_NAMES:
                continue
            if SKIP_DIR_NAMES.intersection(parts) or path.suffix == ".pyc":
                continue
            yield path


def build(code_root: Path = CODE_ROOT, out_dir: Path = None) -> Path:
    target_dir = code_root / "packaging" / OUTPUT_DIR_NAME if out_dir is None else out_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / ZIP_NAME
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in source_files(code_root):
            relative = path.relative_to(code_root).as_posix()
            archive.write(path, f"{TOP_FOLDER}/{relative}")
    return target


if __name__ == "__main__":
    print(f"已生成：{build()}")
    sys.exit(0)
