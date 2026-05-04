from tkinter import messagebox

from src.util.update_util import is_update_available
from src.util.web_browser_util import open_download


class UpdateWindow:
    def __init__(self, main):
        self.main = main

    def prompt_update(self):
        if is_update_available():
            if messagebox.askyesno(
                "Update Available",
                "A new version of CatLock is available. Do you want to update?",
                parent=self.main.tk_root,
            ):
                open_download()
