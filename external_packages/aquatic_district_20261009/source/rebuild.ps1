param(
 [string]$Python = 'C:\Users\cered\Documents\Codex\Tools\mcp-stack\Scripts\python.exe',
 [string]$Blender = 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe',
 [string]$Godot = 'C:\Users\cered\Dolphin\AstraeaTools\godot.exe'
)
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
& $Python (Join-Path $PSScriptRoot 'plan_aquatic.py')
if ($LASTEXITCODE -ne 0) { throw 'Plan validation failed' }
& $Blender -b --python (Join-Path $PSScriptRoot 'build_aquatic.py')
if ($LASTEXITCODE -ne 0) { throw 'Source build process failed; inspect Blender diagnostics too' }
& $Python (Join-Path $PSScriptRoot 'validate_delivery.py')
if ($LASTEXITCODE -ne 0) { throw 'Source/export/retention validation failed' }
& $Python (Join-Path $PSScriptRoot 'verify_supports.py')
if ($LASTEXITCODE -ne 0) { throw 'Source foundation/contact check failed' }
& $Blender -b --python (Join-Path $PSScriptRoot 'render_source.py')
if ($LASTEXITCODE -ne 0) { throw 'Source views failed' }
& $Python (Join-Path $PSScriptRoot 'check_import.py') $Godot
if ($LASTEXITCODE -ne 0) { throw 'Isolated import or floor/obstruction checks failed' }
& $Python (Join-Path $PSScriptRoot 'hash_resources.py')
if ($LASTEXITCODE -ne 0) { throw 'Hash manifest failed' }
