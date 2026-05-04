import tkinter as tk
from tkinter import ttk

from src.ui.overlay_geometry import compute_overlay_geometry
from src.ui.overlay_style import OVERLAY_BORDER_COLOR, build_overlay_content


class SettingsWindow:
    def __init__(self, main):
        self.main = main
        self.root = None
        self.preview = None
        self.opacity_value_label = None
        self.position_value_label = None

    def _update_preview(self, *args):
        self._update_value_labels()
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

        outer = tk.Frame(self.preview, bg=OVERLAY_BORDER_COLOR)
        outer.pack(expand=True, fill="both", padx=1, pady=1)

        build_overlay_content(outer, preview=True)

    def _update_value_labels(self) -> None:
        if self.opacity_value_label is not None:
            self.opacity_value_label.configure(text=f"{self.opacity_var.get()}%")
        if self.position_value_label is not None:
            self.position_value_label.configure(text=f"{self.y_pos_var.get()}%")

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
        self.root = tk.Toplevel(self.main.tk_root)
        self.root.title("CatLock Settings")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.minsize(360, 230)

        self._configure_style()

        current_opacity_pct = int(self.main.config.opacity * 100)
        if current_opacity_pct < 5:
            current_opacity_pct = 5
        if current_opacity_pct > 90:
            current_opacity_pct = 90

        self.opacity_var = tk.IntVar(value=current_opacity_pct)
        self.y_pos_var = tk.IntVar(
            value=getattr(self.main.config, "overlay_y_percent", 25)
        )

        container = ttk.Frame(self.root, padding=(16, 14, 16, 14))
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)

        ttk.Label(
            container,
            text="Overlay Settings",
            style="Header.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            container,
            text="Tune how the lock prompt appears on screen.",
            style="Subtle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 14))

        self._build_slider_row(
            container,
            row=2,
            label="Overlay opacity",
            variable=self.opacity_var,
            from_=5,
            to=90,
            value_attr="opacity_value_label",
        )
        self._build_slider_row(
            container,
            row=3,
            label="Vertical position",
            variable=self.y_pos_var,
            from_=0,
            to=100,
            value_attr="position_value_label",
            pady=(14, 0),
        )

        buttons = ttk.Frame(container)
        buttons.grid(row=4, column=0, pady=(18, 0))

        save_btn = ttk.Button(
            buttons,
            text="Save",
            command=self._on_save,
            width=10,
        )
        save_btn.pack(side="left", padx=(0, 8))

        ttk.Button(
            buttons,
            text="Cancel",
            command=self._on_cancel,
            width=10,
        ).pack(side="left")
        save_btn.focus_set()

        self._create_preview_window()
        self._update_value_labels()

        self.root.update_idletasks()
        self.root.lift()
        self.root.focus_force()
        self.root.grab_set()

        self.main.tk_root.wait_window(self.root)

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        for candidate in ("vista", "default"):
            try:
                style.theme_use(candidate)
                break
            except tk.TclError:
                continue

        base_font = ("Segoe UI", 10)
        style.configure("TLabel", font=base_font)
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Subtle.TLabel", font=("Segoe UI", 9), foreground="#5f6368")
        style.configure("Value.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=base_font, padding=(10, 5))

    def _build_slider_row(
        self,
        parent,
        row: int,
        label: str,
        variable,
        from_: int,
        to: int,
        value_attr: str,
        pady=(0, 0),
    ) -> None:
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=pady)
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text=label).grid(row=0, column=0, sticky="w")

        value_label = ttk.Label(frame, style="Value.TLabel")
        value_label.grid(row=0, column=1, sticky="e")
        setattr(self, value_attr, value_label)

        slider = ttk.Scale(
            frame,
            from_=from_,
            to=to,
            orient="horizontal",
            variable=variable,
            command=lambda v: self._update_preview(),
        )
        slider.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))
