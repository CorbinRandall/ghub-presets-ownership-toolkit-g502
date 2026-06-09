G Hub Preset Toolkit — Mac

FILE TYPES (double-click these):
  .command  = Mac shortcut (opens Terminal, runs the tool)

FIRST TIME:
  1. Double-click:  0 Setup (run once).command
  2. If macOS blocks it: right-click → Open → Open
  3. (Optional, for update block) 0 Setup admin sudo (once).command
     → enter password once; Block/Unblock updates won't ask again

OPTIONAL (pin G Hub version so this toolkit keeps working):
  0c Block G Hub Updates.command   → blocks update hosts in /etc/hosts
  0d Unblock G Hub Updates.command   → undo 0c
  Also turn off "Enable automatic updates" in G Hub Settings.

EVERY TIME (quit G Hub first!):
  1 Export from G Hub.command   → saves profiles into the Presets/ folder
  2 Pull from Mouse.command     → reads onboard mouse profiles (auto: dongle/USB/wired)
  3 Import to G Hub.command     → adds/updates profiles from Presets/ (keeps extras in G Hub)
  4 Replace G Hub with Presets  → G Hub = Presets folder only (removes bloat, type YES)

Your preset files live in:
  (this repo)/Presets/

You can delete, duplicate, or rename .lghub-preset.json files there like normal files.
