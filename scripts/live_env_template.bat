@echo off
setlocal EnableDelayedExpansion

if "%~1"=="" (
  echo Usage: scripts\live_env_template.bat ^<CANOE_CFG_PATH^> [can^|doip] [diagnostics:SendRequest] [wait_poll_interval_s]
  exit /b 1
)

set CANOE_CFG=%~1
set UDS_TRANSPORT=%~2
set CANOE_DIAG_METHOD=%~3
set UDS_WAIT_POLL_INTERVAL_S=%~4
set EXITCODE=0

if "%UDS_TRANSPORT%"=="" set UDS_TRANSPORT=can
if "%CANOE_DIAG_METHOD%"=="" set CANOE_DIAG_METHOD=diagnostics:SendRequest
if "%UDS_WAIT_POLL_INTERVAL_S%"=="" set UDS_WAIT_POLL_INTERVAL_S=0.2

pushd "%~dp0.."
if errorlevel 1 exit /b !ERRORLEVEL!

powershell -ExecutionPolicy Bypass -File scripts\live_env_template.ps1 ^
  -CanoeConfigPath "%CANOE_CFG%" ^
  -UdsTransport "%UDS_TRANSPORT%" ^
  -CanoeDiagMethod "%CANOE_DIAG_METHOD%" ^
  -UdsWaitPollIntervalS "%UDS_WAIT_POLL_INTERVAL_S%" ^
  -CreateBackup

set EXITCODE=!ERRORLEVEL!
popd
exit /b !EXITCODE!
