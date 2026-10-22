@echo off
setlocal
if "%~1"=="" exit /b 2
if not exist "%~1" exit /b 2
if /I not "%~2"=="editor" if /I not "%~2"=="play" (
 echo Usage: Open-current-source.cmd "path to official Godot 4.6.3 console exe" editor^|play
 exit /b 2
)
"%~1" --version | findstr /B /C:"4.6.3.stable.official.7d41c59c4" >nul
if errorlevel 1 exit /b 3
python "%~dp0..\tools\prepare_retained_working_copy.py" --check-only
if errorlevel 1 (
 echo Retained source verification failed. See README before opening.
 exit /b 4
)
if /I "%~2"=="editor" (
 "%~1" --editor --path "%~dp0.."
) else (
 "%~1" --path "%~dp0.." --rendering-method gl_compatibility
)
exit /b %errorlevel%
