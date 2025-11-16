import os

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

from src.ui.settings_window import SettingsWindow
from src.util.path_util import get_packaged_path
from src.util.web_browser_util import open_about, open_buy_me_a_coffee, open_help


class TrayIcon:
    def __init__(self, main):
        self.main = main

    def set_opacity(self, opacity: float) -> None:
        self.main.config.opacity = opacity
        self.main.config.save()

    def toggle_notifications(self) -> None:
        self.main.config.notifications_enabled = not self.main.config.notifications_enabled
        self.main.config.save()

    def is_opacity_checked(self, opacity: float) -> bool:
        return self.main.config.opacity == opacity

    def open(self) -> None:
        path = os.path.join("resources", "img", "icon.png")
        image = Image.open(get_packaged_path(path))
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill="white")
        menu = Menu(
            MenuItem("Lock Keyboard", self.main.send_hotkey_signal),
            MenuItem(
                "Enable/Disable Notifications",
                self.toggle_notifications,
                checked=lambda item: self.main.config.notifications_enabled,
            ),
            MenuItem("Settings...", lambda: SettingsWindow(self.main).open()),
            MenuItem("About", Menu(
                MenuItem("Help", open_help),
                MenuItem("About", open_about),
                MenuItem("Support ☕", open_buy_me_a_coffee),
            )),
            MenuItem("Quit", self.main.quit_program),
        )
        tray_icon = Icon("CatLock", image, "CatLock", menu)
        tray_icon.run()
