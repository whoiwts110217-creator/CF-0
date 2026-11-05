@echo off
REM cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
cd /d "%~dp0"
echo CF-0 relay local task status:
py -3 relay\cf_public_relay.py status
echo Windows scheduled task status:
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "relay\install_task.ps1" status
pause
