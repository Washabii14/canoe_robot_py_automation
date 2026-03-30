@echo off
setlocal

if "%~1"=="" (
  echo Usage: scripts\live_gate.bat ^<CANOE_CFG_PATH^> [--run-robot]
  exit /b 1
)

set CANOE_CFG=%~1
set RUN_ROBOT=%~2
set PYTHON_EXE=python

echo Installing Python dependencies...
%PYTHON_EXE% -m pip install -r requirements.txt
if errorlevel 1 exit /b %errorlevel%

echo Running live preflight gate...
%PYTHON_EXE% -m scripts.live_gate --canoe-config-path "%CANOE_CFG%"
if errorlevel 1 exit /b %errorlevel%

if /I "%RUN_ROBOT%"=="--run-robot" (
  echo Running Robot suites against live backend...
  robot tests/diagnostics tests/flashing
  if errorlevel 1 exit /b %errorlevel%
)

echo Live gate completed successfully.
exit /b 0
