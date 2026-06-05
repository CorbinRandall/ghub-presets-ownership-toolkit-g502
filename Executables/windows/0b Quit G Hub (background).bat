@echo off
cd /d "%~dp0\..\.."
set "GHUB_PRESET_TOOLKIT_ROOT=%CD%"
set "PYTHONPATH=%CD%;%PYTHONPATH%"
echo.
python -m ghub_presets quit-ghub
echo.
pause
