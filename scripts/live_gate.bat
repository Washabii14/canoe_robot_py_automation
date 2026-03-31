@echo off
setlocal EnableDelayedExpansion

if "%~1"=="" (
  echo Usage: scripts\live_gate.bat ^<CANOE_CFG_PATH^> [--run-robot]
  exit /b 1
)

pushd "%~dp0.."
if errorlevel 1 exit /b !ERRORLEVEL!

set CANOE_CFG=%~1
set RUN_ROBOT=%~2
set PYTHON_EXE=python
set EXITCODE=0

echo Installing Python dependencies...
%PYTHON_EXE% -m pip install -r requirements.txt
if errorlevel 1 (
  set EXITCODE=!ERRORLEVEL!
  goto :cleanup
)

%PYTHON_EXE% -c "import win32com.client" >nul 2>&1
if errorlevel 1 (
  echo Installing pywin32 for CANoe COM access...
  %PYTHON_EXE% -m pip install pywin32
  if errorlevel 1 (
    set EXITCODE=!ERRORLEVEL!
    goto :cleanup
  )
)

echo Installing editable project package...
%PYTHON_EXE% -m pip install -e .
if errorlevel 1 (
  set EXITCODE=!ERRORLEVEL!
  goto :cleanup
)

echo Running live preflight gate...
%PYTHON_EXE% -m scripts.live_gate --canoe-config-path "%CANOE_CFG%"
if errorlevel 1 (
  set EXITCODE=!ERRORLEVEL!
  goto :cleanup
)

if /I "%RUN_ROBOT%"=="--run-robot" (
  echo Running Robot suites against live backend...
  %PYTHON_EXE% -m robot tests/diagnostics tests/flashing
  if errorlevel 1 (
    set EXITCODE=!ERRORLEVEL!
    goto :cleanup
  )
)

echo Live gate completed successfully.

:cleanup
popd
exit /b !EXITCODE!
