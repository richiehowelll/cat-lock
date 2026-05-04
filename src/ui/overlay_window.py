import tkinter as tk

from src.ui.overlay_geometry import compute_overlay_geometry
from src.ui.overlay_style import (
    OVERLAY_BORDER_COLOR,
    build_overlay_content,
    set_overlay_hover,
)


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

        self.main.root = tk.Toplevel(self.main.tk_root)
        self.main.root.overrideredirect(True)
        self.main.root.geometry(f"{overlay_width}x{overlay_height}+{x}+{y}")
        self.main.root.attributes("-topmost", True)

        outer = tk.Frame(
            self.main.root,
            bg=OVERLAY_BORDER_COLOR,
        )
        outer.pack(expand=True, fill="both", padx=1, pady=1)

        content = build_overlay_content(outer, unlock_callback=self.main.unlock_keyboard)
        outer.bind("<Button-1>", self.main.unlock_keyboard)
        self.main.root.bind("<Enter>", lambda event: set_overlay_hover(content, True))
        self.main.root.bind(
            "<Leave>",
            lambda event: self.main.root.after(
                20,
                self._clear_hover_if_pointer_left,
                content,
            ),
        )

        self.main.lock_keyboard()

        target_alpha = getattr(self.main.config, "opacity", 0.8)
        self._start_fade_in(target_alpha=target_alpha)
        self._poll_for_shutdown()

        self.main.tk_root.wait_window(self.main.root)
        self.main.root = None

    def _poll_for_shutdown(self) -> None:
        if not self.main.root or not self.main.root.winfo_exists():
            return
        if not self.main.program_running:
            self.main.unlock_keyboard()
            return
        self.main.root.after(100, self._poll_for_shutdown)

    def _clear_hover_if_pointer_left(self, content) -> None:
        if not self.main.root or not self.main.root.winfo_exists():
            return

        pointer_x, pointer_y = self.main.root.winfo_pointerxy()
        left = self.main.root.winfo_rootx()
        top = self.main.root.winfo_rooty()
        right = left + self.main.root.winfo_width()
        bottom = top + self.main.root.winfo_height()

        if not (left <= pointer_x < right and top <= pointer_y < bottom):
            set_overlay_hover(content, False)
