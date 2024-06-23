# CatLock

CatLock is a simple utility designed to prevent accidental keyboard input, particularly when your feline friend decides to grace your workspace.
Currently only supported on **Windows**

## Features
- Lock your keyboard with a customizable hotkey (Ctrl + L by default).
- See a semi-transparent overlay indicating the keyboard is locked, allowing uninterrupted viewing.
- Unlock the keyboard by clicking on the overlay.
- Access configuration options via a convenient system tray menu:
    - Adjust overlay opacity to suit your preferences.
    - Enable or disable system notifications when the keyboard is locked.
    - Set a personalized hotkey combination for locking.
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
