@echo off
cd /d "%~dp0\..\..\scripts"
bash publish_to_github.sh 2>nul || (
  echo.
  echo On Windows, run from Git Bash or WSL, or manually:
  echo   gh repo create ghub-presets --public --source=. --push
  echo.
  pause
  exit /b 1
)
