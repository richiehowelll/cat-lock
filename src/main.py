import threading
import time
from queue import Empty, Queue

import keyboard

from src.config.config import Config
from src.keyboard_controller.hotkey_listener import HotkeyListener
from src.keyboard_controller.pressed_events_handler import clear_pressed_events
from src.os_controller.notifications import send_notification_in_thread
from src.os_controller.tray_icon import TrayIcon
from src.ui.overlay_window import OverlayWindow
from src.ui.update_window import UpdateWindow
from src.util.lockfile_handler import check_lockfile, remove_lockfile


class CatLockCore:
    def __init__(self) -> None:
        self.hotkey_thread = None
        self.show_overlay_queue = Queue()
        self.ui_action_queue = Queue()
        self.config = Config()
        self.root = None
        self.hotkey_lock = threading.Lock()
        self.hotkey_stop_event = None
        self.lock_state_lock = threading.Lock()
        self.listen_for_hotkey = True
        self.program_running = True
        self.is_locked = False
        self.lock_request_pending = False
        self.blocked_keys = set()
        self.changing_hotkey_queue = Queue()
        self.start_hotkey_listener()
        self.clear_pressed_events_thread = threading.Thread(target=clear_pressed_events, daemon=True)
        self.clear_pressed_events_thread.start()
        self.tray_icon_thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        self.tray_icon_thread.start()

    def create_tray_icon(self) -> None:
        TrayIcon(main=self).open()

    def start_hotkey_listener(self) -> None:
        HotkeyListener(self).start_hotkey_listener_thread()

    def lock_keyboard(self) -> None:
        with self.lock_state_lock:
            self.is_locked = True
        self.blocked_keys.clear()
        for i in range(150):
            keyboard.block_key(i)
            self.blocked_keys.add(i)
        send_notification_in_thread(self.config.notifications_enabled)

    def unlock_keyboard(self, event=None) -> None:
        for key in self.blocked_keys:
            keyboard.unblock_key(key)
        self.blocked_keys.clear()
        if self.root:
            self.root.destroy()
            self.root = None
        keyboard.stash_state()
        with self.lock_state_lock:
            self.is_locked = False
            self.lock_request_pending = False

    def send_hotkey_signal(self) -> None:
        with self.lock_state_lock:
            if self.is_locked or self.lock_request_pending:
                return
            self.lock_request_pending = True
        self.show_overlay_queue.put(True)

    def send_ui_action(self, action: str) -> None:
        self.ui_action_queue.put(action)

    def process_ui_actions(self) -> None:
        while True:
            try:
                action = self.ui_action_queue.get(block=False)
            except Empty:
                return

            if action == "settings":
                from src.ui.settings_window import SettingsWindow
                SettingsWindow(self).open()
            elif action == "user_guide":
                from src.ui.user_guide_window import UserGuideWindow
                UserGuideWindow(self).open()
            elif action == "quit":
                self.program_running = False
                self.unlock_keyboard()

    def quit_program(self, icon, item) -> None:
        remove_lockfile()
        self.program_running = False
        self.send_ui_action("quit")
        icon.stop()

    def start(self) -> None:
        check_lockfile()
        UpdateWindow(self).prompt_update()
        # hack to prevent right ctrl sticking
        keyboard.remap_key('right ctrl', 'left ctrl')

        if not self.config.user_guide_shown:
            from src.ui.user_guide_window import UserGuideWindow
            UserGuideWindow(self).open()

        while self.program_running or not self.ui_action_queue.empty():
            self.process_ui_actions()
            if not self.show_overlay_queue.empty():
                self.show_overlay_queue.get(block=False)
                while not self.show_overlay_queue.empty():
                    self.show_overlay_queue.get(block=False)
                overlay = OverlayWindow(main=self)
                keyboard.stash_state()
                overlay.open()
            time.sleep(.1)


if __name__ == "__main__":
    core = CatLockCore()
    core.start()
