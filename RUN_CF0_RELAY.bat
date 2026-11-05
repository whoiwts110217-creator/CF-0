@echo off
REM cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
cd /d "%~dp0"
echo Caveman Focus public GitHub command relay - one poll.
py -3 relay\cf_public_relay.py once
if errorlevel 1 echo Command poll failed. Check HTTPS/network.
pause
