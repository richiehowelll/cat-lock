import json
import os.path
import shutil

from src.util.path_util import get_packaged_path, get_config_path
from src.util.web_browser_util import open_about

BUNDLED_CONFIG_FILE = os.path.join("resources", "config", "config.json")
DEFAULT_HOTKEY = "ctrl+l"


def load():
    try:
        with open(get_config_path(), "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        shutil.copy(get_packaged_path(BUNDLED_CONFIG_FILE), get_config_path())
        with open(get_config_path(), "r") as f:
            return json.load(f)


class Config:
    def __init__(self) -> None:
        config = load()
        self.hotkey = config.get("hotkey", DEFAULT_HOTKEY) if config else DEFAULT_HOTKEY
        self.opacity = config.get("opacity", 0.3) if config else 0.3
        self.notifications_enabled = config.get("notificationsEnabled", True) if config else True
        self.first_open = config.get("firstOpen", True) if config else True
        if self.first_open:
            open_about()
            self.save()
        if not config:
            open_about()
            self.save()

    def save(self) -> None:
        print(f'saving to: {get_config_path()}')
        with open(get_config_path(), "w") as f:
            config = {
                "hotkey": self.hotkey,
                "opacity": self.opacity,
                "notificationsEnabled": self.notifications_enabled,
                "firstOpen": False
            }
            json.dump(config, f)
