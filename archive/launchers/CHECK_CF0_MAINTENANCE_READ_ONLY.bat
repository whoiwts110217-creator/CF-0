@echo off
REM Use SETUP_CF0.bat for the CF-0 relay.
setlocal
REM Caveman Focus HP maintenance status only. Does not start, enable or alter tasks.
cd /d "%~dp0..\.."
if not exist "%~dp0..\..\relay\hp_takeover_check.ps1" (
  echo MISSING_REVIEWED_SOURCE=relay\hp_takeover_check.ps1
  echo LOCAL_CHANGES=NONE
  pause
  exit /b 2
)
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0..\..\relay\hp_takeover_check.ps1" -MaintenanceAudit
set "result=%ERRORLEVEL%"
echo.
echo This reports current local observations only. Nothing was restarted or sent.
echo Keep the original backup and task pause intact until you approve restoration.
pause
exit /b %result%
