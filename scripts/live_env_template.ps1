param(
    [Parameter(Mandatory = $true)]
    [string]$CanoeConfigPath,

    [ValidateSet("can", "doip")]
    [string]$UdsTransport = "can",

    [string]$CanoeDiagMethod = "diagnostics:SendRequest",
    [double]$UdsTimeoutS = 2.0,
    [int]$UdsRetryCount = 1,
    [double]$UdsRetryDelayS = 0.2,
    [double]$UdsWaitPollIntervalS = 0.2,
    [string]$MockFixturePath = "config/fixtures/uds_mock_responses.json",
    [bool]$AutoStartMeasurement = $true,
    [string]$EnvFile = "resources/variables/env.robot",
    [switch]$CreateBackup
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

if (-not [System.IO.Path]::IsPathRooted($EnvFile)) {
    $EnvFile = Join-Path $RepoRoot $EnvFile
}

if (-not (Test-Path $EnvFile)) {
    Write-Error "env file not found: $EnvFile"
    exit 1
}

$updates = @{
    "EXECUTION_BACKEND" = "live"
    "UDS_TRANSPORT" = $UdsTransport
    "MOCK_FIXTURE_PATH" = $MockFixturePath
    "CANOE_CONFIG_PATH" = $CanoeConfigPath
    "AUTO_START_MEASUREMENT" = if ($AutoStartMeasurement) { '${True}' } else { '${False}' }
    "CANOE_DIAG_METHOD" = $CanoeDiagMethod
    "UDS_TIMEOUT_S" = [string]$UdsTimeoutS
    "UDS_RETRY_COUNT" = [string]$UdsRetryCount
    "UDS_RETRY_DELAY_S" = [string]$UdsRetryDelayS
    "UDS_WAIT_POLL_INTERVAL_S" = [string]$UdsWaitPollIntervalS
}

if ($CreateBackup) {
    $backupPath = "$EnvFile.bak"
    Copy-Item -Path $EnvFile -Destination $backupPath -Force
    Write-Host "Backup created: $backupPath"
}

$lines = [System.Collections.Generic.List[string]]::new()
Get-Content -Path $EnvFile -Encoding utf8 | ForEach-Object { [void]$lines.Add($_) }

foreach ($key in $updates.Keys) {
    $pattern = "^\$\{$key\}\s+.*$"
    $newLine = '$' + '{' + $key + '}    ' + $updates[$key]
    $matched = $false
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match $pattern) {
            $lines[$i] = $newLine
            $matched = $true
            break
        }
    }
    if (-not $matched) {
        [void]$lines.Add($newLine)
    }
}

Set-Content -Path $EnvFile -Value $lines -Encoding utf8
Write-Host "Updated $EnvFile for live backend."
