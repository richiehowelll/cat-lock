from queue import Empty, Queue


class UiActionDispatcher:
    SETTINGS = "settings"
    USER_GUIDE = "user_guide"
    QUIT = "quit"

    def __init__(self, main) -> None:
        self.main = main
        # Thread-safe handoff from tray callbacks to the Tk-owning main loop.
        self.queue = Queue()

    def enqueue(self, action: str) -> None:
        self.queue.put(action)

    def has_pending_actions(self) -> bool:
        return not self.queue.empty()

    def process_actions(self) -> None:
        while True:
            try:
                action = self.queue.get(block=False)
            except Empty:
                return

            # Window imports stay local to the dispatch point.
            if action == self.SETTINGS:
                from src.ui.settings_window import SettingsWindow
                SettingsWindow(self.main).open()
            elif action == self.USER_GUIDE:
                from src.ui.user_guide_window import UserGuideWindow
                UserGuideWindow(self.main).open()
            elif action == self.QUIT:
                self.main.program_running = False
                self.main.unlock_keyboard()
                self.main.hotkey_listener.stop()
