import tkinter as tk
from tkinter import ttk

from src.ui.overlay_geometry import compute_overlay_geometry


class SettingsWindow:
    def __init__(self, main):
        self.main = main
        self.root = None
        self.preview = None

    def _update_preview(self, *args):
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
        y_percent = self.y_pos_var.get()
        overlay_width, overlay_height, x, y = compute_overlay_geometry(
            y_percent,
            overlay_width=420,
            overlay_height=120,
        )

        # in case there's an old live one
        if self.preview is not None and self.preview.winfo_exists():
            try:
                self.preview.destroy()
            except tk.TclError:
                pass

        self.preview = tk.Toplevel(self.root)
        self.preview.overrideredirect(True)
        self.preview.geometry(f"{overlay_width}x{overlay_height}+{x}+{y}")
        self.preview.attributes("-topmost", True)
        self.preview.attributes("-alpha", self.opacity_var.get() / 100.0)

        frame = tk.Frame(self.preview, bg="black")
        frame.pack(expand=True, fill="both")

        label = tk.Label(
            frame,
            text="CatLock preview",
            fg="white",
            bg="black",
            font=("Segoe UI", 10),
            justify="center",
        )
        label.pack(expand=True, fill="both")

    def _on_save(self):
        self.main.config.opacity = self.opacity_var.get() / 100.0
        self.main.config.overlay_y_percent = self.y_pos_var.get()
        self.main.config.save()

        if self.preview is not None and self.preview.winfo_exists():
            self.preview.destroy()
        self.root.destroy()

    def _on_cancel(self):
        if self.preview is not None and self.preview.winfo_exists():
            self.preview.destroy()
        self.root.destroy()

    def open(self):
        self.root = tk.Tk()
        self.root.title("CatLock Settings")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.minsize(320, 190)  # a bit wider

        # ---- Theming / style ----
        style = ttk.Style(self.root)
        # Try a modern theme if available
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
        # -------------------------

        # Opacity slider: 5–90%, map to 0.05–0.90
        current_opacity_pct = int(self.main.config.opacity * 100)
        if current_opacity_pct < 5:
            current_opacity_pct = 5
        if current_opacity_pct > 90:
            current_opacity_pct = 90

        self.opacity_var = tk.IntVar(value=current_opacity_pct)

        # Vertical position percent: 0–100 from config
        self.y_pos_var = tk.IntVar(
            value=getattr(self.main.config, "overlay_y_percent", 25)
        )

        # ---- Layout ----
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill="both", expand=True)

        # Small subtitle
        sub = ttk.Label(
            container,
            text="Adjust the overlay while the keyboard is locked.",
        )
        sub.grid(row=0, column=0, sticky="w", pady=(0, 8))

        # Opacity controls
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

        # Vertical position controls
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

        # Buttons (centered)
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

        # Make settings window focused and modal so first click lands on buttons
        self.root.update_idletasks()
        self.root.lift()
        self.root.focus_force()
        self.root.grab_set()

        self.root.mainloop()

