param([int]$RefreshSeconds=15,[switch]$Once)
$maxStep=1054720
$ErrorActionPreference='SilentlyContinue'
do {
  if(-not $Once){Clear-Host}
  $rows=foreach($seed in 0..4){
    $taskName="DDM4IP-BDD100K-SYNTH-Step2-Full-seed$seed"
    $run="D:\DDM4IP-runtime\experiments\bdd100k-synthetic-motionblur-v1-step2-full-seed$seed"
    $task=Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    $taskInfo=if($task){$task|Get-ScheduledTaskInfo}else{$null}
    $statusPath=Join-Path $run 'status.json'
    $logPath=Join-Path $run 'task.log'
    $status=if(Test-Path -LiteralPath $statusPath){(Get-Content -Raw -LiteralPath $statusPath|ConvertFrom-Json).status}else{'NOT_STARTED'}
    [int64]$step=0
    if(Test-Path -LiteralPath $logPath){
      $hit=Select-String -LiteralPath $logPath -Pattern '^\[[^\]]+\]\[\s*(\d+)\]'|Select-Object -Last 1
      if($hit -and $hit.Line -match '^\[[^\]]+\]\[\s*(\d+)\]'){$step=[int64]$Matches[1]}
    }
    $ckpt=Get-ChildItem -LiteralPath (Join-Path $run 'checkpoints') -Filter 'training-state-*.pt'|ForEach-Object {if($_.BaseName -match 'training-state-(\d+)$'){[int64]$Matches[1]}}|Measure-Object -Maximum
    if($ckpt.Maximum -and $ckpt.Maximum -gt $step){$step=[int64]$ckpt.Maximum}
    [pscustomobject]@{Seed=$seed;Task=if($task){$task.State}else{'NotCreated'};Result=if($taskInfo){$taskInfo.LastTaskResult}else{'-'};Status=$status;Step="$step / $maxStep";Percent=('{0:N2}%' -f (100*$step/$maxStep));LogUpdated=if(Test-Path -LiteralPath $logPath){(Get-Item -LiteralPath $logPath).LastWriteTime}else{'-'}}
  }
  Write-Host (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ' Ctrl+C stops this viewer only; training continues.'
  $rows|Format-Table -AutoSize
  if(-not $Once){Start-Sleep -Seconds $RefreshSeconds}
} until($Once)