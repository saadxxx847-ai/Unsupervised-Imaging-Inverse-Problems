[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateNotNullOrEmpty()][string]$RunRoot,
    [Parameter(Mandatory = $true)][ValidateNotNullOrEmpty()][string]$ReservedSpec,
    [switch]$DryRun
)

$ErrorActionPreference = 'Continue'
$expectedHost = 'DESKTOP-KBM1345'
$stageWrapper = 'D:\DDM4IP-runtime\orchestration\run_bdd100k_synthetic_stage.ps1'
$python = 'E:\Anaconda3\envs\ddm4ip\python.exe'
$runner = 'D:\Unsupervised Imaging Inverse Problems\scripts\bdd100k_synthetic_runner.py'
$logPath = Join-Path $RunRoot 'recovery.log'
$claimPath = Join-Path $RunRoot 'execution.claim'
$lockPath = Join-Path $RunRoot 'recovery.lock'
$checkpointDir = Join-Path $RunRoot 'checkpoints'
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Append-RecoveryLog([string]$Message) {
    $line = ('{0} {1}{2}' -f ([DateTime]::UtcNow.ToString('o')), $Message, [Environment]::NewLine)
    [System.IO.File]::AppendAllText($logPath, $line, $utf8NoBom)
}

function Get-CurrentStatus {
    $statusPath = Join-Path $RunRoot 'status.json'
    if (-not (Test-Path -LiteralPath $statusPath -PathType Leaf)) { return $null }
    return (Get-Content -LiteralPath $statusPath -Raw -Encoding UTF8 | ConvertFrom-Json)
}

function Get-ActiveTrainingProcesses {
    $runName = [System.IO.Path]::GetFileName($RunRoot.TrimEnd('\'))
    return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -and
        ($_.CommandLine -like '*ddm4ip.main*' -or $_.CommandLine -like '*bdd100k_synthetic_runner.py*') -and
        $_.CommandLine -like ('*' + $runName + '*')
    })
}

