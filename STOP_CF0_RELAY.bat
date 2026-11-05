@echo off
REM cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "relay\install_task.ps1" remove
pause
