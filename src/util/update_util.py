import logging
from typing import Any, Dict

import requests

from src.version import VERSION

LATEST_RELEASE_URL = "https://api.github.com/repos/richiehowelll/cat-lock/releases/latest"


def is_update_available() -> bool:
    try:
        response = requests.get(LATEST_RELEASE_URL, timeout=5)
        response.raise_for_status()
        release_data: Dict[str, Any] = response.json()

        latest_tag = release_data.get("tag_name")
        if not latest_tag:
            return False

        if latest_tag == VERSION:
            return False

        # require installer asset to exist
        assets = release_data.get("assets") or []
        has_installer = any(
            (asset.get("name") or "").lower().endswith("catlocksetup.exe")
            for asset in assets
        )
        if not has_installer:
            # release exists but installer isn't attached yet
            return False

        if release_data.get("draft") or release_data.get("prerelease"):
            return False

        return True

    except requests.exceptions.RequestException as e:
        logging.info(f"Failed to check for updates: {e}")
    except Exception as e:
        logging.exception(f"Failed to check for updates: {e}")

    return False
