import atexit
import os
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
from src.ui.overlay_window import OverlayWindow
from src.ui.update_window import UpdateWindow
from src.util.lockfile_handler import check_lockfile, remove_lockfile


class CatLockCore:
    def __init__(self) -> None:
        self.hotkey_thread = None
        self.windows_lock_thread = None
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

    def reset(self) -> None:
        # hack to deal with stuck hotkeys and keyboard library malfunctioning after windows lock screen
        try:
            sys.modules.pop('keyboard')
        except Exception as e:
            pass
        import keyboard
        self.changing_hotkey_queue = Queue()
        self.blocked_keys = set()
        self.program_running = True
        self.listen_for_hotkey = True
        self.hotkey_lock = threading.Lock()
        self.hotkey_thread = None
        self.root = None
        self.config = Config()
        self.show_overlay_queue = Queue()
        self.start_hotkey_listener()
        self.windows_lock_thread = threading.Thread(target=self.signal_windows_unlock, daemon=True)
        self.reset_main_queue = Queue()
        self.windows_lock_thread.start()

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
        keyboard.release('ctrl')
        self.blocked_keys.clear()
        if self.root:
            self.root.destroy()
        keyboard.stash_state()
        self.reset_main_queue.put(True)

    def send_hotkey_signal(self) -> None:
        self.show_overlay_queue.put(True)

    def quit_program(self, icon, item) -> None:
        remove_lockfile()
        self.program_running = False
        self.unlock_keyboard()
        icon.stop()

    def signal_windows_unlock(self) -> None:
        while self.program_running:
            process_name = 'LogonUI.exe'
            call_all = 'TASKLIST'
            no_console_flag = 0x08000000
            output_all = subprocess.check_output(call_all, creationflags=no_console_flag)
            output_string_all = str(output_all)
            was_locked = False
            while process_name in output_string_all:
                was_locked = True
                time.sleep(1)
                output_all = subprocess.check_output(call_all, creationflags=no_console_flag)
                output_string_all = str(output_all)
            if was_locked:
                self.reset_main_queue.put(True)
            time.sleep(1)

    def start(self) -> None:
        check_lockfile()
        UpdateWindow(self).prompt_update()
        # hack to prevent right ctrl sticking
        keyboard.remap_key('right ctrl', 'left ctrl')
        while self.program_running:
            if not self.show_overlay_queue.empty():
                self.show_overlay_queue.get(block=False)
                overlay = OverlayWindow(main=self)
                keyboard.stash_state()
                overlay.open()
            if not self.reset_main_queue.empty():
                self.reset()
            time.sleep(.1)


if __name__ == "__main__":
    core = CatLockCore()
    core.start()
