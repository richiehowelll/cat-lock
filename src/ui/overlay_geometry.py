from screeninfo import get_monitors


def get_target_monitor(
    monitor_index: int | None = None,
    monitor_fingerprint: dict | None = None,
):
    """
    Return the configured monitor if possible, otherwise the primary monitor,
    then the first monitor, or a dummy 1920x1080 monitor if screeninfo returns
    nothing.
    """
    monitors = get_monitors()
    if not monitors:
        return _dummy_monitor()

    fingerprint_match = _find_monitor_by_fingerprint(monitors, monitor_fingerprint)
    if fingerprint_match is not None:
        return fingerprint_match

    if monitor_index is not None and 0 <= monitor_index < len(monitors):
        return monitors[monitor_index]

    for m in monitors:
        if getattr(m, "is_primary", False):
            return m

    return monitors[0]


def compute_overlay_geometry(
    y_percent: int | float,
    overlay_width: int = 420,
    overlay_height: int = 120,
    monitor_index: int | None = None,
    monitor_fingerprint: dict | None = None,
):
    """
    Compute (width, height, x, y) for the overlay, centered horizontally.
    y_percent: 0-100 percent from top of monitor where the overlay's top-left should be placed (roughly).
    """
    monitor = get_target_monitor(monitor_index, monitor_fingerprint)

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


def get_monitor_options():
    monitors = get_monitors()
    if not monitors:
        return [(None, "Primary monitor")]

    options = []
    for index, monitor in enumerate(monitors):
        label = f"Monitor {index + 1}: {monitor.width}x{monitor.height}"
        if getattr(monitor, "is_primary", False):
            label = f"{label} (primary)"
        options.append((index, label))
    return options


def get_monitor_fingerprint(monitor_index: int | None):
    monitors = get_monitors()
    if monitor_index is None or not (0 <= monitor_index < len(monitors)):
        return None

    return _monitor_fingerprint(monitors[monitor_index])


def _find_monitor_by_fingerprint(monitors, monitor_fingerprint: dict | None):
    if not monitor_fingerprint:
        return None

    for monitor in monitors:
        if _monitor_fingerprint(monitor) == monitor_fingerprint:
            return monitor

    return None


def _monitor_fingerprint(monitor) -> dict:
    return {
        "x": int(monitor.x),
        "y": int(monitor.y),
        "width": int(monitor.width),
        "height": int(monitor.height),
        "isPrimary": bool(getattr(monitor, "is_primary", False)),
    }


def _dummy_monitor():
    class Dummy:
        x = 0
        y = 0
        width = 1920
        height = 1080

    return Dummy()
