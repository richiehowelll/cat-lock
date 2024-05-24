import os
import threading
import time

import plyer

from src.util.path_util import get_packaged_path


def send_lock_notification() -> None:
    path = os.path.join("resources", "img", "icon.ico")
    plyer.notification.notify(
        app_name="CatLock",
        title="Keyboard Locked",
        message="Click on screen to unlock",
        app_icon=get_packaged_path(path),
        timeout=3,
    )
    time.sleep(.1)


def send_notification_in_thread(notifications_enabled: bool) -> None:
    if notifications_enabled:
        notification_thread = threading.Thread(target=send_lock_notification, daemon=True)
        notification_thread.start()
        notification_thread.join()
