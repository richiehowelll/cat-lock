import threading
import time

import plyer


def send_lock_notification(notifications_enabled: bool):
    if notifications_enabled:
        plyer.notification.notify(
            app_name="CatLock",
            title="Keyboard Locked",
            message="Click on screen to unlock",
            app_icon="../resources/img/icon.ico",
            timeout=3,
        )
        time.sleep(.1)


def send_notification_in_thread(notifications_enabled: bool):
    if notifications_enabled:
        notification_thread = threading.Thread(target=send_lock_notification, args=notifications_enabled, daemon=True)
        notification_thread.start()
        notification_thread.join()
