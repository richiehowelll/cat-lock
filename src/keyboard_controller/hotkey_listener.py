import logging
import threading
import time

import keyboard


class HotkeyListener:
    def __init__(self, hotkey: str, callback) -> None:
        self.hotkey = hotkey
        self.callback = callback
        # Listener lifecycle state is updated under this lock.
        self.lock = threading.Lock()
        self.thread = None
        self.stop_event = None

    def start(self) -> None:
        keyboard.stash_state()
        with self.lock:
            self._stop_locked()
            self._start_locked()

    def restart(self, hotkey: str | None = None) -> None:
        with self.lock:
            if hotkey is not None:
                self.hotkey = hotkey
            self._stop_locked()
            self._start_locked()

    def stop(self) -> None:
        with self.lock:
            self._stop_locked()

    def _start_locked(self) -> None:
        self.stop_event = threading.Event()
        self.thread = threading.Thread(
            target=self._listen,
            args=(self.stop_event, self.hotkey),
            daemon=True,
        )
        self.thread.start()

    def _stop_locked(self) -> None:
        if self.stop_event:
            self.stop_event.set()
        if self.thread and threading.current_thread() is not self.thread and self.thread.is_alive():
            # Restart and shutdown wait briefly for the listener to release its
            # registered hotkey.
            self.thread.join(timeout=2)
        self.thread = None
        self.stop_event = None

    def _listen(self, stop_event: threading.Event, hotkey: str) -> None:
        handler = keyboard.add_hotkey(hotkey, self.callback, suppress=False)
        try:
            while not stop_event.is_set():
                time.sleep(1)
        finally:
            try:
                keyboard.remove_hotkey(handler)
            except (KeyError, ValueError):
                logging.debug("Hotkey was already removed: %s", hotkey)
