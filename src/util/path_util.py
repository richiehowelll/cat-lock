import os
import sys
from pathlib import Path


def get_packaged_path(path: str) -> str:
    try:
        wd = sys._MEIPASS
        return os.path.join(wd, path)
    except:
        base = Path(__file__).parent.parent.parent
        return os.path.join(base, path)