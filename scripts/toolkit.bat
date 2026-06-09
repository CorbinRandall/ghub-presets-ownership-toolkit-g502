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
echo Not affiliated with Logitech. Modifies settings.db - see DISCLAIMER.md
echo.

if /i "%ACTION%"=="setup" goto :setup
if /i "%ACTION%"=="export" goto :export
if /i "%ACTION%"=="pull" goto :pull
if /i "%ACTION%"=="import" goto :import
if /i "%ACTION%"=="replace" goto :replace
if /i "%ACTION%"=="quit-ghub" goto :quit_ghub
if /i "%ACTION%"=="block-updates" goto :block_updates
if /i "%ACTION%"=="unblock-updates" goto :unblock_updates
if /i "%ACTION%"=="backup" goto :backup
echo Unknown action: %ACTION%
pause
exit /b 1

:setup
echo Installing Python dependencies...
%PY% -m pip install -e "%TOOLKIT%"
if errorlevel 1 (
  echo.
  echo Setup failed. Check Python and internet connection.
  goto :done_fail
)
if not exist "%PRESETS%\onboard" mkdir "%PRESETS%\onboard"
if not exist "%PRESETS%\_archive" mkdir "%PRESETS%\_archive"
echo.
echo Setup done. Use the .bat files in Executables\windows\
goto :done

:backup
%PY% -m ghub_presets --folder "%PRESETS%" backup
if errorlevel 1 goto :done_fail
goto :done

:quit_ghub
echo Stopping G Hub (including background agents)...
%PY% -m ghub_presets quit-ghub
if errorlevel 1 goto :done_fail
echo G Hub is fully stopped.
goto :done

:block_updates
echo Blocking G Hub automatic updates (admin required)...
echo This disables LGHUBUpdaterService and adds outbound firewall rules.
echo.
%PY% -m ghub_presets --folder "%PRESETS%" block-updates
if errorlevel 1 goto :done_fail
goto :done

:unblock_updates
echo Removing G Hub update block (admin required)...
%PY% -m ghub_presets --folder "%PRESETS%" unblock-updates
if errorlevel 1 goto :done_fail
goto :done

:export
echo IMPORTANT: G Hub must be quit before export reads settings.db.
echo If export fails, run "0b Quit G Hub (background).bat" first.
echo.
%PY% -m ghub_presets --folder "%PRESETS%" backup
if errorlevel 1 goto :done_fail
if not exist "%PRESETS%" mkdir "%PRESETS%"
%PY% -m ghub_presets --folder "%PRESETS%" export --all
if errorlevel 1 (
  echo.
  echo EXPORT FAILED. Quit Logitech G Hub completely, then run again.
  echo   Double-click: Executables\windows\0b Quit G Hub ^(background^).bat
  goto :done_fail
)
echo.
echo Opening Presets folder...
explorer "%PRESETS%"
goto :done

:pull
echo IMPORTANT: Quit G Hub and connect mouse via USB before pull.
echo.
if not exist "%PRESETS%\onboard" mkdir "%PRESETS%\onboard"
echo Reading onboard slots 1-3 from mouse (G502)...
set "PULL_OK=0"
for %%s in (1 2 3) do (
  %PY% -m ghub_presets --folder "%PRESETS%" pull --slot %%s --device g502 --raw 2>nul && set "PULL_OK=1"
  %PY% -m ghub_presets --folder "%PRESETS%" pull --slot %%s --device g502 2>nul && set "PULL_OK=1"
)
echo.
if "!PULL_OK!"=="0" (
  echo No onboard profiles read. Check USB, quit G Hub, and G502 device.
) else (
  echo Raw backup: %PRESETS%\onboard\
  echo G Hub-ready: %PRESETS%\onboard_slot*.lghub-preset.json
)
explorer "%PRESETS%"
goto :done

:import
echo IMPORTANT: Quit G Hub completely before import.
echo.
dir /b "%PRESETS%\*.lghub-preset.json" >nul 2>&1
if errorlevel 1 (
  echo No preset files in %PRESETS%
  echo Run "1 Export from G Hub.bat" first, or copy .lghub-preset.json files into Presets\
  goto :done_fail
)
%PY% -m ghub_presets --folder "%PRESETS%" backup
if errorlevel 1 goto :done_fail
%PY% -m ghub_presets --folder "%PRESETS%" import "%PRESETS%" --replace
if errorlevel 1 (
  echo.
  echo Import failed. Quit Logitech G Hub completely, then run again.
  goto :done_fail
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
  goto :done_fail
)
echo.
dir /b "%PRESETS%\*.lghub-preset.json" >nul 2>&1
if errorlevel 1 (
  echo No preset files in %PRESETS%
  echo Run "1 Export from G Hub.bat" first to save your current profiles.
  goto :done_fail
)
%PY% -m ghub_presets --folder "%PRESETS%" backup
if errorlevel 1 goto :done_fail
echo Presets folder (this is the only folder used):
echo   %PRESETS%
echo.
echo This makes G Hub match ONLY the .lghub-preset.json files in that folder.
echo.
%PY% -m ghub_presets --folder "%PRESETS%" replace "%PRESETS%" --dry-run
echo.
pause
%PY% -m ghub_presets --folder "%PRESETS%" replace "%PRESETS%"
if errorlevel 1 goto :done_fail
echo.
echo Success. Profiles now in G Hub:
%PY% -m ghub_presets list
echo.
echo You can open Logitech G Hub now.
goto :done

:done_fail
echo.
pause
exit /b 1

:done
echo.
pause
exit /b 0

