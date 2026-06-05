# G Hub Preset Toolkit

Take full control of your Logitech G Hub mouse profiles — **export**, **pull from onboard memory**, and **import** — without relying on Logitech cloud sync.

**Not affiliated with Logitech.** Use at your own risk; always back up `settings.db`.

**→ New here? Read [START_HERE.md](START_HERE.md)**

## What you get

| Feature | Description |
|---------|-------------|
| **Export** | Backup all G Hub profiles to portable `.lghub-preset.json` files |
| **Pull** | Read profiles stored on the mouse (HID++ onboard memory) |
| **Import** | Restore presets into G Hub’s database |
| **Replace** | Make G Hub match your `Presets/` folder only (removes bloat) |

Works on **macOS** and **Windows**. Noob-friendly double-click scripts included.

```
ghub-presets/
├── START_HERE.md
├── Presets/              ← your profiles (gitignored — yours stay local)
├── Executables/
│   ├── mac/              ← .command files
│   └── windows/          ← .bat files
└── ghub_presets/         ← Python CLI
```

## Quick start

1. Clone or download this repo  
2. **Setup** (once): `Executables/mac/0 Setup` or `Executables/windows/0 Setup`  
3. **Quit G Hub** (menu bar → Quit — not just close the window)  
4. Use **Export**, **Pull**, **Import**, or **Replace** from `Executables/`  
5. Open G Hub  

Your personal presets never leave your machine unless you copy the `Presets/` folder yourself.

## Requirements

- Python 3.10+
- [Logitech G Hub](https://www.logitechg.com/en-us/innovation/g-hub.html)
- G502 (wired) tested; other mice need `--device` flags (see below)
- Mouse pull: USB connection, G Hub quit, `hidapi` (installed by Setup)

## CLI (optional)

```bash
pip install -e .
ghub-presets status
ghub-presets export --all
ghub-presets import Presets/ --replace
ghub-presets replace Presets/
ghub-presets pull --slot 1 --device g502
ghub-presets quit-ghub
```

## G Hub database paths

| OS | `settings.db` |
|----|----------------|
| macOS | `~/Library/Application Support/lghub/settings.db` |
| Windows | `%LOCALAPPDATA%\LGHUB\settings.db` |

## Supported devices (v1)

| `--device` | Mouse |
|------------|-------|
| `g502` | G502 Proteus Spectrum (PID 0xC332) |
| `g502wireless` | G502 Lightspeed (USB) |
| `g502wireless-dongle` | G502 Lightspeed (receiver) |

## Limitations

- Quit G Hub completely before export/import/replace (background menu-bar agent counts as running)
- Complex macros and G-Shift layers: best-effort conversion
- Scroll-wheel tilt assignments may be software-only
- Cannot modify G Hub while it is open

## License

MIT — see [LICENSE](LICENSE). Vendored HID++ code adapted from [lexr1/omm.py](https://github.com/lexr1/omm.py).
