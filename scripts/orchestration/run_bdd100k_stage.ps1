param([Parameter(Mandatory=$true)][string]$SpecPath)
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
if ((hostname).Trim() -ne 'DESKTOP-KBM1345') { throw 'Wrong host' }
$env:TEMP='D:\DDM4IP-runtime\temp'; $env:TMP=$env:TEMP
$env:PIP_CACHE_DIR='D:\DDM4IP-runtime\pip-cache'
$env:TORCH_HOME='D:\DDM4IP-runtime\torch-home'
$env:XDG_CACHE_HOME='D:\DDM4IP-runtime\xdg-cache'
$env:MPLCONFIGDIR='D:\DDM4IP-runtime\xdg-cache\matplotlib'
$env:PYTHONPYCACHEPREFIX='D:\DDM4IP-runtime\orchestration\pycache'
$env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'
Set-Location -LiteralPath 'D:\Unsupervised Imaging Inverse Problems'
$previous=$ErrorActionPreference
try {
    $ErrorActionPreference='Continue'
    & 'E:\Anaconda3\envs\ddm4ip\python.exe' "$PSScriptRoot\bdd100k_runner.py" execute $SpecPath
    $nativeCode=$LASTEXITCODE
} finally { $ErrorActionPreference=$previous }
exit $nativeCode
