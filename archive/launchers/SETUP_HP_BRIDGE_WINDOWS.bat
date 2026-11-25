@echo off
REM Use SETUP_CF0.bat for the CF-0 relay.
REM cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
cd /d "%~dp0..\.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\..\bridge\setup_windows.ps1" configure
if errorlevel 1 (
  echo Private mailbox setup did not pass. No scheduled task was installed.
  pause
  exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\..\bridge\setup_windows.ps1" install
if errorlevel 1 (
  echo Scheduler setup failed. Check the displayed error.
  pause
  exit /b 1
)
echo HP bridge configured. Check first scheduled run after signing in.
pause
