@echo off
chcp 65001 >nul
setlocal
rem Copies this folder to the user's local app data and adds desktop shortcuts. No admin rights needed.
if not exist "%~dp0autoreply.exe" goto :no_program
"%~dp0autoreply.exe" install
goto :end
:no_program
echo 找不到 autoreply.exe。请先把整个文件夹解压出来，再双击这个文件。
:end
echo.
pause
endlocal
