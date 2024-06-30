import os
import sys
from pathlib import Path


def get_packaged_path(path: str) -> str:
    try:
        wd = sys._MEIPASS
        return os.path.abspath(os.path.join(wd, path))
    except:
        base = Path(__file__).parent.parent.parent
        return os.path.join(base, path)


def get_config_path() -> str:
    home = str(Path.home())
    config_dir = os.path.join(home, '.catlock', 'config')
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return os.path.join(config_dir, "config.json")
