import threading
import time

import keyboard


class HotkeyListener:
    def __init__(self, main):
        self.main = main

    def start_hotkey_listener_thread(self) -> None:
        keyboard.stash_state()
        with self.main.hotkey_lock:
            if self.main.hotkey_stop_event:
                self.main.hotkey_stop_event.set()
            if self.main.hotkey_thread and threading.current_thread() is not self.main.hotkey_thread and self.main.hotkey_thread.is_alive():
                self.main.hotkey_thread.join(timeout=2)
                keyboard.unhook_all_hotkeys()
            self.main.hotkey_stop_event = threading.Event()
            self.main.listen_for_hotkey = True
            self.main.hotkey_thread = threading.Thread(
                target=self.hotkey_listener,
                args=(self.main.hotkey_stop_event, self.main.config.hotkey),
                daemon=True,
            )
            self.main.hotkey_thread.start()

    def hotkey_listener(self, stop_event: threading.Event, hotkey: str) -> None:
        keyboard.add_hotkey(hotkey, self.main.send_hotkey_signal, suppress=False)
        while not stop_event.is_set():
            time.sleep(1)
        keyboard.unhook_all_hotkeys()
