@echo off
setlocal
REM Caveman Focus HP maintenance status only. Does not start, enable or alter tasks.
cd /d "%~dp0"
if not exist "%~dp0relay\hp_takeover_check.ps1" (
  echo MISSING_REVIEWED_SOURCE=relay\hp_takeover_check.ps1
  echo LOCAL_CHANGES=NONE
  pause
  exit /b 2
)
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0relay\hp_takeover_check.ps1" -MaintenanceAudit
set "result=%ERRORLEVEL%"
echo.
echo This reports current local observations only. Nothing was restarted or sent.
echo Keep the original backup and task pause intact until you approve restoration.
pause
exit /b %result%
