@echo off
setlocal

REM Get the directory of the script
set DIR=%~dp0

REM Add the directory to the PATH
setx PATH "%PATH%;%DIR%"

REM Create an alias for gcu
set ALIAS_CMD=python %DIR%main.py
doskey gcu=%ALIAS_CMD%

echo Setup complete. You can now use 'gcu' to run gpt-cli-utils.
pause
