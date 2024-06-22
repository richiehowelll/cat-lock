# CatLock

CatLock is a program that helps you lock your keyboard with a hotkey, preventing accidental typing, especially when your cat jumps onto your keyboard.

Currently only supported on **Windows**

## Features
- Lock the keyboard using a customizable hotkey (`Ctrl + L` by default).
- Displays an overlay indicating the keyboard is locked.
  - Overlay is semi-transparent, allowing you to continue watching videos or viewing content even when the keyboard is locked.
- Click the overlay to unlock the keyboard.
- System tray menu with configuration options:
  - Customize overlay opacity
  - Enable/Disable system notifications when keyboard is locked
  - Set custom lock hotkey
## Build an executable
```bash
pip install pyinstaller
```

```bash
pyinstaller --onefile --add-data="./resources/img/icon.ico:./resources/img/" --add-data="./resources/img/icon.png:./resources/img/" --add-data="./resources/config/config.json:./resources/config/" --icon="./resources/img/icon.ico" --hidden-import plyer.platforms.win.notification --noconsole --name="CatLock" "./src/main.py"
```
## Caveats
- Relies on https://github.com/boppreh/keyboard/ which only has full support for Windows
- OS bound hotkeys take precedence such as `ctrl+alt+del` (this way you don't get locked out if something goes wrong)

## Support
If you found this project helpful or want to support my work, consider buying me a coffee!

<a href="https://buymeacoffee.com/richiehowelll" target="_blank"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=yourusername&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff"></a>

Your contributions will help maintain and improve this project. Thank you!

## Tested by:

<img src="https://i.imgur.com/AuEkoPy.jpeg" width="50%" height="50%"/>
