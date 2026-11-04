@echo off
chcp 65001 >nul
setlocal
rem Packs the log folder into a zip on the desktop.
if not exist "%~dp0autoreply.exe" goto :no_program
"%~dp0autoreply.exe" collectlog
goto :end
:no_program
echo 找不到 autoreply.exe。请先运行 安装.bat，再双击这个文件。
:end
echo.
pause
endlocal
