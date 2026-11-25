@echo off
REM Use SETUP_CF0.bat for the CF-0 relay.
REM cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
cd /d "%~dp0..\.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\..\bridge\setup_windows.ps1" remove
pause
