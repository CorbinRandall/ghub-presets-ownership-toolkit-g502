@echo off
setlocal
set "ROOT=%~dp0"
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "GHUB_PRESET_TOOLKIT_ROOT=%ROOT%"
set "GHUB_PRESETS_DIR=%ROOT%\Presets"
set "PYTHONPATH=%ROOT%;%PYTHONPATH%"

set "PY=python"
where python >nul 2>&1 && python -c "import sys; raise SystemExit(0 if sys.version_info[:2]>=(3,10) else 1)" >nul 2>&1 || set "PY="
if not defined PY (
  where py >nul 2>&1 && py -3 -c "import sys; raise SystemExit(0 if sys.version_info[:2]>=(3,10) else 1)" >nul 2>&1 && set "PY=py -3"
)
if not defined PY (
  echo ERROR: Python 3.10+ not found. Run Executables\windows\0 Setup ^(run once^).bat
  exit /b 1
)

%PY% -m ghub_presets --folder "%ROOT%\Presets" %*
