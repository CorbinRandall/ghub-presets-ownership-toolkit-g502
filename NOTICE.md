# Third-party notices

## HID++ / onboard profile code

Mouse **pull** functionality includes code adapted from the open-source project [omm.py](https://github.com/lexr1/omm.py) (lexr1), vendored under `ghub_presets/omm/`.

HID++ is a protocol used to communicate with Logitech devices. This project uses it only to **read** onboard profile data from hardware you own. It is not an official Logitech SDK.

## Python dependencies

- **[hidapi](https://github.com/libusb/hidapi)** — USB HID access for onboard profile pull

Install via `pip install -e .` or the Setup scripts in `Executables/`.

## Logitech trademarks

Logitech, G, G HUB, and related marks are trademarks of Logitech Europe S.A. and/or Logitech, Inc. This project is not affiliated with Logitech.
