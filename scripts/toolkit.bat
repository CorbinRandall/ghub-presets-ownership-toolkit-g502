@echo off
setlocal EnableDelayedExpansion

if "%~1"=="" (
  echo Usage: toolkit.bat action
  exit /b 1
)

set "ACTION=%~1"
set "TOOLKIT=%~dp0.."
for %%I in ("%TOOLKIT%") do set "TOOLKIT=%%~fI"
set "PRESETS=%TOOLKIT%\Presets"

set "GHUB_PRESET_TOOLKIT_ROOT=%TOOLKIT%"
set "GHUB_PRESETS_DIR=%PRESETS%"
set "PYTHONPATH=%TOOLKIT%;%PYTHONPATH%"

set "PY=python"
where python >nul 2>&1 && python -c "import sys; raise SystemExit(0 if sys.version_info[:2]>=(3,10) else 1)" >nul 2>&1 || set "PY="
if not defined PY (
  where py >nul 2>&1 && py -3 -c "import sys; raise SystemExit(0 if sys.version_info[:2]>=(3,10) else 1)" >nul 2>&1 && set "PY=py -3"
)
if not defined PY (
  echo ERROR: Python 3.10+ not found.
  echo Install from https://www.python.org/downloads/ and check "Add python.exe to PATH"
  echo Or run: winget install Python.Python.3.12
  pause
  exit /b 1
)

echo.
echo ==============================================
echo   G Hub Preset Toolkit
echo   Presets folder: %PRESETS%
echo ==============================================
echo.
echo IMPORTANT: Quit Logitech G Hub completely first!
echo.
echo Not affiliated with Logitech. Modifies settings.db - see DISCLAIMER.md
echo.

if /i "%ACTION%"=="setup" goto :setup
if /i "%ACTION%"=="export" goto :export
if /i "%ACTION%"=="pull" goto :pull
if /i "%ACTION%"=="import" goto :import
if /i "%ACTION%"=="replace" goto :replace
echo Unknown action: %ACTION%
pause
exit /b 1

:setup
echo Installing Python dependencies...
%PY% -m pip install -e "%TOOLKIT%"
if not exist "%PRESETS%\onboard" mkdir "%PRESETS%\onboard"
echo.
echo Setup done. Use the .bat files in Executables\windows\
goto :done

:export
if not exist "%PRESETS%" mkdir "%PRESETS%"
%PY% -m ghub_presets --folder "%PRESETS%" export --all
echo.
echo Saved to: %PRESETS%
explorer "%PRESETS%"
goto :done

:pull
if not exist "%PRESETS%\onboard" mkdir "%PRESETS%\onboard"
echo Reading onboard slots 1-3 from mouse (G502)...
for %%s in (1 2 3) do (
  %PY% -m ghub_presets --folder "%PRESETS%" pull --slot %%s --device g502 --raw 2>nul || echo   slot %%s raw skipped
  %PY% -m ghub_presets --folder "%PRESETS%" pull --slot %%s --device g502 2>nul || echo   slot %%s skipped
)
echo.
echo Raw backup: %PRESETS%\onboard\
explorer "%PRESETS%"
goto :done

:import
dir /b "%PRESETS%\*.lghub-preset.json" >nul 2>&1
if errorlevel 1 (
  echo No preset files in %PRESETS%
  echo Run Export from G Hub first, or copy .lghub-preset.json files into Presets\
  goto :done
)
%PY% -m ghub_presets --folder "%PRESETS%" import "%PRESETS%" --replace
if errorlevel 1 (
  echo.
  echo Import failed. Quit Logitech G Hub completely, then run again.
  goto :done
)
echo.
echo Done. Open Logitech G Hub to see your profiles.
goto :done

:replace
echo Stopping G Hub (including background agents)...
%PY% -m ghub_presets quit-ghub
if errorlevel 1 (
  echo.
  echo Could not stop G Hub. Quit from system tray, then run again.
  goto :done
)
echo.
dir /b "%PRESETS%\*.lghub-preset.json" >nul 2>&1
if errorlevel 1 (
  echo No preset files in %PRESETS%
  goto :done
)
echo Presets folder (this is the only folder used):
echo   %PRESETS%
echo.
echo This makes G Hub match ONLY the .lghub-preset.json files in that folder.
echo.
%PY% -m ghub_presets --folder "%PRESETS%" replace "%PRESETS%" --dry-run
echo.
pause
%PY% -m ghub_presets --folder "%PRESETS%" replace "%PRESETS%"
if errorlevel 1 goto :done
echo.
echo Success. Profiles now in G Hub:
%PY% -m ghub_presets list
echo.
echo You can open Logitech G Hub now.
goto :done

:done
echo.
pause
