@echo off
setlocal
title Hard - Start
cd /d "%~dp0"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-hard.ps1"
set "hardExit=%errorlevel%"
if not "%hardExit%"=="0" goto failed
start "" "http://127.0.0.1:4173"
exit /b 0
:failed
echo.
echo Hard could not start. Please check the details above.
pause
exit /b %hardExit%
