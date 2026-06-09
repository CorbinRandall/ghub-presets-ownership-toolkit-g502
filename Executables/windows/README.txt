G Hub Preset Toolkit — Windows

FILE TYPES (double-click these):
  .bat  = Windows batch file (runs the tool in a command window)

FIRST TIME:
  1. Install Python 3.10+ (python.org — check "Add python.exe to PATH")
     Or: winget install Python.Python.3.12
  2. Double-click:  0 Setup (run once).bat

EVERY TIME:
  0b Quit G Hub (background).bat  → stop G Hub before export/import (required!)
  1 Export from G Hub.bat           → saves profiles into Presets\ (backs up settings.db first)
  2 Pull from Mouse.bat             → reads what's stored on the mouse hardware (USB, G Hub quit)
  3 Import to G Hub.bat             → adds/updates profiles from Presets\ (keeps extras in G Hub)
  4 Replace G Hub with Presets.bat  → G Hub = Presets folder only (preview + confirm)

Your preset files live in:
  (this repo)\Presets\

Database backups (automatic before export/import/replace):
  (this repo)\Presets\_archive\

You can delete, duplicate, or rename .lghub-preset.json files there like normal files.
