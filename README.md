# CatLock

CatLock is a program that helps you lock your keyboard with a hotkey, preventing accidental typing, especially when your cat jumps onto your keyboard.

## Features
- Lock the keyboard using a customizable hotkey (`Ctrl + Shift + L` by default).
- Display an overlay indicating the keyboard is locked.
- Click the overlay to unlock the keyboard.
- System tray menu with config options:
  - Customize overlay opacity
  - Enable/Disable system notifications when keyboard is locked
  - Set custom lock hotkey
## Caveats
- Relies on https://github.com/boppreh/keyboard/ which only has full support for Windows
- OS bound hotkeys take precedence such as `ctrl+alt+del` (this way you don't get locked out if something goes wrong)
