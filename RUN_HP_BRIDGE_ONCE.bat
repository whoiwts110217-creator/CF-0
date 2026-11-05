@echo off
REM cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
setlocal
cd /d "%~dp0"
if "%CF_BRIDGE_REPO%"=="" goto :config
if "%CF_BRIDGE_TOKEN%"=="" if "%GITHUB_TOKEN%"=="" goto :config
echo Caveman Focus HP Bridge - One Private Mailbox Poll
py -3 "bridge\cf_hp_bridge.py" once
if errorlevel 1 goto :failed
echo One private mailbox poll completed. Check receipts and task evidence.
pause
exit /b 0
:config
echo Missing CF_BRIDGE_REPO or CF_BRIDGE_TOKEN.
echo Create a separate PRIVATE repository and set a narrowly scoped token locally.
pause
exit /b 2
:failed
echo Poll failed. Check local output; no account connection was claimed.
pause
exit /b 1
