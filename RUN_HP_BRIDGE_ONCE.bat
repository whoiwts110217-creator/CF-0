@echo off
REM cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
setlocal
cd /d "%~dp0"
if exist "%LOCALAPPDATA%\CavemanFocus\HPBridge\config.json" (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0bridge\setup_windows.ps1" once
  if errorlevel 1 goto :failed
  echo Private mailbox poll finished.
  pause
  exit /b 0
)
if "%CF_BRIDGE_REPO%"=="" goto :config
if "%CF_BRIDGE_TOKEN%"=="" if "%GITHUB_TOKEN%"=="" goto :config
py -3 "bridge\cf_hp_bridge.py" once
if errorlevel 1 goto :failed
pause
exit /b 0
:config
echo Private mailbox not configured. Use SETUP_HP_BRIDGE_WINDOWS.bat first.
pause
exit /b 2
:failed
echo Bridge poll failed. Check the displayed error.
pause
exit /b 1
