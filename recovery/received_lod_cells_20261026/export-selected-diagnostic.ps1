param([Parameter(Mandatory=$true)][string]$ExpectedRevision)
$ErrorActionPreference='Stop'
$workspace=Split-Path $PSScriptRoot
$project=Join-Path $workspace 'Astraea-construction-6c52b7a8\Game'
$engine=Join-Path $workspace 'astraea-e3af0334-inspection-20261022\engine\Godot_v4.6.3-stable_win64.exe'
if((& git -C (Split-Path $project) rev-parse HEAD).Trim() -ne $ExpectedRevision){throw 'Wrong protected source'}
if(Get-CimInstance Win32_Process|Where-Object {$_.Name -match 'godot|astraea|blender|msbuild|ninja'}){throw 'Competing engine/build process'}
if((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB -lt 10){throw 'Starting RAM below10GiB'}
if((Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace/1GB -lt 40){throw 'Starting disk below40GiB'}
if((Get-FileHash $engine).Hash -ne 'EF90E929BA1A6A4322860285D97F40F4AA349C90329A91B0E8B55B8DF0F4CB00'){throw 'Editor changed'}
$template=Join-Path $env:APPDATA 'Godot\export_templates\4.6.3.stable\windows_release_x86_64.exe'
if((Get-FileHash $template).Hash -ne '91724F15024A3A545E28CCD83134403D31CE2323A38E51C95E4DFA282F732AB6'){throw 'Template changed'}
$output=Join-Path $workspace ('Astraea-Windows-Diagnostic-'+$ExpectedRevision.Substring(0,8))
if(Test-Path -LiteralPath $output){throw 'Output already exists; preserve existing work'}
New-Item -ItemType Directory -Path $output|Out-Null
$logs=Join-Path $PSScriptRoot ('export-selected-'+$ExpectedRevision.Substring(0,8))
if(Test-Path -LiteralPath $logs){throw 'Evidence already exists'}
New-Item -ItemType Directory -Path $logs|Out-Null
$oldScratch=$env:ASTRAEA_CONTRACT_PACK_TMP
$env:ASTRAEA_CONTRACT_PACK_TMP=Join-Path $logs 'exact-source-contracts.pck'
$proc=$null;$reason='unknown';$forced=$false;$started=[DateTime]::UtcNow
try {
 $arguments=@('--headless','--path',('"'+$project+'"'),'--log-file',('"'+(Join-Path $logs 'engine.log')+'"'),'--export-release','"Integrated Construction Package"',('"'+(Join-Path $output 'Astraea.exe')+'"'))
 $proc=Start-Process $engine -ArgumentList $arguments -WorkingDirectory $project -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logs 'stdout.log') -RedirectStandardError (Join-Path $logs 'stderr.log')
 $proc.Id|Set-Content (Join-Path $logs 'pid.txt')
 Write-Output ('Export PID '+$proc.Id+' output '+$output)
 while(-not $proc.HasExited){
  $proc.Refresh();$free=(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB;$disk=(Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace/1GB
  $row=[pscustomobject]@{utc=[DateTime]::UtcNow.ToString('o');elapsed=([DateTime]::UtcNow-$started).TotalSeconds;private_GiB=$proc.PrivateMemorySize64/1GB;free_RAM_GiB=$free;free_disk_GiB=$disk}
  $row|Export-Csv (Join-Path $logs 'samples.csv') -Append -NoTypeInformation
  $row|ConvertTo-Json -Compress|Write-Output
  if($free -lt 5 -or $proc.PrivateMemorySize64 -gt 16GB -or $disk -lt 20){$reason='resource_safety_stop';break}
  if($row.elapsed -gt 1800){$reason='export_deadline';break}
  Start-Sleep -Seconds 10
 }
 if($proc.HasExited){$reason='process_exited'}
} finally {
 $env:ASTRAEA_CONTRACT_PACK_TMP=$oldScratch
 if($proc -and -not $proc.HasExited){[void]$proc.CloseMainWindow();if(-not $proc.WaitForExit(3000)){$forced=$true;$proc.Kill();$proc.WaitForExit()}}
 [ordered]@{revision=$ExpectedRevision;output=$output;reason=$reason;forced=$forced;exit_code=if($proc){$proc.ExitCode}else{$null};started=$started;ended=[DateTime]::UtcNow}|ConvertTo-Json|Set-Content (Join-Path $logs 'summary.json')
 Get-Content (Join-Path $logs 'summary.json')
}
