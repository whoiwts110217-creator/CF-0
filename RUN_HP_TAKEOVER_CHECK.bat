@echo off
REM cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
setlocal
cd /d "%~dp0"
echo Caveman Focus - owner-approved HP connection diagnostic
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0relay\hp_takeover_check.ps1" -RunPoll
if errorlevel 1 echo Connection check reported a failure; review the printed result.
echo This checks only the existing allowlisted relay; no unrestricted PC access.
pause
