@echo off
setlocal
cd /d "%~dp0"
set "STATUS=%TEMP%\CF200_LIVE_STATUS.txt"
> "%STATUS%" echo CAVEMAN FOCUS - CF-200 STATUS
>> "%STATUS%" echo Notepad opened locally. Automatic GitHub updates appear in the companion live window.
>> "%STATUS%" echo Notepad may not reload external file changes. This file is a launch marker.
start "" notepad.exe "%STATUS%"
where py >nul 2>nul
if not errorlevel 1 (
  start "" py -3 cf200_live_status.py
) else (
  where python >nul 2>nul
  if not errorlevel 1 (
    start "" python cf200_live_status.py
  ) else (
    echo Python not found. Notepad has still been launched.
    pause
  )
)
