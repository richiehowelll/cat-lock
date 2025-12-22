import tkinter as tk
from tkinter import messagebox

from src.util.update_util import is_update_available
from src.util.web_browser_util import open_download


class UpdateWindow:
    def __init__(self, main):
        self.main = main

    def prompt_update(self):
        if is_update_available():
            self.main.root.withdraw()
            self.main.root.update_idletasks()
            if messagebox.askyesno(
                'Update Available',
                'A new version of CatLock is available. Do you want to update?',
                parent=self.main.root,
            ):
                open_download()
