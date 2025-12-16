import tkinter as tk

from src.ui.overlay_geometry import compute_overlay_geometry
from src.ui.overlay_style import OVERLAY_BG_COLOR, OVERLAY_BORDER_COLOR, OVERLAY_FONT, OVERLAY_TEXT_COLOR


class OverlayWindow:
    def __init__(self, main):
        self.main = main

    def _start_fade_in(self, target_alpha: float, duration_ms: int = 180, steps: int = 10):
        # Clamp target alpha
        if target_alpha <= 0:
            target_alpha = 0.05
        if target_alpha > 1:
            target_alpha = 1.0

        step_alpha = target_alpha / float(steps)
        step_time = max(10, duration_ms // steps)

        def fade_step(i=0):
            if not self.main.root or not self.main.root.winfo_exists():
                return  # window already gone
            current = step_alpha * i
            if current > target_alpha:
                current = target_alpha
            self.main.root.attributes("-alpha", current)
            if i < steps:
                self.main.root.after(step_time, fade_step, i + 1)

        # Start fully transparent and then run the fade
        self.main.root.attributes("-alpha", 0.0)
        self.main.root.after(0, fade_step)

    def open(self) -> None:
        y_percent = getattr(self.main.config, "overlay_y_percent", 25)
        overlay_width, overlay_height, x, y = compute_overlay_geometry(y_percent)

        self.main.root = tk.Tk()
        self.main.root.overrideredirect(True)
        self.main.root.geometry(f"{overlay_width}x{overlay_height}+{x}+{y}")
        self.main.root.attributes("-topmost", True)

        outer = tk.Frame(
            self.main.root,
            bg=OVERLAY_BORDER_COLOR,
        )
        outer.pack(expand=True, fill="both", padx=1, pady=1)

        inner = tk.Frame(
            outer,
            bg=OVERLAY_BG_COLOR,
            padx=20,
            pady=16,
        )
        inner.pack(expand=True, fill="both")

        text = (
            "🔒 CatLock\n\n"
            "Keyboard is locked.\n"
            "Click this box to unlock."
        )

        label = tk.Label(
            inner,
            text=text,
            fg=OVERLAY_TEXT_COLOR,
            bg=OVERLAY_BG_COLOR,
            font=OVERLAY_FONT,
            justify="center",
        )
        label.pack(expand=True, fill="both")

        for widget in (outer, inner, label):
            widget.bind("<Button-1>", self.main.unlock_keyboard)

        self.main.lock_keyboard()

        target_alpha = getattr(self.main.config, "opacity", 0.8)
        self._start_fade_in(target_alpha=target_alpha)

        self.main.root.mainloop()
