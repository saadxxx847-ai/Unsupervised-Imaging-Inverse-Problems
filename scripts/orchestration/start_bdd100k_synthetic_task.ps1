[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateNotNullOrEmpty()][string]$TaskName,
    [Parameter(Mandatory = $true)][ValidateNotNullOrEmpty()][string]$SpecPath
)

$ErrorActionPreference = 'Stop'
$expectedHost = 'DESKTOP-KBM1345'
$runWrapper = 'D:\DDM4IP-runtime\orchestration\run_bdd100k_synthetic_stage.ps1'

if ($env:COMPUTERNAME -ne $expectedHost) {
    throw "wrong host: $env:COMPUTERNAME"
}
if (-not (Test-Path -LiteralPath $runWrapper -PathType Leaf)) {
    throw "runtime wrapper is missing: $runWrapper"
}
if (-not (Test-Path -LiteralPath $SpecPath -PathType Leaf)) {
    throw "reserved spec is missing: $SpecPath"
}
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    throw "scheduled task already exists: $TaskName"
}

# Reservation is metadata-only.  This launcher is the only file allowed to
# register/start a pilot, full, or audit task; this script is not invoked here.
powershell.exe -NoLogo -NoProfile -NonInteractive -File $runWrapper -Action prepare -SpecPath $SpecPath
if ($LASTEXITCODE -ne 0) {
    throw "prepare failed with exit code $LASTEXITCODE"
}

$spec = Get-Content -LiteralPath $SpecPath -Raw -Encoding UTF8 | ConvertFrom-Json
$reservedSpec = Join-Path ([string]$spec.run_root) 'spec.json'
if (-not (Test-Path -LiteralPath $reservedSpec -PathType Leaf)) {
    throw "reserved spec was not written: $reservedSpec"
}

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument (
    "-NoLogo -NoProfile -NonInteractive -File `"$runWrapper`" -Action execute -SpecPath `"$reservedSpec`""
)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
Register-ScheduledTask -TaskName $TaskName -Action $action -Principal $principal -Description 'BDD100K synthetic benchmark isolated stage'
Start-ScheduledTask -TaskName $TaskName
