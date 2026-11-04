@echo off
chcp 65001 >nul
setlocal
rem Runs the self check; the program prints the result and writes it to the log.
if not exist "%~dp0autoreply.exe" goto :no_program
"%~dp0autoreply.exe" selfcheck
goto :end
:no_program
echo 找不到 autoreply.exe。请先运行 安装.bat，再双击这个文件。
:end
echo.
pause
endlocal
