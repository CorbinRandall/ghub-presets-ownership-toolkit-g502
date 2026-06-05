# G Hub Preset Toolkit — START HERE

Full control of your Logitech mouse profiles: **export**, **backup on the mouse**, and **import** into G Hub — without Logitech cloud sync.

> **Not affiliated with Logitech.** This tool edits your local G Hub database.  
> Read [DISCLAIMER.md](DISCLAIMER.md) and [SECURITY.md](SECURITY.md) before Import or Replace.

## Get the toolkit

```bash
git clone https://github.com/CorbinRandall/ghub-presets.git
cd ghub-presets
```

Or download ZIP from [github.com/CorbinRandall/ghub-presets](https://github.com/CorbinRandall/ghub-presets).

## What you need

1. **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)  
   - Windows: check **“Add python.exe to PATH”** during install  
2. **Logitech G Hub** installed  
3. This repo folder on your computer  

**Your presets are not in git** — after clone, run Export or copy your local `Presets/` folder in.

## First time setup

| Mac | Windows |
|-----|---------|
| Double-click `Executables/mac/0 Setup (run once).command` | Double-click `Executables/windows/0 Setup (run once).bat` |

If Mac says the file is from an unidentified developer: **right-click → Open → Open**.

## The three things you’ll do

**Always quit G Hub first** (menu bar → Quit Logitech G Hub).

| Step | Mac (double-click) | Windows (double-click) | What it does |
|------|-------------------|------------------------|--------------|
| **1. Export** | `1 Export from G Hub.command` | `1 Export from G Hub.bat` | Copies all G Hub profiles → **`Presets/`** folder |
| **2. Pull** | `2 Pull from Mouse.command` | `2 Pull from Mouse.bat` | Reads profiles stored **on the mouse** → `Presets/` + `Presets/onboard/` |
| **3. Import** | `3 Import to G Hub.command` | `3 Import to G Hub.bat` | Adds/updates profiles from **`Presets/`** (keeps extra G Hub profiles) |
| **4. Replace** | `4 Replace G Hub with Presets.command` | `4 Replace G Hub with Presets.bat` | **Wipes bloat** — G Hub will match **`Presets/`** only (removes other desktop profiles + old macros) |

Then **open G Hub** again.

**Use #4 when** G Hub has duplicates or profiles you deleted from `Presets/` but they still show in the app. The script **automatically tries to quit G Hub**, including the **menu bar background agent** (not just the main window). Review the preview, then press **Enter** to apply.

**Important:** Closing the G Hub window is not enough. Use the **menu bar icon → Quit Logitech G HUB**, or let script #4 run `quit-ghub` for you. If old profiles reappear after opening G Hub, the agent was still running and overwrote the database — run #4 again with G Hub fully quit.

**Presets folder path:** `ghub-presets/Presets/` (next to `Executables/`). That is the only folder Replace uses.

## Where are my files?

```
ghub-presets/
  Presets/              ← YOUR PROFILES (edit like normal files)
  Executables/
    mac/                ← .command files (Mac)
    windows/            ← .bat files (Windows)
```

Each `Something.lghub-preset.json` in **`Presets/`** = one of your profiles in G Hub.

**Ignore `Presets/_system/`** — that holds `DONT_TOUCH_SYSTEM` (Logitech’s required factory default). The toolkit keeps it automatically; you don’t edit or delete it.

## File types (noob cheat sheet)

| OS | Double-click extension | What it is |
|----|------------------------|------------|
| **Mac** | `.command` | Mini app that runs in Terminal |
| **Windows** | `.bat` | Script that runs in Command Prompt |

You do **not** need to type commands if you use the files in `Executables/`.

## New computer

1. Copy this whole repo (or at least the **`Presets/`** folder).  
2. Install Python + G Hub.  
3. Run **Setup** once.  
4. Run **Import to G Hub**.  

## Advanced (optional terminal)

```bash
cd path/to/ghub-presets
pip install -e .
python3 -m ghub_presets export --all
python3 -m ghub_presets import Presets/ --replace
python3 -m ghub_presets pull --slot 1 --device g502
```

## Mouse note

Pull is tuned for **G502** (`--device g502`). Other mice need different device flags — see main `README.md`.

## Safety (short version)

- **Your data stays on your machine** — no cloud upload.
- **Quit G Hub fully** before Export / Import / Replace (menu bar agent counts as running).
- **Automatic DB backup** before writes — see [SECURITY.md](SECURITY.md) for restore steps.
- **Not official Logitech software** — no Logitech logos; don’t claim endorsement when sharing.
