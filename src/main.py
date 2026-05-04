import threading
import time
from queue import Queue

import keyboard

from src.config.config import Config
from src.keyboard_controller.hotkey_listener import HotkeyListener
from src.keyboard_controller.keyboard_lock_controller import KeyboardLockController
from src.keyboard_controller.pressed_events_handler import clear_pressed_events
from src.os_controller.tray_icon import TrayIcon
from src.ui.overlay_window import OverlayWindow
from src.ui.update_window import UpdateWindow
from src.ui.ui_action_dispatcher import UiActionDispatcher
from src.util.lockfile_handler import check_lockfile, remove_lockfile


class CatLockCore:
    def __init__(self) -> None:
        # Cross-thread lock requests are funneled through the main loop.
        self.show_overlay_queue = Queue()
        self.config = Config()
        self.root = None
        self.program_running = True
        self.ui_dispatcher = UiActionDispatcher(self)
        self.keyboard_lock = KeyboardLockController(
            notifications_enabled_getter=lambda: self.config.notifications_enabled,
        )
        self.hotkey_listener = HotkeyListener(
            hotkey=self.config.hotkey,
            callback=self.send_hotkey_signal,
        )
        self.hotkey_listener.start()
        # Lifecycle-bound workaround for stale keyboard pressed-state entries
        # left behind by Windows lock/unlock transitions.
        self.clear_pressed_events_thread = threading.Thread(
            target=clear_pressed_events,
            args=(lambda: self.program_running,),
            daemon=True,
        )
        self.clear_pressed_events_thread.start()
        self.tray_icon_thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        self.tray_icon_thread.start()

    def create_tray_icon(self) -> None:
        TrayIcon(main=self).open()

    def start_hotkey_listener(self) -> None:
        self.hotkey_listener.restart(self.config.hotkey)

    def lock_keyboard(self) -> None:
        self.keyboard_lock.lock_keyboard()

    def unlock_keyboard(self, event=None) -> None:
        if self.root:
            self.root.destroy()
            self.root = None
        self.keyboard_lock.unlock_keyboard()

    def send_hotkey_signal(self) -> None:
        # A pending request represents one overlay session waiting to start.
        if not self.keyboard_lock.reserve_lock_request():
            return
        self.show_overlay_queue.put(True)

    def send_ui_action(self, action: str) -> None:
        self.ui_dispatcher.enqueue(action)

    def quit_program(self, icon, item) -> None:
        remove_lockfile()
        self.program_running = False
        self.send_ui_action(UiActionDispatcher.QUIT)
        icon.stop()

    def start(self) -> None:
        check_lockfile()
        UpdateWindow(self).prompt_update()
        # hack to prevent right ctrl sticking
        keyboard.remap_key('right ctrl', 'left ctrl')

        if not self.config.user_guide_shown:
            from src.ui.user_guide_window import UserGuideWindow
            UserGuideWindow(self).open()

        while self.program_running or self.ui_dispatcher.has_pending_actions():
            # Tk windows are created from this loop; background callbacks only
            # enqueue UI actions.
            self.ui_dispatcher.process_actions()
            if not self.show_overlay_queue.empty():
                self.show_overlay_queue.get(block=False)
                # One active overlay session consumes all pending lock signals.
                while not self.show_overlay_queue.empty():
                    self.show_overlay_queue.get(block=False)
                overlay = OverlayWindow(main=self)
                keyboard.stash_state()
                overlay.open()
            time.sleep(.1)

        self.hotkey_listener.stop()


if __name__ == "__main__":
    core = CatLockCore()
    core.start()
