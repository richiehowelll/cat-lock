import tkinter as tk

from src.ui.overlay_geometry import compute_overlay_geometry


class OverlayWindow:
    def __init__(self, main):
        self.main = main

    def open(self) -> None:
        y_percent = getattr(self.main.config, "overlay_y_percent", 25)
        overlay_width, overlay_height, x, y = compute_overlay_geometry(y_percent)

        self.main.root = tk.Tk()
        self.main.root.overrideredirect(True)
        self.main.root.geometry(f"{overlay_width}x{overlay_height}+{x}+{y}")
        self.main.root.attributes("-topmost", True)
        self.main.root.attributes("-alpha", self.main.config.opacity)

        frame = tk.Frame(self.main.root, bg="black")
        frame.pack(expand=True, fill="both")

        text = (
            "CatLock\n\n"
            "Keyboard is locked.\n"
            "Click this box to unlock."
        )
        label = tk.Label(
            frame,
            text=text,
            fg="white",
            bg="black",
            font=("Segoe UI", 11),
            justify="center",
        )
        label.pack(expand=True, fill="both")

        frame.bind("<Button-1>", self.main.unlock_keyboard)
        label.bind("<Button-1>", self.main.unlock_keyboard)

        self.main.lock_keyboard()
        self.main.root.mainloop()
