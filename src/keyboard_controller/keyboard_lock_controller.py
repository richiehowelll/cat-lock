import threading

import keyboard

from src.os_controller.notifications import send_notification_in_thread


class KeyboardLockController:
    def __init__(self, notifications_enabled_getter) -> None:
        self.notifications_enabled_getter = notifications_enabled_getter
        # Shared lock state is accessed by hotkey and UI callback paths.
        self.state_lock = threading.Lock()
        self.blocked_keys = set()
        self.is_locked = False
        self.lock_request_pending = False

    def reserve_lock_request(self) -> bool:
        # Pending means the main loop has accepted a lock request but has not
        # opened the overlay yet.
        with self.state_lock:
            if self.is_locked or self.lock_request_pending:
                return False
            self.lock_request_pending = True
            return True

    def lock_keyboard(self) -> None:
        with self.state_lock:
            self.is_locked = True

        self.blocked_keys.clear()
        for i in range(150):
            keyboard.block_key(i)
            self.blocked_keys.add(i)

        send_notification_in_thread(self.notifications_enabled_getter())

    def unlock_keyboard(self) -> None:
        for key in self.blocked_keys:
            keyboard.unblock_key(key)
        self.blocked_keys.clear()
        # Clear keyboard's internal pressed-state cache after blocked-key use.
        keyboard.stash_state()

        with self.state_lock:
            self.is_locked = False
            self.lock_request_pending = False
