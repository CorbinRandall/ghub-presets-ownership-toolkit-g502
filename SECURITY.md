# Security & data handling

## What this tool modifies

| Target | When | What happens |
|--------|------|----------------|
| **`settings.db`** | Import, Replace, Export (read) | SQLite database used by Logitech G HUB on your PC/Mac |
| **`settings.db.backup-*`** | Before Import / Replace writes | Automatic timestamped copy of the database file |
| **`Presets/*.lghub-preset.json`** | Export, Pull | JSON files you own; safe to copy, delete, or encrypt |
| **Mouse onboard memory** | Pull only | Read-only via HID++; writes only if you later save profiles in G Hub to the device |

This tool does **not**:

- Run while G Hub is open (by design — avoids races with G Hub’s own writes)
- Upload data to the internet
- Store credentials or Logitech account tokens
- Modify mouse firmware

## Optional: block G Hub updates (Windows)

If you run `block-updates` (or `0c Block G Hub Updates.bat`), the toolkit may modify:

| Target | What happens |
|--------|----------------|
| **Windows Firewall** | Outbound block rules for `lghub_updater.exe` and `lghub_software_manager.exe` |
| **`C:\Windows\System32\drivers\etc\hosts`** | `127.0.0.1` entries for Logitech update/pipeline hosts (marked with a toolkit comment) |
| **`LGHUBUpdaterService`** | Kept **automatic and running** — G Hub boot-loops if this service is disabled |
| **`HKLM` / `HKCU` `Software\Logitech\GHUB`** | DWORDs such as `AutoUpdateCheckEnabled=0` (created if missing) |
| **`Presets/_archive/ghub-update-block.json`** | Saved prior service startup type and registry values for undo |

Undo with `unblock-updates` or `0d Unblock G Hub Updates.bat` (admin required). Also turn off **Enable automatic updates** in G Hub’s own Settings for belt-and-suspenders protection.

G Hub may still prompt for updates if you run a separate installer; this only blocks the built-in updater service and background download path the toolkit observed on Windows.

## G Hub database locations

| OS | Path |
|----|------|
| macOS | `~/Library/Application Support/lghub/settings.db` |
| Windows | `%LOCALAPPDATA%\LGHUB\settings.db` |

Backups created by this tool:

```
settings.db.backup-YYYYMMDD-HHMMSS
```

(same folder as `settings.db`)

## Safe usage checklist

1. **Quit G Hub** — menu bar → Quit Logitech G HUB, or run `ghub-presets quit-ghub`.
2. **Export first** — keep a copy of profiles in `Presets/` before Replace.
3. **Verify** — run `ghub-presets status` and confirm `G Hub blocking: False`.
4. **Replace** — review the dry-run list; only desktop mouse profiles not in `Presets/` are removed.
5. **Reopen G Hub** — confirm profiles look correct.

## If G Hub looks wrong after import

1. Quit G Hub again.
2. Find the newest `settings.db.backup-*` beside `settings.db`.
3. Copy the backup over `settings.db` (and delete `settings.db-wal` / `settings.db-shm` if present).
4. Open G Hub.

On macOS, Time Machine or Finder backup of `~/Library/Application Support/lghub/` is also a good idea.

## Reporting security issues

If you find a vulnerability (e.g. unsafe path handling, command injection in scripts), please **open a private security advisory** on GitHub or file an issue with minimal reproduction steps. Do not post exploit details publicly before a fix.

This project is a local admin tool: it assumes you trust the preset files you import and the machine you run it on.

## Privacy

- Preset JSON may contain macro keystrokes and profile names you created — treat `Presets/` as **personal data**.
- The public git repository **gitignores** `Presets/*.lghub-preset.json` so your profiles are not published with the toolkit by default.
- Do not commit or share preset files if they contain sensitive macro sequences or account-related shortcuts.
