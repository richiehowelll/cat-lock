import time

import keyboard


def clear_pressed_events(is_running) -> None:
    while is_running():
        # Hotkeys stop working after windows locks & unlocks
        # https://github.com/boppreh/keyboard/issues/223
        deleted = []
        with keyboard._pressed_events_lock:
            for k in list(keyboard._pressed_events.keys()):
                item = keyboard._pressed_events[k]
                if time.time() - item.time > 2:
                    deleted.append(item.name)
                    del keyboard._pressed_events[k]
        time.sleep(1)
