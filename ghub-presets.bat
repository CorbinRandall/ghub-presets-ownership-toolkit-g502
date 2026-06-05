@echo off
setlocal
set "ROOT=%~dp0"
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "GHUB_PRESET_TOOLKIT_ROOT=%ROOT%"
set "GHUB_PRESETS_DIR=%ROOT%\Presets"
set "PYTHONPATH=%ROOT%;%PYTHONPATH%"
python -m ghub_presets --folder "%ROOT%\Presets" %*
