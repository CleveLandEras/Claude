@echo off
chcp 65001 >nul
setlocal
rem Runs on Windows only. Builds dist\autoreply from source with PyInstaller.
rem Non-ASCII text stays on echo lines; paths are always quoted.
cd /d "%~dp0.."
set "PKG=%CD%\packaging"
set "VENV=%PKG%\.venv-windows"
set "VPY=%VENV%\Scripts\python.exe"

echo [1/4] 查找 Python
where py >nul 2>&1
if errorlevel 1 goto :try_python
py -3.11 --version >nul 2>&1
if errorlevel 1 goto :try_python
set "PY=py -3.11"
goto :check_python
:try_python
python --version >nul 2>&1
if errorlevel 1 goto :no_python
set "PY=python"
:check_python
%PY% -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 11) else 1)"
if errorlevel 1 goto :wrong_python
%PY% -c "import tkinter"
if errorlevel 1 goto :no_tkinter

echo [2/4] 建虚拟环境
if exist "%VPY%" goto :have_venv
%PY% -m venv "%VENV%"
if errorlevel 1 goto :venv_failed
:have_venv

echo [3/4] 安装打包工具，第一次要下载，约 2 分钟
"%VPY%" -m pip install --disable-pip-version-check -r "%PKG%\requirements-build.txt"
if not errorlevel 1 goto :deps_ok
echo 官方下载源连不上，改用清华镜像再试一次
"%VPY%" -m pip install --disable-pip-version-check -i https://pypi.tuna.tsinghua.edu.cn/simple -r "%PKG%\requirements-build.txt"
if errorlevel 1 goto :pip_failed
:deps_ok

echo [4/4] 打包，约 2 分钟
"%VPY%" -m PyInstaller --noconfirm --clean --distpath "%PKG%\dist" --workpath "%PKG%\build" "%PKG%\autoreply.spec"
if errorlevel 1 goto :build_failed
if not exist "%PKG%\dist\autoreply\autoreply.exe" goto :build_failed

echo.
echo 打包完成。接下来在自动打开的文件夹里双击 安装.bat
start "" explorer "%PKG%\dist\autoreply"
goto :end

:no_python
echo 没找到 Python。请先装 Python 3.11.9，安装时勾选 Add python.exe to PATH，再双击这个文件。
goto :end
:wrong_python
echo 这台电脑的 Python 不是 3.11。请按说明第 2 步装 Python 3.11.9，再双击这个文件。
goto :end
:no_tkinter
echo 这个 Python 缺界面组件 tkinter。请从 python.org 重新装一次，选默认选项。
goto :end
:venv_failed
echo 虚拟环境建不起来。请把这个窗口截图发回来。
goto :end
:pip_failed
echo 打包工具下载失败，多半是这台电脑上不了外网。请把这个窗口截图发回来。
goto :end
:build_failed
echo 打包失败。请把这个窗口截图发回来。
goto :end

:end
echo.
pause
endlocal
