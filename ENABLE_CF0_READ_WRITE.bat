@echo off
REM cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "relay\cf_public_relay_rw.ps1" enable
if errorlevel 1 echo READ/WRITE setup not completed. Existing relay was not intentionally reset.
pause
