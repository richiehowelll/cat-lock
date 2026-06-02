import threading
import logging

import keyboard

from src.os_controller.notifications import send_notification_in_thread

KEY_CODES_TO_BLOCK = range(150)


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

        blocked_keys = set()
        try:
            for key_code in KEY_CODES_TO_BLOCK:
                keyboard.block_key(key_code)
                blocked_keys.add(key_code)
        except Exception:
            self._unblock_keys(blocked_keys)
            with self.state_lock:
                self.is_locked = False
                self.lock_request_pending = False
            raise

        with self.state_lock:
            self.blocked_keys = blocked_keys

        send_notification_in_thread(self.notifications_enabled_getter())

    def unlock_keyboard(self) -> None:
        with self.state_lock:
            blocked_keys = self.blocked_keys
            self.blocked_keys = set()
            self.is_locked = False
            self.lock_request_pending = False

        self._unblock_keys(blocked_keys)
        # Clear keyboard's internal pressed-state cache after blocked-key use.
        keyboard.stash_state()

    @staticmethod
    def _unblock_keys(blocked_keys) -> None:
        for key in blocked_keys:
            try:
                keyboard.unblock_key(key)
            except Exception:
                logging.exception("Failed to unblock key code: %s", key)
