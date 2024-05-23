import tkinter as tk


class Overlay:
    def __init__(self, main):
        self.main = main


def show(self):
    self.root = tk.Tk()
    self.root.attributes('-fullscreen', True)
    self.root.attributes('-topmost', True)
    self.root.attributes('-alpha', self.config.opacity)
    self.root.bind('<Button-1>', self.unlock_keyboard)

    self.lock_keyboard()
    self.root.mainloop()