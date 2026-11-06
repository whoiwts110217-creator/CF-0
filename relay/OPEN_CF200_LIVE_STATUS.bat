@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 cf200_live_status.py
) else (
  python cf200_live_status.py
)
if errorlevel 1 pause
