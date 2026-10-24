@echo off
py -3 "%~dp0LAUNCH_ASTRAEA.py" %*
if errorlevel 1 pause
