import threading
import time

import keyboard


class HotkeyListener:
    def __init__(self, kl):
        self.kl = kl

    def start_hotkey_listener_thread(self):
        keyboard.stash_state()
        with self.kl.hotkey_lock:
            self.kl.listen_for_hotkey = True
            if self.kl.hotkey_thread and threading.current_thread() is not self.kl.hotkey_thread and self.kl.hotkey_thread.is_alive():
                self.kl.hotkey_thread.join()
            self.kl.hotkey_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
            self.kl.hotkey_thread.start()

    def hotkey_listener(self):
        keyboard.add_hotkey(self.kl.config.hotkey, self.kl.send_hotkey_signal)
        while self.kl.listen_for_hotkey:
            time.sleep(1)
        keyboard.remove_hotkey(self.kl.config.hotkey)