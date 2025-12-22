import tkinter as tk
from tkinter import ttk

from src.ui.overlay_geometry import compute_overlay_geometry
from src.ui.overlay_style import OVERLAY_TEXT_COLOR, OVERLAY_FONT, OVERLAY_BG_COLOR, OVERLAY_BORDER_COLOR


class SettingsWindow:
    def __init__(self, main):
        self.main = main
        self.root = None
        self.preview = None
        self.on_close = None
        self._in_cleanup = False

    def is_open(self):
        return self.root is not None and self.root.winfo_exists()

    def focus(self):
        if self.is_open():
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self._create_preview_window()
            self._update_preview()

    def _update_preview(self, *args):
        if self.preview is None or not self.preview.winfo_exists():
            self._create_preview_window()
            if self.preview is None or not self.preview.winfo_exists():
                return

        y_percent = self.y_pos_var.get()
        overlay_width, overlay_height, x, y = compute_overlay_geometry(
            y_percent,
            overlay_width=420,
            overlay_height=120,
        )

        self.preview.geometry(f"{overlay_width}x{overlay_height}+{x}+{y}")
        self.preview.attributes("-alpha", self.opacity_var.get() / 100.0)

    def _create_preview_window(self):
        """Create the preview window if missing and ensure it's visible."""
        if self.preview is None or not self.preview.winfo_exists():
            y_percent = self.y_pos_var.get()
            overlay_width, overlay_height, x, y = compute_overlay_geometry(
                y_percent,
                overlay_width=420,
                overlay_height=120,
            )

            self.preview = tk.Toplevel(self.root)
            self.preview.overrideredirect(True)
            self.preview.geometry(f"{overlay_width}x{overlay_height}+{x}+{y}")
            self.preview.attributes("-topmost", True)
            self.preview.attributes("-alpha", self.opacity_var.get() / 100.0)
            self.preview.transient(self.root)

            outer = tk.Frame(self.preview, bg=OVERLAY_BORDER_COLOR)
            outer.pack(expand=True, fill="both", padx=1, pady=1)

            inner = tk.Frame(outer, bg=OVERLAY_BG_COLOR, padx=20, pady=16)
            inner.pack(expand=True, fill="both")

            label = tk.Label(
                inner,
                text="CatLock preview",
                fg=OVERLAY_TEXT_COLOR,
                bg=OVERLAY_BG_COLOR,
                font=OVERLAY_FONT,
                justify="center",
            )
            label.pack(expand=True, fill="both")
        else:
            try:
                self.preview.deiconify()
                self.preview.lift()
            except tk.TclError:
                # Recreate if the window was torn down unexpectedly
                self.preview = None
                self._create_preview_window()

    def _cleanup(self):
        if self._in_cleanup:
            return
        self._in_cleanup = True
        if self.preview is not None and self.preview.winfo_exists():
            try:
                self.preview.destroy()
            except tk.TclError:
                pass
        self.preview = None

        if self.root is not None and self.root.winfo_exists():
            try:
                self.root.destroy()
            except tk.TclError:
                pass
        self.root = None

        if self.on_close:
            cb, self.on_close = self.on_close, None
            cb()

    def _on_save(self):
        self.main.config.opacity = self.opacity_var.get() / 100.0
        self.main.config.overlay_y_percent = self.y_pos_var.get()
        self.main.config.save()

        self._cleanup()

    def _on_cancel(self):
        self._cleanup()

    def open(self):
        self._in_cleanup = False
        self.root = tk.Toplevel(self.main.root)
        self.root.title("CatLock Settings")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.minsize(320, 190)  # a bit wider

        style = ttk.Style(self.root)
        for candidate in ("vista", "default"):
            try:
                style.theme_use(candidate)
                break
            except tk.TclError:
                continue

        base_font = ("Segoe UI", 10)
        style.configure("TLabel", font=base_font)
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("TButton", font=base_font, padding=(8, 4))

        # Opacity slider: 5–90%, map to 0.05–0.90
        current_opacity_pct = int(self.main.config.opacity * 100)
        if current_opacity_pct < 5:
            current_opacity_pct = 5
        if current_opacity_pct > 90:
            current_opacity_pct = 90

        self.opacity_var = tk.IntVar(master=self.root, value=current_opacity_pct)

        # Vertical position percent: 0–100 from config
        self.y_pos_var = tk.IntVar(
            master=self.root,
            value=getattr(self.main.config, "overlay_y_percent", 25)
        )

        # ---- Layout ----
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill="both", expand=True)

        sub = ttk.Label(
            container,
            text="Adjust the overlay while the keyboard is locked.",
        )
        sub.grid(row=0, column=0, sticky="w", pady=(0, 8))

        opacity_frame = ttk.Frame(container)
        opacity_frame.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        opacity_frame.columnconfigure(0, weight=1)

        ttk.Label(opacity_frame, text="Overlay opacity:").grid(
            row=0, column=0, sticky="w"
        )
        opacity_slider = ttk.Scale(
            opacity_frame,
            from_=5,
            to=90,
            orient="horizontal",
            variable=self.opacity_var,
            command=lambda v: self._update_preview(),
        )
        opacity_slider.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        position_frame = ttk.Frame(container)
        position_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        position_frame.columnconfigure(0, weight=1)

        ttk.Label(position_frame, text="Vertical position:").grid(
            row=0, column=0, sticky="w"
        )
        y_slider = ttk.Scale(
            position_frame,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.y_pos_var,
            command=lambda v: self._update_preview(),
        )
        y_slider.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        buttons = ttk.Frame(container)
        buttons.grid(row=4, column=0, pady=(14, 0), sticky="ew")
        buttons.columnconfigure(0, weight=1)

        btn_container = ttk.Frame(buttons)
        btn_container.grid(row=0, column=0)

        save_btn = ttk.Button(
            btn_container,
            text="Save",
            command=self._on_save,
            width=10,
        )
        save_btn.pack(side="left", padx=(0, 8))

        cancel_btn = ttk.Button(
            btn_container,
            text="Cancel",
            command=self._on_cancel,
            width=10,
        )
        cancel_btn.pack(side="left")

        self._create_preview_window()

        self.root.update_idletasks()
        self.root.lift()
        self.root.focus_force()
        try:
            self.root.grab_set()
        except tk.TclError:
            # If grab fails (e.g., window not yet viewable), continue without modal grab
            pass

        self.root.transient(self.main.root)

