param(
    [Parameter(Mandatory = $true)]
    [string]$CanoeConfigPath,

    [switch]$RunRobot,

    [string]$PythonExe = "python",
    [string]$RobotExe = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

Push-Location $RepoRoot
try {
    Write-Host "Installing Python dependencies..."
    & $PythonExe -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Dependency install failed (exit code: $LASTEXITCODE)."
        exit $LASTEXITCODE
    }

    & $PythonExe -c "import win32com.client" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing pywin32 for CANoe COM access..."
        & $PythonExe -m pip install pywin32
        if ($LASTEXITCODE -ne 0) {
            Write-Error "pywin32 install failed (exit code: $LASTEXITCODE)."
            exit $LASTEXITCODE
        }
    }

    Write-Host "Installing editable project package..."
    & $PythonExe -m pip install -e .
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Editable package install failed (exit code: $LASTEXITCODE)."
        exit $LASTEXITCODE
    }

    Write-Host "Running live preflight gate..."
    & $PythonExe -m scripts.live_gate --canoe-config-path "$CanoeConfigPath"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Live gate preflight failed (exit code: $LASTEXITCODE)."
        exit $LASTEXITCODE
    }

    if ($RunRobot) {
        Write-Host "Running Robot suites against live backend..."
        if ([string]::IsNullOrWhiteSpace($RobotExe)) {
            & $PythonExe -m robot tests/diagnostics tests/flashing
        } else {
            & $RobotExe tests/diagnostics tests/flashing
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Robot live run failed (exit code: $LASTEXITCODE)."
            exit $LASTEXITCODE
        }
    }

    Write-Host "Live gate completed successfully."
}
finally {
    Pop-Location
}
