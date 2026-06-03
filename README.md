# G Hub Personal Preset Control

Cross-platform CLI to **export**, **import**, and **pull** Logitech G Hub mouse profiles outside Logitech’s sync system.

Keep presets in `~/LogitechPresets/` (or any folder), copy them to any Mac/Windows machine, and inject them into G Hub’s database so they appear natively when you open the app.

## Requirements

- Python 3.10+
- Logitech G Hub installed (creates `settings.db` on first run)
- For **pull** (mouse read): `hidapi` — included in `requirements.txt`

## Install

```bash
cd ~/Projects/ghub-presets
pip install -e .
```

Optional mouse support:

```bash
pip install hidapi
```

## Important

**Quit Logitech G Hub completely** before `export`, `import`, or `pull`. If G Hub is running, it may overwrite changes or block HID access to the mouse.

```bash
ghub-presets status   # check paths and whether G Hub is running
```

## G Hub database locations

| OS | Path |
|----|------|
| macOS | `~/Library/Application Support/lghub/settings.db` |
| Windows | `%LOCALAPPDATA%\LGHUB\settings.db` |

Override with `--db-path` or preset folder with `--folder` / `GHUB_PRESETS_DIR`.

---

## Daily workflows

### Export all profiles (backup)

```bash
ghub-presets export --all
```

Writes `*.lghub-preset.json` files to `~/LogitechPresets/` and updates `manifest.json`.

### Export one profile

```bash
ghub-presets export --name "Mac F1"
```

### Restore after G Hub loses settings

```bash
# Quit G Hub first
ghub-presets import ~/LogitechPresets/ --replace
# Open G Hub
```

### New Mac or Windows PC

1. Install G Hub, connect mouse once (creates empty `settings.db`)
2. Copy your `LogitechPresets` folder to the machine
3. Quit G Hub
4. `ghub-presets import ~/LogitechPresets/`
5. Open G Hub

### List profiles

```bash
ghub-presets list                  # from G Hub database
ghub-presets list --source folder  # from preset folder
```

### Import options

```bash
ghub-presets import ~/LogitechPresets/Mac_F1.lghub-preset.json
ghub-presets import ~/LogitechPresets/ --replace
ghub-presets import ~/LogitechPresets/Mac_F1.lghub-preset.json --rename "Mac F1 backup"
ghub-presets import ~/LogitechPresets/ --dry-run
ghub-presets import ~/LogitechPresets/ --target-device g502wireless
```

---

## Pull from mouse onboard memory

Reads the active configuration stored **on the mouse hardware** (not G Hub software profiles).

```bash
# G502 Hero / Spectrum wired
ghub-presets pull --slot 1 --device g502

# G502 Lightspeed (USB cable)
ghub-presets pull --slot 1 --device g502wireless

# G502 Lightspeed (wireless dongle)
ghub-presets pull --slot 1 --device g502wireless-dongle --output ~/LogitechPresets/onboard1.json
```

Then import into G Hub:

```bash
ghub-presets import ~/LogitechPresets/onboard_slot1.lghub-preset.json
```

### Mouse pull limitations

- G Hub must be **quit** (exclusive HID access)
- Only settings saved to **onboard memory** are readable
- Complex multi-step macros may import incompletely
- G-Shift layer mappings are best-effort
- Software-only profiles (never saved to device) cannot be pulled from hardware
- Up to 5 onboard slots per mouse

### Windows HID notes

- Wired USB connection is most reliable
- If the device is not found, ensure no other Logitech software is running
- Some systems need [hidapi](https://github.com/libusb/hidapi) with appropriate USB drivers

### macOS HID notes

- Enable the **Logitech G HUB HID Driver Extension** in System Settings → Login Items & Extensions → Driver Extensions
- Grant Terminal (or your terminal app) **Input Monitoring** if HID open fails
- Pull uses non-exclusive HID access so it can work while Logitech’s driver is active (no need to uninstall G Hub drivers)
- Use wired connection or receiver; Bluetooth may not expose HID++ onboard feature

---

## Preset file format

Files use extension `.lghub-preset.json` with `"format": "lghub-preset-v1"`. They contain:

- G Hub `profile` object (button assignments, DPI references)
- Associated `cards` (macros, mouse settings, lighting)
- Optional `ommRaw` when pulled from mouse
- Human-readable `readable` summary

---

## Supported devices (v1)

| CLI `--device` | Mouse | G Hub slot prefix |
|----------------|-------|-------------------|
| `g502` | G502 Proteus Spectrum / Gaming Mouse G502 (PID 0xC332) | `g502spectrum_` |
| `g502-hero` | G502 Hero wired (PID 0xC08B) | `g502spectrum_` |
| `g502wireless` | G502 Lightspeed (USB) | `g502wireless_` |
| `g502wireless-dongle` | G502 Lightspeed (receiver) | `g502wireless_` |

Import remaps slot prefixes when `--target-device` differs from the export source.

---

## What this cannot do

- Modify G Hub while it is running
- Add menu items inside G Hub (no plugin API)
- Guarantee 100% mouse→G Hub conversion for complex macros
- Import presets into non-G502 mice without additional device maps

---

## License

Tool code: MIT. Vendored `omm/` HID++ code adapted from [lexr1/omm.py](https://github.com/lexr1/omm.py).
