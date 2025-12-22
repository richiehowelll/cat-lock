import tkinter as tk

from src.ui.overlay_geometry import compute_overlay_geometry
from src.ui.overlay_style import OVERLAY_BG_COLOR, OVERLAY_BORDER_COLOR, OVERLAY_FONT, OVERLAY_TEXT_COLOR


class OverlayWindow:
    def __init__(self, main):
        self.main = main
        self._window = None

    def _build_window(self, geometry: str) -> None:
        self._window = tk.Toplevel(self.main.root)
        self._window.withdraw()
        self._window.overrideredirect(True)
        self._window.geometry(geometry)
        self._window.attributes("-topmost", True)

        outer = tk.Frame(
            self._window,
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

    def _ensure_window(self, geometry: str) -> None:
        if self._window is None or not self._window.winfo_exists():
            self._build_window(geometry)
        else:
            self._window.geometry(geometry)

    def _start_fade_in(self, target_alpha: float, duration_ms: int = 180, steps: int = 10):
        # Clamp target alpha
        if target_alpha <= 0:
            target_alpha = 0.05
        if target_alpha > 1:
            target_alpha = 1.0

        step_alpha = target_alpha / float(steps)
        step_time = max(10, duration_ms // steps)

        def fade_step(i=0):
            if not self._window or not self._window.winfo_exists():
                return  # window already gone
            current = step_alpha * i
            if current > target_alpha:
                current = target_alpha
            self._window.attributes("-alpha", current)
            if i < steps:
                self._window.after(step_time, fade_step, i + 1)

        # Start fully transparent and then run the fade
        self._window.attributes("-alpha", 0.0)
        self._window.after(0, fade_step)

    def open(self) -> None:
        y_percent = getattr(self.main.config, "overlay_y_percent", 25)
        overlay_width, overlay_height, x, y = compute_overlay_geometry(y_percent)
        geometry = f"{overlay_width}x{overlay_height}+{x}+{y}"
        self._ensure_window(geometry)

        self.main.lock_keyboard()

        target_alpha = getattr(self.main.config, "opacity", 0.8)
        self._start_fade_in(target_alpha=target_alpha)
        self._window.deiconify()
        self._window.lift()

    def hide(self) -> None:
        if self._window and self._window.winfo_exists():
            self._window.withdraw()
