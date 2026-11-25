@echo off
REM Use SETUP_CF0.bat for the CF-0 relay.
rem Owner-local CF-0 health report status; no command execution or schedule changes.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\..\relay\configure_health_reporting.ps1" -Mode status
set "CODE=%ERRORLEVEL%"
if not "%CODE%"=="0" echo Health operation failed safely. Existing relay untouched.
pause
exit /b %CODE%