function Acquire-RecoveryLock {
    try {
        $stream = New-Object System.IO.FileStream(
            $lockPath,
            [System.IO.FileMode]::CreateNew,
            [System.IO.FileAccess]::Write,
            [System.IO.FileShare]::None
        )
        $bytes = [System.Text.Encoding]::UTF8.GetBytes(('pid={0} started={1}{2}' -f $PID, [DateTime]::UtcNow.ToString('o'), [Environment]::NewLine))
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Dispose()
        return $true
    } catch {
        if (-not (Test-Path -LiteralPath $lockPath -PathType Leaf)) { return $false }
        $lock = Get-Item -LiteralPath $lockPath -ErrorAction SilentlyContinue
        if ($null -eq $lock -or (([DateTime]::UtcNow - $lock.LastWriteTimeUtc).TotalMinutes -lt 30)) {
            Append-RecoveryLog 'recovery lock is held; skipping duplicate invocation'
            return $false
        }
        $stale = Join-Path $RunRoot ('recovery.lock.stale-{0}.txt' -f [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ'))
        try {
            Move-Item -LiteralPath $lockPath -Destination $stale
            Append-RecoveryLog ('archived stale recovery lock: {0}' -f $stale)
        } catch {
            Append-RecoveryLog ('could not archive stale recovery lock: {0}' -f $_.Exception.Message)
            return $false
        }
        try {
            $stream = New-Object System.IO.FileStream(
                $lockPath,
                [System.IO.FileMode]::CreateNew,
                [System.IO.FileAccess]::Write,
                [System.IO.FileShare]::None
            )
            $bytes = [System.Text.Encoding]::UTF8.GetBytes(('pid={0} started={1}{2}' -f $PID, [DateTime]::UtcNow.ToString('o'), [Environment]::NewLine))
            $stream.Write($bytes, 0, $bytes.Length)
            $stream.Dispose()
            return $true
        } catch {
            Append-RecoveryLog ('could not acquire recovery lock after stale archive: {0}' -f $_.Exception.Message)
            return $false
        }
    }
}

if ($env:COMPUTERNAME -ne $expectedHost) {
    Append-RecoveryLog ('wrong host: {0}' -f $env:COMPUTERNAME)
    exit 2
}
if (-not (Test-Path -LiteralPath $python -PathType Leaf) -or -not (Test-Path -LiteralPath $runner -PathType Leaf)) {
    Append-RecoveryLog 'fixed project Python or runner is missing'
    exit 2
}
if (-not (Test-Path -LiteralPath $RunRoot -PathType Container)) {
    Append-RecoveryLog ('run root is missing: {0}' -f $RunRoot)
    exit 2
}
if (-not (Test-Path -LiteralPath $ReservedSpec -PathType Leaf)) {
    Append-RecoveryLog ('reserved spec is missing: {0}' -f $ReservedSpec)
    exit 2
}

$spec = Get-Content -LiteralPath $ReservedSpec -Raw -Encoding UTF8 | ConvertFrom-Json
if ($spec.run_root -ne $RunRoot -or $spec.stage -ne 'step1' -or $spec.mode -ne 'full') {
    Append-RecoveryLog 'reserved spec does not match a Step 1 full run root'
    exit 2
}

$status = Get-CurrentStatus
if ($null -eq $status) {
    Append-RecoveryLog 'status.json is missing'
    exit 2
}
if ($status.status -in @('SUCCESS', 'FAILED')) {
    Append-RecoveryLog ('recovery skipped for terminal status: {0}; FAILED needs a new authorized run' -f $status.status)
    exit 0
}

$active = @(Get-ActiveTrainingProcesses)
if ($active.Count -gt 0) {
    Append-RecoveryLog ('recovery skipped because an active training process exists: {0}' -f $active.Count)
    exit 0
}

if ($DryRun) {
    Append-RecoveryLog 'dry-run: would invoke the existing stage runner; claims and locks unchanged'
    exit 0
}

$ownedLock = Acquire-RecoveryLock
if (-not $ownedLock) { exit 0 }
try {
    $active = @(Get-ActiveTrainingProcesses)
    if ($active.Count -gt 0) {
        Append-RecoveryLog ('recovery skipped after locking because an active training process exists: {0}' -f $active.Count)
        exit 0
    }

    $checkpoints = @()
    if (Test-Path -LiteralPath $checkpointDir -PathType Container) {
        $checkpoints = @(Get-ChildItem -LiteralPath $checkpointDir -Filter 'training-state-*.pt' -File -ErrorAction SilentlyContinue)
    }
    if ($checkpoints.Count -eq 0) {
        Append-RecoveryLog 'no training-state checkpoint exists; recovery will start from step 0'
    } else {
        $latest = $checkpoints | Sort-Object {
            $match = [Regex]::Match($_.Name, '^training-state-(\d+)\.pt$')
            if ($match.Success) { [Int64]$match.Groups[1].Value } else { -1 }
        } -Descending | Select-Object -First 1
        Append-RecoveryLog ('latest training-state checkpoint: {0} ({1} bytes)' -f $latest.FullName, $latest.Length)
    }

    if (Test-Path -LiteralPath $claimPath -PathType Leaf) {
        $archivedClaim = Join-Path $RunRoot ('execution.claim.stale-{0}.json' -f [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ'))
        Move-Item -LiteralPath $claimPath -Destination $archivedClaim
        Append-RecoveryLog ('archived stale execution claim: {0}' -f $archivedClaim)
    }

    $env:TEMP = 'D:\DDM4IP-runtime\temp'
    $env:TMP = 'D:\DDM4IP-runtime\temp'
    $env:PIP_CACHE_DIR = 'D:\DDM4IP-runtime\pip-cache'
    $env:TORCH_HOME = 'D:\DDM4IP-runtime\torch-home'
    $env:XDG_CACHE_HOME = 'D:\DDM4IP-runtime\xdg-cache'
    Append-RecoveryLog 'invoking existing stage runner; the trainer will auto-load the latest checkpoint in this run root'
    & powershell.exe -NoLogo -NoProfile -NonInteractive -File $stageWrapper -Action execute -SpecPath $ReservedSpec
    $exitCode = $LASTEXITCODE
    Append-RecoveryLog ('stage runner exit code: {0}' -f $exitCode)
    exit $exitCode
} finally {
    if (Test-Path -LiteralPath $lockPath -PathType Leaf) {
        Remove-Item -LiteralPath $lockPath -Force
    }
}
