@echo off
REM cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
setlocal
cd /d "%~dp0"
echo Caveman Focus HP Bridge - One authorized private mailbox poll
REM Reuse the DPAPI-encrypted credential created by SETUP_HP_BRIDGE_WINDOWS.bat.
REM Never require a token pasted into this batch file or interactive terminal.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0bridge\setup_windows.ps1" once
if errorlevel 1 goto :failed
echo The private mailbox poll completed. See repository receipt and local state.
pause
exit /b 0
:failed
echo Poll failed. Check local output; no successful receipt is assumed.
pause
exit /b 1
