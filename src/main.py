import subprocess
import sys
import threading
import time
from queue import Queue

import keyboard

from src.config.config import Config
from src.keyboard_controller.hotkey_listener import HotkeyListener
from src.os_controller.notifications import send_notification_in_thread
from src.os_controller.tray_icon import TrayIcon
from src.ui.change_hotkey_window import ChangeHotkeyWindow
from src.ui.overlay_window import OverlayWindow


class CatLockCore:
    def __init__(self):
        self.hotkey_thread = None
        self.windows_lock_thread = None
        self.show_change_hotkey_queue = None
        self.show_overlay_queue = None
        self.config = None
        self.root = None
        self.hotkey_lock = None
        self.listen_for_hotkey = None
        self.program_running = None
        self.blocked_keys = None
        self.changing_hotkey_queue = None
        self.reset_main_queue = None
        self.reset()
        self.tray_icon_thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        self.tray_icon_thread.start()

    def reset(self):
        try:
            sys.modules.pop('keyboard')
        except Exception as e:
            pass
        self.changing_hotkey_queue = Queue()
        self.blocked_keys = set()
        self.program_running = True
        self.listen_for_hotkey = True
        self.hotkey_lock = threading.Lock()
        self.hotkey_thread = None
        self.root = None
        self.config = Config()
        self.show_overlay_queue = Queue()
        self.show_change_hotkey_queue = Queue()
        self.start_hotkey_listener()
        self.windows_lock_thread = threading.Thread(target=self.signal_windows_unlock, daemon=True)
        self.reset_main_queue = Queue()
        self.windows_lock_thread.start()

    def create_tray_icon(self):
        TrayIcon(main=self).open()

    def start_hotkey_listener(self):
        HotkeyListener(self).start_hotkey_listener_thread()

    def set_hotkey(self, new_hotkey):
        self.config.hotkey = new_hotkey
        self.config.save()

    def lock_keyboard(self):
        self.blocked_keys.clear()
        for i in range(150):
            keyboard.block_key(i)
            self.blocked_keys.add(i)
        send_notification_in_thread(self.config.notifications_enabled)

    def unlock_keyboard(self, event=None):
        for key in self.blocked_keys:
            keyboard.unblock_key(key)
        self.blocked_keys.clear()
        if self.root:
            self.root.destroy()
        keyboard.stash_state()
        self.reset_main_queue.put(True)

    def send_hotkey_signal(self):
        keyboard.stash_state()
        self.show_overlay_queue.put(True)

    def send_change_hotkey_signal(self):
        self.show_change_hotkey_queue.put(True)

    def quit_program(self, icon, item):
        self.program_running = False
        self.unlock_keyboard()
        icon.stop()

    def signal_windows_unlock(self):
        while self.program_running:
            process_name = 'LogonUI.exe'
            call_all = 'TASKLIST'
            output_all = subprocess.check_output(call_all)
            output_string_all = str(output_all)
            was_locked = False
            while process_name in output_string_all:
                was_locked = True
                time.sleep(1)
                output_all = subprocess.check_output(call_all)
                output_string_all = str(output_all)
            if was_locked:
                self.reset_main_queue.put(True)
            time.sleep(1)

    def start(self):
        while self.program_running:
            if not self.show_overlay_queue.empty():
                self.show_overlay_queue.get(block=False)
                overlay = OverlayWindow(main=self)
                overlay.open()
            elif not self.show_change_hotkey_queue.empty():
                self.show_change_hotkey_queue.get(block=False)
                change_hotkey_window = ChangeHotkeyWindow(main=self)
                change_hotkey_window.open()
            if not self.reset_main_queue.empty():
                self.reset()
            time.sleep(.1)


if __name__ == "__main__":
    core = CatLockCore()
    core.start()
