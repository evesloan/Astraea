$Mode='orchard-receiving-check'
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$project=Join-Path (Split-Path $root) 'Astraea-construction-6c52b7a8\Game'
$engine=Join-Path (Split-Path $root) 'astraea-e3af0334-inspection-20261022\engine\Godot_v4.6.3-stable_win64.exe'
$expected='3a455e8508306558fd44caf2ede5c7fd02ccb6dd'
$revision=(& git -C (Split-Path $project) rev-parse HEAD).Trim()
if($revision -ne $expected){throw 'Wrong source revision'}
if((Get-FileHash -LiteralPath $engine -Algorithm SHA256).Hash -ne 'EF90E929BA1A6A4322860285D97F40F4AA349C90329A91B0E8B55B8DF0F4CB00'){throw 'Engine differs'}
$conflicts=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -match 'godot|astraea|blender|msbuild|ninja|^Unity\.exe$|UnityShaderCompiler|AssetImportWorker'})
if($conflicts.Count){throw 'Competing process found'}
$available=(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB
if($available -lt 10){throw 'Insufficient starting RAM headroom'}
$run=Join-Path $root ($Mode+'-014')
if(Test-Path -LiteralPath $run){throw 'Preserving existing attempt; refusing duplicate'}
New-Item -ItemType Directory -Path $run|Out-Null
$argsList=@('--rendering-method','gl_compatibility','--path',('"'+$project+'"'),'--log-file',('"'+(Join-Path $run 'engine.log')+'"'),'--script','res://orchard_tram_interior_20261025/integration/check_installed_components.gd','--',('--result="'+(Join-Path $run 'result.json')+'"'))
$limit=240
$samples=[Collections.Generic.List[object]]::new();$reason='unknown';$proc=$null;$started=[DateTime]::UtcNow;$gpuLow=0;$forced=$false;$previousCpu=0.0;$previousElapsed=0.0
try{
 $proc=Start-Process -FilePath $engine -ArgumentList $argsList -WorkingDirectory $project -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $run 'stdout.log') -RedirectStandardError (Join-Path $run 'stderr.log')
 $proc.Id|Set-Content -LiteralPath (Join-Path $run 'pid.txt')
 Write-Output ('Started '+$Mode+' PID '+$proc.Id)
 while(-not $proc.HasExited){
  $proc.Refresh();$elapsed=([DateTime]::UtcNow-$started).TotalSeconds
  $available=(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB
  $disk=(Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace/1GB
  $gpu=((& nvidia-smi --query-gpu=memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits|Select-Object -First 1).Split(',')|ForEach-Object {[double]$_.Trim()})
  $row=[pscustomobject]@{utc=[DateTime]::UtcNow.ToString('o');elapsed_seconds=[math]::Round($elapsed,2);pid=$proc.Id;resident_GiB=[math]::Round($proc.WorkingSet64/1GB,3);private_GiB=[math]::Round($proc.PrivateMemorySize64/1GB,3);available_RAM_GiB=[math]::Round($available,3);disk_free_GiB=[math]::Round($disk,3);GPU_used_MiB=$gpu[0];GPU_free_MiB=$gpu[1];GPU_util_percent=$gpu[2];responding=$proc.Responding}
  $cpu=$proc.TotalProcessorTime.TotalSeconds; $row|Add-Member NoteProperty process_CPU_percent_one_core ([math]::Round(100*($cpu-$previousCpu)/[math]::Max(0.001,$elapsed-$previousElapsed),2));$previousCpu=$cpu;$previousElapsed=$elapsed; $samples.Add($row);$row|Export-Csv -LiteralPath (Join-Path $run 'samples.csv') -Append -NoTypeInformation
  if($samples.Count%5 -eq 1){$row|ConvertTo-Json -Compress|Write-Output}
  if($gpu[1] -lt 384){$gpuLow++}else{$gpuLow=0}
  if($available -lt 5){$reason='available_RAM_below_5_GiB';break}
  if($proc.PrivateMemorySize64 -gt 16GB){$reason='private_memory_above_16_GiB';break}
  if($gpuLow -ge 2){$reason='GPU_free_below_384_MiB_twice';break}
  if($disk -lt 20){$reason='disk_free_below_20_GiB';break}
  $errors=Get-Content -LiteralPath (Join-Path $run 'stderr.log') -Tail 100 -ErrorAction SilentlyContinue
  if($errors -match 'Element limit reached|SCRIPT ERROR|Assertion failed'){$reason='engine_error_safety_stop';break}
  if($elapsed -ge $limit){$reason='observation_timeout';break}
  Start-Sleep -Seconds 3
 }
 if($proc.HasExited){$reason='process_exited'}
}finally{
 if($proc -and -not $proc.HasExited){[void]$proc.CloseMainWindow();if(-not $proc.WaitForExit(3000)){$forced=$true;$proc.Kill();$proc.WaitForExit()}}
 $summary=[ordered]@{mode=$Mode;revision=$revision;started_utc=$started;ended_utc=[DateTime]::UtcNow;reason=$reason;forced_stop=$forced;exit_code=if($proc){$proc.ExitCode}else{$null};max_private_GiB=($samples|Measure-Object private_GiB -Maximum).Maximum;max_resident_GiB=($samples|Measure-Object resident_GiB -Maximum).Maximum;min_available_RAM_GiB=($samples|Measure-Object available_RAM_GiB -Minimum).Minimum;samples=$samples.Count}
 $summary|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $run 'summary.json')
 $summary|ConvertTo-Json|Write-Output
}





