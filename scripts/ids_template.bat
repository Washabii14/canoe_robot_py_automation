@echo off
setlocal EnableDelayedExpansion

if "%~1"=="" (
  echo Usage: scripts\ids_template.bat ^<ID_PROFILE^> [CAN_TESTER_ID] [CAN_ECU_ID] [CAN_FUNCTIONAL_ID]
  echo Example: scripts\ids_template.bat CAN_BENCH_A 0x741 0x749 0x7DF
  exit /b 1
)

set ID_PROFILE=%~1
set CAN_TESTER_PHYSICAL_ID=%~2
set CAN_ECU_PHYSICAL_ID=%~3
set CAN_TESTER_FUNCTIONAL_ID=%~4
set EXITCODE=0

if "%CAN_TESTER_PHYSICAL_ID%"=="" set CAN_TESTER_PHYSICAL_ID=0x7E0
if "%CAN_ECU_PHYSICAL_ID%"=="" set CAN_ECU_PHYSICAL_ID=0x7E8
if "%CAN_TESTER_FUNCTIONAL_ID%"=="" set CAN_TESTER_FUNCTIONAL_ID=0x7DF

pushd "%~dp0.."
if errorlevel 1 exit /b !ERRORLEVEL!

powershell -ExecutionPolicy Bypass -File scripts\ids_template.ps1 ^
  -IdProfile "%ID_PROFILE%" ^
  -CanTesterPhysicalId "%CAN_TESTER_PHYSICAL_ID%" ^
  -CanEcuPhysicalId "%CAN_ECU_PHYSICAL_ID%" ^
  -CanTesterFunctionalId "%CAN_TESTER_FUNCTIONAL_ID%" ^
  -CreateBackup

set EXITCODE=!ERRORLEVEL!
popd
exit /b !EXITCODE!
