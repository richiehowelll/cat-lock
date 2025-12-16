# CatLock

CatLock is a simple utility designed to prevent accidental keyboard input, particularly when your feline friend decides to grace your workspace.
Currently only supported on **Windows**

## Features
- Lock your keyboard with a hotkey (Ctrl + L).
- See a semi-transparent overlay indicating the keyboard is locked, allowing uninterrupted viewing.
- Unlock the keyboard by clicking on the overlay.
- Access configuration options via a convenient system tray menu:
    - Adjust overlay opacity to suit your preferences.
    - Enable or disable system notifications when the keyboard is locked.
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

<a href="https://www.buymeacoffee.com/richiehowelll" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

Your contributions will help maintain and improve this project. Thank you!

## Tested by:

<img src="https://i.imgur.com/AuEkoPy.jpeg" width="50%" height="50%"/>
