import tkinter as tk
import keyboard
import threading
import time
import webbrowser
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw


def open_about():
    webbrowser.open("https://github.com/richiehowelll/CatLock", new=2)


class KeyboardLock:
    def __init__(self):
        self.blocked_keys = set()
        self.program_running = True
        self.hotkey_thread = threading.Thread(target=self.start_hotkey_listener, daemon=True)
        self.tray_icon_thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        self.root = None

    def lock_keyboard(self):
        self.blocked_keys.clear()
        for i in range(150):
            keyboard.block_key(i)
            self.blocked_keys.add(i)
        print("Keyboard Locked")

    def unlock_keyboard(self, event=None):
        for key in self.blocked_keys:
            keyboard.unblock_key(key)
        self.blocked_keys.clear()

        # Manually release the hotkey keys to ensure they're not stuck
        keyboard.release("ctrl")
        keyboard.release("shift")
        keyboard.release("l")

        print("Keyboard Unlocked")

        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.destroy()

    def show_overlay(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.5)
        self.root.bind('<Button-1>', self.unlock_keyboard)
        message = tk.Label(self.root, text="Keyboard Locked! Click to Unlock.", bg='black', fg='white', font=("Arial", 24))
        message.pack(expand=True)

        self.lock_keyboard()

        self.root.mainloop()

    def start_hotkey_listener(self):
        while self.program_running:
            keyboard.wait("ctrl+shift+l")
            if self.program_running:
                self.show_overlay()

    def create_tray_icon(self):
        image = Image.open("../resources/img/icon.png")
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill="white")
        menu = Menu(
            MenuItem("About", open_about),
            MenuItem("Quit", self.quit_program),
        )
        tray_icon = Icon("Keyboard Locker", image, "Keyboard Locker", menu)
        tray_icon.run()

    def quit_program(self, icon, item):
        self.program_running = False
        self.unlock_keyboard()
        icon.stop()
        print("Program Exiting")

    def start(self):
        print("Program Starting")
        self.hotkey_thread.start()
        self.tray_icon_thread.start()

        while self.program_running:
            time.sleep(1)
