import json
import os.path
import shutil

from src.util.path_util import get_packaged_path, get_config_path
from src.util.web_browser_util import open_about

BUNDLED_CONFIG_FILE = os.path.join("resources", "config", "config.json")
DEFAULT_HOTKEY = "ctrl+l"
DEFAULT_OPACITY = 0.8
OVERLAY_OPACITY_REVISION = 1  # bump this if we need to change default again


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
        config = load() or {}

        self.hotkey = config.get("hotkey", DEFAULT_HOTKEY)
        self.opacity = float(config.get("opacity", DEFAULT_OPACITY))
        self.notifications_enabled = config.get("notificationsEnabled", True)

        self.overlay_y_percent = int(config.get("overlayYPercent", 25))
        if self.overlay_y_percent < 0:
            self.overlay_y_percent = 0
        if self.overlay_y_percent > 100:
            self.overlay_y_percent = 100

        self.user_guide_shown = bool(config.get("userGuideShown", False))

        # One-time migration: force all users to the new default opacity
        self.overlay_opacity_revision = int(config.get("overlayOpacityRevision", 0))

        needs_save = False

        if self.overlay_opacity_revision < OVERLAY_OPACITY_REVISION:
            self.opacity = DEFAULT_OPACITY
            self.overlay_opacity_revision = OVERLAY_OPACITY_REVISION
            needs_save = True

        # If there was no valid config at all, this is a first run.
        if not config:
            open_about()
            needs_save = True

        if needs_save:
            self.save()

    def save(self) -> None:
        print(f'saving to: {get_config_path()}')
        with open(get_config_path(), "w") as f:
            config = {
                "hotkey": self.hotkey,
                "opacity": self.opacity,
                "notificationsEnabled": self.notifications_enabled,
                "overlayYPercent": self.overlay_y_percent,
                "userGuideShown": self.user_guide_shown,
                "overlayOpacityRevision": self.overlay_opacity_revision,
            }
            json.dump(config, f)

