import threading
import time

import keyboard


class HotkeyListener:
    def __init__(self, main):
        self.main = main

    def start_hotkey_listener_thread(self) -> None:
        keyboard.stash_state()
        with self.main.hotkey_lock:
            self.main.listen_for_hotkey = True
            if self.main.hotkey_thread and threading.current_thread() is not self.main.hotkey_thread and self.main.hotkey_thread.is_alive():
                self.main.hotkey_thread.join()
            self.main.hotkey_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
            self.main.hotkey_thread.start()

    def hotkey_listener(self) -> None:
        keyboard.add_hotkey(self.main.config.hotkey, self.main.send_hotkey_signal, suppress=True)
        while self.main.listen_for_hotkey:
            time.sleep(1)
        keyboard.unhook_all_hotkeys()
