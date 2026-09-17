param([Parameter(Mandatory=$true)][string]$SpecPath)
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
if ((hostname).Trim() -ne 'DESKTOP-KBM1345') { throw 'Wrong host' }
$spec=Get-Content -LiteralPath $SpecPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($spec.task_name -notmatch '^DDM4IP-BDD100K-[A-Za-z0-9_-]+$') { throw 'Invalid task name' }
$timeoutMinutes = if ($spec.mode -eq 'validation') { 10 } else { [int]$spec.execution_timeout_minutes }
if ($timeoutMinutes -lt 1 -or $timeoutMinutes -gt 4320) { throw 'Invalid execution timeout' }
$existing=Get-ScheduledTask | Where-Object { $_.TaskName -eq $spec.task_name }
if ($existing) { throw 'Task already exists; refusing overwrite' }
$env:TEMP='D:\DDM4IP-runtime\temp'; $env:TMP=$env:TEMP
$env:PIP_CACHE_DIR='D:\DDM4IP-runtime\pip-cache'
$env:TORCH_HOME='D:\DDM4IP-runtime\torch-home'
$env:XDG_CACHE_HOME='D:\DDM4IP-runtime\xdg-cache'
$env:MPLCONFIGDIR='D:\DDM4IP-runtime\xdg-cache\matplotlib'
$env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'
$engine=Join-Path $PSScriptRoot 'bdd100k_runner.py'
$python='E:\Anaconda3\envs\ddm4ip\python.exe'
$previous=$ErrorActionPreference
try {
    $ErrorActionPreference='Continue'
    & $python $engine prepare $SpecPath
    $nativeCode=$LASTEXITCODE
} finally { $ErrorActionPreference=$previous }
if ($nativeCode -ne 0) { throw "Runner preflight failed with exit $nativeCode" }
$reservedSpec=Join-Path $spec.run_root 'spec.json'
try {
    $runner=Join-Path $PSScriptRoot 'run_bdd100k_stage.ps1'
    $arguments='-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'+$runner+'" -SpecPath "'+$reservedSpec+'"'
    $action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arguments -WorkingDirectory 'D:\Unsupervised Imaging Inverse Problems'
    $identity=[Security.Principal.WindowsIdentity]::GetCurrent().Name
    $principal=New-ScheduledTaskPrincipal -UserId $identity -LogonType S4U -RunLevel Limited
    $settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes $timeoutMinutes) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    $description="BDD100K $($spec.stage) $($spec.mode); frozen spec and no-overwrite runner contract"
    Register-ScheduledTask -TaskName $spec.task_name -Action $action -Principal $principal -Settings $settings -Description $description -ErrorAction Stop | Out-Null
    Start-ScheduledTask -TaskName $spec.task_name -ErrorAction Stop
    [pscustomobject]@{task_name=$spec.task_name;run_root=$spec.run_root;log_path=(Join-Path $spec.run_root 'task.log')} | ConvertTo-Json
} catch {
    $launchError=$_
    $ErrorActionPreference='Continue'
    & $python $engine dispatch-failed $reservedSpec
    $ErrorActionPreference=$previous
    throw $launchError
}
