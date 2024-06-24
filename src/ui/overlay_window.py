import tkinter as tk

from screeninfo import get_monitors


class OverlayWindow:
    def __init__(self, main):
        self.main = main

    def open(self) -> None:
        monitors = get_monitors()

        # Calculate combined geometry of all monitors
        total_width = sum([monitor.width for monitor in monitors])
        max_height = max([monitor.height for monitor in monitors])
        min_x = min([monitor.x for monitor in monitors])
        min_y = min([monitor.y for monitor in monitors])

        self.main.root = tk.Tk()
        self.main.root.overrideredirect(True)  # Remove window decorations
        self.main.root.geometry(f'{total_width}x{max_height}+{min_x}+{min_y}')
        self.main.root.attributes('-topmost', True)
        self.main.root.attributes('-alpha', self.main.config.opacity)
        self.main.root.bind('<Button-1>', self.main.unlock_keyboard)

        self.main.lock_keyboard()
        self.main.root.mainloop()