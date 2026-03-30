param(
    [Parameter(Mandatory = $true)]
    [string]$CanoeConfigPath,

    [switch]$RunRobot,

    [string]$PythonExe = "python",
    [string]$RobotExe = "robot"
)

$ErrorActionPreference = "Stop"

Write-Host "Installing Python dependencies..."
& $PythonExe -m pip install -r requirements.txt

Write-Host "Running live preflight gate..."
& $PythonExe -m scripts.live_gate --canoe-config-path "$CanoeConfigPath"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Live gate preflight failed (exit code: $LASTEXITCODE)."
    exit $LASTEXITCODE
}

if ($RunRobot) {
    Write-Host "Running Robot suites against live backend..."
    & $RobotExe tests/diagnostics tests/flashing
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Robot live run failed (exit code: $LASTEXITCODE)."
        exit $LASTEXITCODE
    }
}

Write-Host "Live gate completed successfully."
