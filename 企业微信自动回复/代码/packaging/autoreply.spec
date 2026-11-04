# -*- mode: python ; coding: utf-8 -*-
# PyInstaller config, run by the packaging batch file on Windows.
# Builds one folder (dist/autoreply) holding two programs:
#   autoreply        - console version, called by the batch files
#   autoreply_window - no console, opens the test window
# The batch files are copied next to them at the end.
import shutil
from pathlib import Path

packaging_dir = Path(SPECPATH)
code_root = packaging_dir.parent
FOLDER_NAME = "autoreply"
BATCH_FILES = ("安装.bat", "自检.bat", "收集日志.bat")

a = Analysis(
    [str(code_root / "autoreply" / "app.py")],
    pathex=[str(code_root)],
    hiddenimports=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

console_exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="autoreply",
    console=True,
    upx=False,
)
window_exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="autoreply_window",
    console=False,
    upx=False,
)
coll = COLLECT(
    console_exe,
    window_exe,
    a.binaries,
    a.datas,
    upx=False,
    name=FOLDER_NAME,
)

output_dir = Path(DISTPATH) / FOLDER_NAME
for batch_file in BATCH_FILES:
    shutil.copy2(packaging_dir / batch_file, output_dir / batch_file)
