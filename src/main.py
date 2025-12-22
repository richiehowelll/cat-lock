import threading
from queue import Queue

import keyboard
import tkinter as tk

from src.config.config import Config
from src.keyboard_controller.hotkey_listener import HotkeyListener
from src.keyboard_controller.pressed_events_handler import clear_pressed_events
from src.os_controller.notifications import send_notification_in_thread
from src.os_controller.tray_icon import TrayIcon
from src.ui.overlay_window import OverlayWindow
from src.ui.settings_window import SettingsWindow
from src.ui.update_window import UpdateWindow
from src.util.lockfile_handler import check_lockfile, remove_lockfile


class CatLockCore:
    def __init__(self) -> None:
        self.hotkey_thread = None
        self.show_overlay_queue = Queue()
        self.ui_task_queue = Queue()
        self.config = Config()
        self.root = tk.Tk()
        self.root.withdraw()
        self.hotkey_lock = threading.Lock()
        self.listen_for_hotkey = True
        self.program_running = True
        self.blocked_keys = set()
        self.changing_hotkey_queue = Queue()
        self.settings_window = None
        self.overlay = OverlayWindow(main=self)
        self.start_hotkey_listener()
        self.clear_pressed_events_thread = threading.Thread(
            target=clear_pressed_events, args=(lambda: self.program_running,), daemon=True
        )
        self.clear_pressed_events_thread.start()
        self.tray_icon_thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        self.tray_icon_thread.start()

    def create_tray_icon(self) -> None:
        TrayIcon(main=self).open()

    def start_hotkey_listener(self) -> None:
        HotkeyListener(self).start_hotkey_listener_thread()

    def lock_keyboard(self) -> None:
        self.blocked_keys.clear()
        for i in range(150):
            keyboard.block_key(i)
            self.blocked_keys.add(i)
        send_notification_in_thread(self.config.notifications_enabled)

    def unlock_keyboard(self, event=None) -> None:
        for key in self.blocked_keys:
            keyboard.unblock_key(key)
        self.blocked_keys.clear()
        self.overlay.hide()
        keyboard.stash_state()

    def send_hotkey_signal(self) -> None:
        self.show_overlay_queue.put(True)

    def quit_program(self, icon, item) -> None:
        remove_lockfile()
        self.program_running = False
        self.listen_for_hotkey = False
        self.show_overlay_queue.put(None)
        self.ui_task_queue.put(lambda: self._shutdown_ui(icon))

    def _clear_settings_window(self) -> None:
        self.settings_window = None

    def open_settings_window(self) -> None:
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self)
            self.settings_window.on_close = self._clear_settings_window

        if self.settings_window.is_open():
            self.settings_window.focus()
        else:
            self.settings_window.open()

    def _shutdown_ui(self, icon=None) -> None:
        self.unlock_keyboard()
        try:
            if icon is not None:
                icon.stop()
        finally:
            if self.root and self.root.winfo_exists():
                self.root.quit()

    def _drain_queues(self) -> None:
        while not self.show_overlay_queue.empty():
            try:
                signal = self.show_overlay_queue.get(block=False)
            except Exception:
                break
            if signal is None:
                # quit signal
                continue
            keyboard.stash_state()
            self.overlay.open()

        while not self.ui_task_queue.empty():
            try:
                fn = self.ui_task_queue.get(block=False)
            except Exception:
                break
            try:
                fn()
            except Exception:
                # Tk callbacks already surface errors to stderr; keep loop alive
                pass

        if self.program_running and self.root and self.root.winfo_exists():
            self.root.after(50, self._drain_queues)

    def schedule_on_ui_thread(self, callback) -> None:
        self.ui_task_queue.put(callback)

    def start(self) -> None:
        check_lockfile()
        UpdateWindow(self).prompt_update()
        # hack to prevent right ctrl sticking
        keyboard.remap_key('right ctrl', 'left ctrl')

        if not self.config.user_guide_shown:
            from src.ui.user_guide_window import UserGuideWindow
            UserGuideWindow(self).open()

        self.root.after(0, self._drain_queues)
        self.root.mainloop()


if __name__ == "__main__":
    core = CatLockCore()
    core.start()
