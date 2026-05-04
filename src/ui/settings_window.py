import tkinter as tk
from tkinter import ttk

from src.config.config import DEFAULT_OPACITY
from src.ui.overlay_geometry import (
    compute_overlay_geometry,
    get_monitor_fingerprint,
    get_monitor_options,
)
from src.ui.overlay_style import OVERLAY_BORDER_COLOR, build_overlay_content


class SettingsWindow:
    def __init__(self, main):
        self.main = main
        self.root = None
        self.preview = None
        self.opacity_value_label = None
        self.position_value_label = None
        self.monitor_options = []
        self.monitor_label_to_index = {}
        self.monitor_var = None

    def _update_preview(self, *args):
        self._update_value_labels()
        if self.preview is None or not self.preview.winfo_exists():
            return

        y_percent = self.y_pos_var.get()
        monitor_index = self._selected_monitor_index()
        monitor_fingerprint = self._selected_monitor_fingerprint()
        overlay_width, overlay_height, x, y = compute_overlay_geometry(
            y_percent,
            overlay_width=420,
            overlay_height=120,
            monitor_index=monitor_index,
            monitor_fingerprint=monitor_fingerprint,
        )

        self.preview.geometry(f"{overlay_width}x{overlay_height}+{x}+{y}")
        self.preview.attributes("-alpha", self.opacity_var.get() / 100.0)

    def _create_preview_window(self):
        y_percent = self.y_pos_var.get()
        monitor_index = self._selected_monitor_index()
        monitor_fingerprint = self._selected_monitor_fingerprint()
        overlay_width, overlay_height, x, y = compute_overlay_geometry(
            y_percent,
            overlay_width=420,
            overlay_height=120,
            monitor_index=monitor_index,
            monitor_fingerprint=monitor_fingerprint,
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
        self.main.config.overlay_monitor_index = self._selected_monitor_index()
        self.main.config.overlay_monitor_fingerprint = (
            self._selected_monitor_fingerprint()
        )
        self.main.config.save()

        if self.preview is not None and self.preview.winfo_exists():
            self.preview.destroy()
        self.root.destroy()

    def _on_cancel(self):
        if self.preview is not None and self.preview.winfo_exists():
            self.preview.destroy()
        self.root.destroy()

    def _on_reset(self):
        self.opacity_var.set(int(DEFAULT_OPACITY * 100))
        self.y_pos_var.set(25)
        if self.monitor_options:
            self.monitor_var.set(self.monitor_options[0][1])
        self._update_preview()

    def open(self):
        self.root = tk.Toplevel(self.main.tk_root)
        self.root.title("CatLock Settings")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.minsize(360, 270)

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
        self._load_monitor_options()
        self.monitor_var = tk.StringVar(value=self._selected_monitor_label())

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
        ).grid(row=1, column=0, sticky="w", pady=(2, 2))

        reset_button = ttk.Label(
            container,
            text="Reset to defaults",
            style="Link.TLabel",
            cursor="hand2",
        )
        reset_button.grid(row=2, column=0, sticky="w", pady=(0, 14))
        reset_button.bind("<Button-1>", lambda event: self._on_reset())

        self._build_monitor_row(container, row=3)

        self._build_slider_row(
            container,
            row=4,
            label="Overlay opacity",
            variable=self.opacity_var,
            from_=5,
            to=90,
            value_attr="opacity_value_label",
        )
        self._build_slider_row(
            container,
            row=5,
            label="Vertical position",
            variable=self.y_pos_var,
            from_=0,
            to=100,
            value_attr="position_value_label",
            pady=(14, 0),
        )

        action_buttons = ttk.Frame(container)
        action_buttons.grid(row=6, column=0, pady=(18, 0))

        save_btn = ttk.Button(
            action_buttons,
            text="Save",
            command=self._on_save,
            width=10,
        )
        save_btn.pack(side="left", padx=(0, 8))

        ttk.Button(
            action_buttons,
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
        style.configure("Link.TLabel", font=("Segoe UI", 9), foreground="#2563eb")
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

    def _build_monitor_row(self, parent, row: int) -> None:
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="Monitor").grid(row=0, column=0, sticky="w")

        monitor_picker = ttk.Combobox(
            frame,
            textvariable=self.monitor_var,
            values=list(self.monitor_label_to_index.keys()),
            state="readonly",
        )
        monitor_picker.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        monitor_picker.bind("<<ComboboxSelected>>", self._update_preview)

    def _load_monitor_options(self) -> None:
        self.monitor_options = get_monitor_options()
        self.monitor_label_to_index = {
            label: monitor_index
            for monitor_index, label in self.monitor_options
        }

    def _selected_monitor_label(self) -> str:
        configured_index = getattr(self.main.config, "overlay_monitor_index", None)
        for monitor_index, label in self.monitor_options:
            if monitor_index == configured_index:
                return label

        return self.monitor_options[0][1]

    def _selected_monitor_index(self):
        if self.monitor_var is None:
            return getattr(self.main.config, "overlay_monitor_index", None)

        return self.monitor_label_to_index.get(self.monitor_var.get())

    def _selected_monitor_fingerprint(self):
        monitor_index = self._selected_monitor_index()
        return get_monitor_fingerprint(monitor_index)
