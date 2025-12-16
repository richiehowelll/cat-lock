from screeninfo import get_monitors


def get_target_monitor():
    """
    Return the primary monitor if possible, otherwise the first monitor,
    or a dummy 1920x1080 monitor if screeninfo returns nothing.
    """
    monitors = get_monitors()
    if not monitors:
        class Dummy:
            x = 0
            y = 0
            width = 1920
            height = 1080
        return Dummy()

    for m in monitors:
        if getattr(m, "is_primary", False):
            return m

    return monitors[0]


def compute_overlay_geometry(
    y_percent: int | float,
    overlay_width: int = 420,
    overlay_height: int = 120,
):
    """
    Compute (width, height, x, y) for the overlay, centered horizontally.
    y_percent: 0–100 percent from top of monitor where the overlay's top-left should be placed (roughly).
    """
    monitor = get_target_monitor()

    # Clamp percent
    try:
        y_percent = float(y_percent)
    except (TypeError, ValueError):
        y_percent = 25.0

    if y_percent < 0:
        y_percent = 0.0
    if y_percent > 100:
        y_percent = 100.0

    # Horizontal center
    x = monitor.x + (monitor.width - overlay_width) // 2

    # Vertical position: interpolate between top and bottom
    available = monitor.height - overlay_height
    y_offset = int(available * (y_percent / 100.0))
    y = monitor.y + y_offset

    return overlay_width, overlay_height, x, y
