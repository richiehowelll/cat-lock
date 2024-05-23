import threading
import time
from queue import Queue

import keyboard

from src.config import Config
from src.hotkey_listener import HotkeyListener
from src.notifications import send_notification_in_thread
from src.tray_icon import TrayIcon
from src.ui.change_hotkey_window import ChangeHotkeyWindow
from src.ui.overlay_window import OverlayWindow


class KeyboardLock:
    def __init__(self):
        self.blocked_keys = set()
        self.program_running = True
        self.listen_for_hotkey = True
        self.hotkey_lock = threading.Lock()
        self.hotkey_thread = None
        self.tray_icon_thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        self.root = None
        self.config = Config()
        self.show_overlay_queue = Queue()
        self.show_change_hotkey_queue = Queue()
        self.start_hotkey_listener()
        self.tray_icon_thread.start()

    def create_tray_icon(self):
        TrayIcon(main=self)

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

        # Manually release the hotkey keys to ensure they're not stuck
        keyboard.release(self.config.hotkey)
        print(f"Keyboard Unlocked {self.config.hotkey}")
        if self.root:
            self.root.destroy()

    def send_hotkey_signal(self):
        self.show_overlay_queue.put(True)

    def send_change_hotkey_signal(self):
        self.show_change_hotkey_queue.put(True)

    def quit_program(self, icon, item):
        self.program_running = False
        self.unlock_keyboard()
        icon.stop()
        print("Program Exiting")

    def start(self):
        print("Program Starting")
        while self.program_running:
            if not self.show_overlay_queue.empty():
                self.show_overlay_queue.get(block=False)
                overlay = OverlayWindow(main=self)
                overlay.open()
            elif not self.show_change_hotkey_queue.empty():
                self.show_change_hotkey_queue.get(block=False)
                change_hotkey_window = ChangeHotkeyWindow(main=self)
                change_hotkey_window.open()
            time.sleep(.1)
