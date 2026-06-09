# G Hub Preset Toolkit

Take full control of your Logitech G Hub mouse profiles — **export**, **pull from onboard memory**, and **import** — without relying on Logitech cloud sync.

> **Independent project — not affiliated with Logitech or Logitech G HUB.**  
> Modifies your local `settings.db` while G Hub is quit. [Use at your own risk](DISCLAIMER.md).  
> Read [SECURITY.md](SECURITY.md) before Import or Replace.

**→ New here? Read [START_HERE.md](START_HERE.md)**

## What you get

| Feature | Description |
|---------|-------------|
| **Export** | Backup all G Hub profiles to portable `.lghub-preset.json` files |
| **Pull** | Read profiles stored on the mouse (HID++ onboard memory) |
| **Import** | Restore presets into G Hub’s database |
| **Replace** | Make G Hub match your `Presets/` folder only (removes bloat) |
| **Block updates** *(optional)* | Pin G Hub version — block auto-updates so this toolkit keeps working |

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

## Optional: block G Hub auto-updates

Logitech can ship G Hub updates that change `settings.db` or break this toolkit. You can **optionally** block background auto-updates and pin your current G Hub version.

| Platform | Block | Undo |
|----------|-------|------|
| **Windows** | `Executables/windows/0c Block G Hub Updates.bat` | `0d Unblock G Hub Updates.bat` |
| **macOS** | `Executables/mac/0c Block G Hub Updates.command` | `0d Unblock G Hub Updates.command` |

**macOS first time (optional):** run `Executables/mac/0 Setup admin sudo (once).command` once so Block/Unblock won't keep asking for your password.

**What it does**

- **Windows:** outbound firewall rules on updater binaries, `hosts` entries for Logitech update servers, registry flags. Keeps `LGHUBUpdaterService` **running** (disabling it causes G Hub to boot-loop).
- **macOS:** `127.0.0.1` entries in `/etc/hosts` for Logitech update/pipeline hosts. Keeps `com.logi.ghub.updater` **loaded** (unloading it can prevent G Hub from starting).

**Also do this in G Hub:** Settings → turn off **Enable automatic updates**.

**Undo anytime** with the `0d` script or:

```bash
ghub-presets unblock-updates
```

Details and recovery: [SECURITY.md](SECURITY.md). Not affiliated with Logitech — use at your own risk.

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
ghub-presets block-updates      # optional; admin/sudo required
ghub-presets unblock-updates    # undo block
```

## G Hub database paths

| OS | `settings.db` |
|----|----------------|
| macOS | `~/Library/Application Support/lghub/settings.db` |
| Windows | `%LOCALAPPDATA%\LGHUB\settings.db` |

## Supported devices (v1)

See **[ghub_presets/ROSETTA.md](ghub_presets/ROSETTA.md)** for G502 slot names, built-in preset ID rules (including why g1/g2/g3 clicks share suffixes with F1–F3), and OMM onboard mapping.

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

## Legal & safety

| Document | Purpose |
|----------|---------|
| [DISCLAIMER.md](DISCLAIMER.md) | Not affiliated with Logitech, no warranty, your responsibility |
| [SECURITY.md](SECURITY.md) | What files are touched, backups, recovery steps |
| [NOTICE.md](NOTICE.md) | Third-party code and trademarks |
| [LICENSE](LICENSE) | MIT license |

## License

MIT — see [LICENSE](LICENSE).
