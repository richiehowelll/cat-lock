import tkinter as tk
from tkinter import ttk


class UserGuideWindow:
    def __init__(self, main):
        self.main = main
        self.root = None
        self.dont_show_var = None

    def _on_close(self):
        if self.dont_show_var is not None:
            self.main.config.user_guide_shown = self.dont_show_var.get()
            self.main.config.save()

        self.root.destroy()

    def open(self):
        self.root = tk.Toplevel(self.main.tk_root)
        self.root.title("Welcome to CatLock")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.minsize(350, 210)

        self.dont_show_var = tk.BooleanVar(master=self.root, value=True)
        self._configure_style()

        container = ttk.Frame(self.root, padding=(16, 14, 16, 14))
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Welcome to CatLock",
            style="Header.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            container,
            text="A quiet keyboard lock for moments when paws get curious.",
            style="Subtle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 12))

        hotkey = getattr(self.main.config, "hotkey", "Ctrl+L")
        hotkey_display = hotkey.upper()

        text = (
            f"- Press {hotkey_display} to lock your keyboard.\n"
            "- A compact overlay appears while input is blocked.\n"
            "- Click the overlay to unlock.\n"
            "- Use Settings from the tray menu to adjust the overlay."
        )

        ttk.Label(
            container,
            text=text,
            justify="left",
            wraplength=320,
        ).grid(row=2, column=0, sticky="w")

        ttk.Checkbutton(
            container,
            text="Don't show this again",
            variable=self.dont_show_var,
        ).grid(row=3, column=0, sticky="w", pady=(12, 0))

        button_row = ttk.Frame(container)
        button_row.grid(row=4, column=0, sticky="ew", pady=(14, 0))
        button_row.columnconfigure(0, weight=1)

        got_it_btn = ttk.Button(
            button_row,
            text="Got it",
            command=self._on_close,
            width=10,
        )
        got_it_btn.grid(row=0, column=0)
        got_it_btn.focus_set()

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
        style.configure("TButton", font=base_font, padding=(10, 5))
