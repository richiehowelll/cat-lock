import threading
from tkinter import messagebox

from src.util.update_util import is_update_available
from src.util.web_browser_util import open_download


class UpdateWindow:
    def __init__(self, main):
        self.main = main

    def check_for_update_in_thread(self) -> None:
        thread = threading.Thread(target=self._check_for_update, daemon=True)
        thread.start()

    def _check_for_update(self) -> None:
        if self.main.program_running and is_update_available():
            from src.ui.ui_action_dispatcher import UiActionDispatcher
            self.main.send_ui_action(UiActionDispatcher.UPDATE_AVAILABLE)

    def prompt_update(self) -> None:
        if messagebox.askyesno(
            "Update Available",
            "A new version of CatLock is available. Do you want to update?",
            parent=self.main.tk_root,
        ):
            open_download()
