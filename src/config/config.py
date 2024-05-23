import json
import os.path

from src.util.path_util import get_packaged_path

CONFIG_FILE = os.path.join("resources", "config", "config.json")
DEFAULT_HOTKEY = "ctrl+l"


def load():
    try:
        with open(get_packaged_path(CONFIG_FILE), "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass  # Fall back to the default hotkey


class Config:
    def __init__(self):
        config = load()
        if config:
            self.hotkey = config.get("hotkey", DEFAULT_HOTKEY)
            self.opacity = config.get("opacity", 0.3)
            self.notifications_enabled = config.get("notificationsEnabled", True)
        else:
            self.hotkey = DEFAULT_HOTKEY
            self.opacity = 0.3
            self.notifications_enabled = True
            self.save()

    def save(self):
        with open(get_packaged_path(CONFIG_FILE), "w") as f:
            config = {
                "hotkey": self.hotkey,
                "opacity": self.opacity,
                "notificationsEnabled": self.notifications_enabled,
            }
            json.dump(config, f)