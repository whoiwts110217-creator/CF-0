@echo off
REM cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
setlocal
cd /d "%~dp0"
echo Caveman Focus HP Bridge - Offline Verification
py -3 "bridge\cf_hp_bridge.py" demo
if errorlevel 1 goto :failed
py -3 -m unittest discover -s "bridge\tests" -q
if errorlevel 1 goto :failed
echo Demo and unit tests passed on THIS computer.
echo This does not establish a private GitHub or ChatGPT account connection.
pause
exit /b 0
:failed
echo Verification failed. Do not enable scheduling.
pause
exit /b 1
