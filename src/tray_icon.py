import webbrowser

from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw


def open_about():
    webbrowser.open("https://github.com/richiehowelll/CatLock", new=2)


class TrayIcon:
    def __init__(self, main):
        self.main = main
        self.create_tray_icon()

    def set_opacity(self, opacity):
        self.main.config.opacity = opacity
        self.main.config.save()

    def toggle_notifications(self):
        self.main.config.notifications_enabled = not self.main.config.notifications_enabled
        self.main.config.save()

    def create_tray_icon(self):
        image = Image.open("../resources/img/icon.png")
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill="white")
        menu = Menu(
            MenuItem("About", open_about),
            MenuItem("Change Hotkey", self.main.send_change_hotkey_signal),
            MenuItem(
                "Enable/Disable Notifications",
                self.toggle_notifications,
                checked=lambda item: self.main.config.notifications_enabled,
            ),
            MenuItem("Set Opacity", Menu(
                MenuItem("5%", lambda: self.set_opacity(0.05)),
                MenuItem("10%", lambda: self.set_opacity(0.1)),
                MenuItem("30%", lambda: self.set_opacity(0.3)),
                MenuItem("50%", lambda: self.set_opacity(0.5)),
                MenuItem("70%", lambda: self.set_opacity(0.7)),
                MenuItem("90%", lambda: self.set_opacity(0.9)),
            )),
            MenuItem("Quit", self.main.quit_program),
        )
        tray_icon = Icon("Keyboard Locker", image, "Keyboard Locker", menu)
        tray_icon.run()
