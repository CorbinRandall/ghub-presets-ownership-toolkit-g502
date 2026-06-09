@echo off
setlocal
cd /d "%~dp0\..\..\scripts"

:: Request administrator elevation (required for service + firewall changes).
net session >nul 2>&1
if %errorlevel% neq 0 (
  echo Requesting administrator privileges...
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b 0
)

call toolkit.bat block-updates
exit /b %errorlevel%
