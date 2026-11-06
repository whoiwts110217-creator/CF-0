@echo off
rem Owner-local CF-0 health report disable; no command execution or schedule changes.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0relay\configure_health_reporting.ps1" -Mode disable
set "CODE=%ERRORLEVEL%"
if not "%CODE%"=="0" echo Health operation failed safely. Existing relay untouched.
pause
exit /b %CODE%
