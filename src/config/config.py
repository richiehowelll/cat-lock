import json

CONFIG_FILE = "../config.json"
DEFAULT_HOTKEY = "ctrl+shift+l"


def load():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass  # Fall back to the default hotkey


class Config:
    def __init__(self):
        config = load()
        self.hotkey = config.get("hotkey", DEFAULT_HOTKEY)
        self.opacity = config.get("opacity", 0.5)
        self.notifications_enabled = config.get("notificationsEnabled", True)

    def save(self):
        with open(CONFIG_FILE, "w") as f:
            config = {
                "hotkey": self.hotkey,
                "opacity": self.opacity,
                "notificationsEnabled": self.notifications_enabled,
            }
            json.dump(config, f)