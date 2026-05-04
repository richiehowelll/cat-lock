import tkinter as tk

OVERLAY_BG_COLOR = "#202124"
OVERLAY_BORDER_COLOR = "#5f6368"
OVERLAY_CLICK_BORDER_COLOR = "#8ab4f8"
OVERLAY_CLICK_BG_COLOR = "#2d3440"
OVERLAY_HOVER_BG_COLOR = "#26282c"
OVERLAY_TEXT_COLOR = "#f1f3f4"
OVERLAY_MUTED_TEXT_COLOR = "#bdc1c6"
OVERLAY_TITLE_FONT = ("Segoe UI", 15, "bold")
OVERLAY_BODY_FONT = ("Segoe UI", 10)
OVERLAY_HINT_FONT = ("Segoe UI", 9)


def build_overlay_content(parent, unlock_callback=None, preview: bool = False):
    inner = tk.Frame(
        parent,
        bg=OVERLAY_BG_COLOR,
        padx=24,
        pady=18,
    )
    inner.pack(expand=True, fill="both")

    title = tk.Label(
        inner,
        text="CatLock",
        fg=OVERLAY_TEXT_COLOR,
        bg=OVERLAY_BG_COLOR,
        font=OVERLAY_TITLE_FONT,
    )
    title.pack(anchor="center")

    body_text = "Keyboard locked" if not preview else "Preview"
    body = tk.Label(
        inner,
        text=body_text,
        fg=OVERLAY_TEXT_COLOR,
        bg=OVERLAY_BG_COLOR,
        font=OVERLAY_BODY_FONT,
    )
    body.pack(anchor="center", pady=(4, 0))

    hint_text = "Click to unlock" if not preview else "This matches the lock overlay"
    hint = tk.Label(
        inner,
        text=hint_text,
        fg=OVERLAY_MUTED_TEXT_COLOR,
        bg=OVERLAY_BG_COLOR,
        font=OVERLAY_HINT_FONT,
    )
    hint.pack(anchor="center", pady=(6, 0))

    widgets = (inner, title, body, hint)
    if unlock_callback is not None:
        for widget in widgets:
            widget.bind("<Button-1>", unlock_callback)
            widget.configure(cursor="hand2")

    return inner


def set_overlay_hover(content, hovered: bool) -> None:
    color = OVERLAY_HOVER_BG_COLOR if hovered else OVERLAY_BG_COLOR
    _set_bg((content, *content.winfo_children()), color)


def set_overlay_pressed(content, pressed: bool) -> None:
    color = OVERLAY_CLICK_BG_COLOR if pressed else OVERLAY_HOVER_BG_COLOR
    _set_bg((content, *content.winfo_children()), color)


def _set_bg(widgets, color: str) -> None:
    for widget in widgets:
        widget.configure(bg=color)
