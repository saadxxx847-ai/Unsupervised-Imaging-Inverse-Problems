[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateSet('prepare', 'execute', 'dispatch-failed')][string]$Action,
    [Parameter(Mandatory = $true)][ValidateNotNullOrEmpty()][string]$SpecPath
)

$ErrorActionPreference = 'Continue'
$expectedHost = 'DESKTOP-KBM1345'
$projectRoot = 'D:\Unsupervised Imaging Inverse Problems'
$python = 'E:\Anaconda3\envs\ddm4ip\python.exe'
$runner = Join-Path $projectRoot 'scripts\bdd100k_synthetic_runner.py'

if ($env:COMPUTERNAME -ne $expectedHost) {
    Write-Error "wrong host: $env:COMPUTERNAME"
    exit 2
}
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    Write-Error "fixed Python is missing: $python"
    exit 2
}
if (-not (Test-Path -LiteralPath $runner -PathType Leaf)) {
    Write-Error "synthetic runner is missing: $runner"
    exit 2
}

$env:TEMP = 'D:\DDM4IP-runtime\temp'
$env:TMP = 'D:\DDM4IP-runtime\temp'
$env:PIP_CACHE_DIR = 'D:\DDM4IP-runtime\pip-cache'
$env:TORCH_HOME = 'D:\DDM4IP-runtime\torch-home'
$env:XDG_CACHE_HOME = 'D:\DDM4IP-runtime\xdg-cache'
$env:HF_HOME = 'D:\DDM4IP-runtime\hf-cache'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'

& $python $runner $Action --spec $SpecPath --current-host $expectedHost --current-python $python
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Write-Error "synthetic stage runner failed with exit code $exitCode"
}
exit $exitCode
