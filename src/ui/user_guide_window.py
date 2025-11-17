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
        self.root = tk.Tk()
        self.root.title("Welcome to CatLock")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.minsize(320, 160)

        self.dont_show_var = tk.BooleanVar(master=self.root, value=True)

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

        container = ttk.Frame(self.root, padding=10)
        container.pack(fill="both", expand=True)

        header = ttk.Label(
            container,
            text="Welcome to CatLock",
            style="Header.TLabel",
        )
        header.grid(row=0, column=0, sticky="w")

        hotkey = getattr(self.main.config, "hotkey", "Ctrl+L")
        hotkey_display = hotkey.upper()

        text = (
            f"• Press {hotkey_display} to lock your keyboard.\n"
            "• A small overlay will appear on your screen.\n"
            "• Click the overlay box to unlock."
        )
        desc = ttk.Label(container, text=text, justify="left")
        desc.grid(row=1, column=0, sticky="w", pady=(4, 8))

        chk = ttk.Checkbutton(
            container,
            text="Don't show this again",
            variable=self.dont_show_var,
        )
        chk.grid(row=2, column=0, sticky="w")

        btn_row = ttk.Frame(container)
        btn_row.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        btn_row.columnconfigure(0, weight=1)

        got_it_btn = ttk.Button(
            btn_row,
            text="Got it",
            command=self._on_close,
            width=10,
        )
        got_it_btn.grid(row=0, column=0)

        self.root.update_idletasks()
        self.root.lift()
        self.root.focus_force()
        self.root.grab_set()

        self.root.mainloop()
