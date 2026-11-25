@echo off
REM cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
REM One setup for the CF-0 relay. Safe to run again.
REM SETUP_CF0.bat -Uninstall removes only the scheduled task.
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup_cf0.ps1" %*
set "CODE=%ERRORLEVEL%"
echo.
if not "%CODE%"=="0" echo SETUP FAILED. Read the PASS/FAIL summary above. Nothing was deleted.
pause
exit /b %CODE%
