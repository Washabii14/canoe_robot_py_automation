param(
    [Parameter(Mandatory = $true)]
    [string]$IdProfile,

    [string]$CanTesterPhysicalId = "0x7E0",
    [string]$CanEcuPhysicalId = "0x7E8",
    [string]$CanTesterFunctionalId = "0x7DF",
    [string]$DoipTesterSourceAddr = "0x0E80",
    [string]$DoipEcuTargetAddr = "0x0001",
    [string]$EcuLogicalName = "ECU_PLACEHOLDER",
    [string]$ProgrammingVariant = "VARIANT_PLACEHOLDER",
    [string]$IdsFile = "resources/variables/ids.robot",
    [switch]$CreateBackup
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

if (-not [System.IO.Path]::IsPathRooted($IdsFile)) {
    $IdsFile = Join-Path $RepoRoot $IdsFile
}

if (-not (Test-Path $IdsFile)) {
    Write-Error "ids file not found: $IdsFile"
    exit 1
}

$updates = @{
    "ID_PROFILE" = $IdProfile
    "CAN_TESTER_PHYSICAL_ID" = $CanTesterPhysicalId
    "CAN_ECU_PHYSICAL_ID" = $CanEcuPhysicalId
    "CAN_TESTER_FUNCTIONAL_ID" = $CanTesterFunctionalId
    "DOIP_TESTER_SOURCE_ADDR" = $DoipTesterSourceAddr
    "DOIP_ECU_TARGET_ADDR" = $DoipEcuTargetAddr
    "ECU_LOGICAL_NAME" = $EcuLogicalName
    "PROGRAMMING_VARIANT" = $ProgrammingVariant
}

if ($CreateBackup) {
    $backupPath = "$IdsFile.bak"
    Copy-Item -Path $IdsFile -Destination $backupPath -Force
    Write-Host "Backup created: $backupPath"
}

$lines = [System.Collections.Generic.List[string]]::new()
Get-Content -Path $IdsFile -Encoding utf8 | ForEach-Object { [void]$lines.Add($_) }

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

Set-Content -Path $IdsFile -Value $lines -Encoding utf8
Write-Host "Updated $IdsFile with profile $IdProfile."
