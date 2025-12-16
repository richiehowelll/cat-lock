import os

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

from src.ui.settings_window import SettingsWindow
from src.ui.user_guide_window import UserGuideWindow
from src.util.path_util import get_packaged_path
from src.util.web_browser_util import open_about, open_buy_me_a_coffee, open_faq


class TrayIcon:
    def __init__(self, main):
        self.main = main

    def toggle_notifications(self) -> None:
        self.main.config.notifications_enabled = not self.main.config.notifications_enabled
        self.main.config.save()

    def open_settings(self) -> None:
        SettingsWindow(self.main).open()

    def open_user_guide(self) -> None:
        UserGuideWindow(self.main).open()

    def open(self) -> None:
        path = os.path.join("resources", "img", "icon.png")
        image = Image.open(get_packaged_path(path))
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill="white")

        hotkey = getattr(self.main.config, "hotkey", None)
        if hotkey:
            hotkey_display = hotkey.upper()
            lock_label = f"Lock keyboard ({hotkey_display})"
        else:
            lock_label = "Lock keyboard"

        menu = Menu(
            MenuItem(lock_label, self.main.send_hotkey_signal),

            Menu.SEPARATOR,

            MenuItem("Settings…", self.open_settings),
            MenuItem(
                "Show notifications",
                self.toggle_notifications,
                checked=lambda item: self.main.config.notifications_enabled,
            ),

            MenuItem("Support ☕", open_buy_me_a_coffee),

            Menu.SEPARATOR,

            MenuItem("User Guide", self.open_user_guide),
            MenuItem("FAQ", open_faq),
            MenuItem("About CatLock", open_about),

            Menu.SEPARATOR,

            MenuItem("Quit", self.main.quit_program),
        )

        tray_icon = Icon("CatLock", image, "CatLock", menu)
        tray_icon.run()
