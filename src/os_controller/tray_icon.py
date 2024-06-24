import os

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

from src.util.path_util import get_packaged_path
from src.util.web_browser_util import open_about, open_buy_me_a_coffee


class TrayIcon:
    def __init__(self, main):
        self.main = main

    def set_opacity(self, opacity: int) -> None:
        self.main.config.opacity = opacity
        self.main.config.save()

    def toggle_notifications(self) -> None:
        self.main.config.notifications_enabled = not self.main.config.notifications_enabled
        self.main.config.save()

    def open(self) -> None:
        path = os.path.join("resources", "img", "icon.png")
        image = Image.open(get_packaged_path(path))
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill="white")
        menu = Menu(
            MenuItem("About", open_about),
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
            MenuItem("Support ☕", open_buy_me_a_coffee),
            MenuItem("Quit", self.main.quit_program),
        )
        tray_icon = Icon("CatLock", image, "CatLock", menu)
        tray_icon.run()
