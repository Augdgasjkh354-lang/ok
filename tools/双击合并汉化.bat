@echo off
rem Merge Ashfall Chinese localization into an existing module (no Python needed).
rem Usage: double-click, or drag the Modules\TestMod folder onto this file.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0merge_localization.ps1" %*
echo.
pause
