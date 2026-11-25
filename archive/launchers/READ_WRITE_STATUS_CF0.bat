@echo off
REM Use SETUP_CF0.bat for the CF-0 relay.
REM cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
cd /d "%~dp0..\.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "relay\cf_public_relay_rw.ps1" status
pause
