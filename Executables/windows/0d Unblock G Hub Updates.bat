@echo off
setlocal
cd /d "%~dp0\..\..\scripts"

net session >nul 2>&1
if %errorlevel% neq 0 (
  echo Requesting administrator privileges...
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b 0
)

call toolkit.bat unblock-updates
exit /b %errorlevel%
