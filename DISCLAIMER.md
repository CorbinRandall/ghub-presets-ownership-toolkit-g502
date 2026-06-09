# Disclaimer

## Not affiliated with Logitech

**G Hub Preset Toolkit** is an independent, open-source community project. It is **not** made, endorsed, sponsored, or approved by **Logitech** or **Logitech G HUB**.

- Do not represent this project as official Logitech software or support.
- Do not use Logitech logos, G HUB branding, or marketing assets in forks or posts implying endorsement.
- “Logitech”, “G HUB”, and related names are trademarks of their respective owners. This project uses them only to describe compatibility.

## Your data, your machine

This tool reads and writes files **on your computer**:

- Logitech G Hub’s local `settings.db` database
- Optional HID++ communication with **your** USB mouse hardware
- JSON preset files in the `Presets/` folder you control

It does **not** connect to Logitech cloud accounts, Logitech servers, or online sync services. Your presets stay local unless **you** copy them elsewhere.

## No warranty

The software is provided under the [MIT License](LICENSE) **“AS IS”**, without warranty of any kind. See [LICENSE](LICENSE) for the full text.

The authors are not responsible for:

- Lost, corrupted, or overwritten G Hub profiles or macros
- Mice that stop working as expected after import
- Game bans or anti-cheat flags (this tool is not designed for cheating; use macros responsibly in online games)
- Violations of Logitech’s terms of service in your jurisdiction

## Use at your own risk

Before **Import** or **Replace**:

1. **Quit Logitech G HUB completely** (including the menu bar / system tray background agent).
2. **Back up** `settings.db` — the toolkit creates timestamped backups on write; keep your own copy too.
3. **Export** your current profiles to `Presets/` so you can roll back.

If something goes wrong, restore from `settings.db.backup-*` next to your G Hub data folder (see [SECURITY.md](SECURITY.md)).

## Software updates

Logitech may change G Hub, `settings.db` format, or HID behavior at any time. This project may stop working after a G Hub update without notice. That is a normal maintenance risk, not something this project can guarantee against.

On Windows, you can optionally run **`0c Block G Hub Updates.bat`** (or `ghub-presets block-updates`) to block updater network traffic and related update checks while keeping `LGHUBUpdaterService` running (G Hub needs it to start). See [SECURITY.md](SECURITY.md). Undo with **`0d Unblock G Hub Updates.bat`** when you want updates again.

## Questions or takedown

This project is intended as a legitimate local backup and portability tool for end users who own Logitech hardware. If you are a rights holder with concerns, open an issue on the repository or contact the maintainer via GitHub.
