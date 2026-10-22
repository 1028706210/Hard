@echo off
setlocal
title Hard - Stop
cd /d "%~dp0"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\stop-hard.ps1"
set "hardExit=%errorlevel%"
if not "%hardExit%"=="0" goto failed
timeout /t 2 /nobreak >nul 2>&1
exit /b 0
:failed
echo.
echo Hard could not stop. Please check the details above.
pause
exit /b %hardExit%
