import tkinter as tk


class OverlayWindow:
    def __init__(self, main):
        self.main = main

    def open(self) -> None:
        self.main.root = tk.Tk()
        self.main.root.attributes('-fullscreen', True)
        self.main.root.attributes('-topmost', True)
        self.main.root.attributes('-alpha', self.main.config.opacity)
        self.main.root.bind('<Button-1>', self.main.unlock_keyboard)

        self.main.lock_keyboard()
        self.main.root.mainloop()