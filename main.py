import tkinter as tk
import keyboard
import threading
import time
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

blocked_keys = set()

program_running = True


def lock_keyboard():
    global blocked_keys
    blocked_keys.clear()
    for i in range(150):
        keyboard.block_key(i)
        blocked_keys.add(i)
    print("Keyboard Locked")


def unlock_keyboard(event=None):
    global blocked_keys
    for key in blocked_keys:
        keyboard.unblock_key(key)
    blocked_keys.clear()

    # Manually release the hotkey keys to ensure they're not stuck
    keyboard.release("ctrl")
    keyboard.release("shift")
    keyboard.release("l")

    print("Keyboard Unlocked")

    if 'root' in globals() and root.winfo_exists():  # Check if overlay is active
        root.destroy()  # Close the overlay


def show_overlay():
    global root
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes('-topmost', True)
    root.attributes('-alpha', 0.5)
    root.bind('<Button-1>', unlock_keyboard)
    message = tk.Label(root, text="Keyboard Locked! Click to Unlock.", bg='black', fg='white', font=("Arial", 24))
    message.pack(expand=True)

    lock_keyboard()

    root.mainloop()


def start_hotkey_listener():
    global program_running
    while program_running:
        keyboard.wait("ctrl+shift+l")
        if program_running:
            show_overlay()


def create_tray_icon():
    image = Image.new("RGB", (64, 64), "black")
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill="white")  # White square in the middle
    menu = Menu(
        MenuItem("Quit", quit_program)
    )
    tray_icon = Icon("Keyboard Locker", image, "Keyboard Locker", menu)
    tray_icon.run()


def quit_program(icon, item):
    global program_running
    unlock_keyboard()
    icon.stop()
    program_running = False
    print("Program Exiting")


try:
    hotkey_thread = threading.Thread(target=start_hotkey_listener, daemon=True)
    hotkey_thread.start()

    tray_icon_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_icon_thread.start()

    while program_running:
        time.sleep(1)
except Exception as e:
    print(e)
    exit()
