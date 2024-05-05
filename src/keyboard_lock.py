import gc
import json
import threading
import time
import tkinter as tk
import webbrowser
from collections import deque

import keyboard
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem


def open_about():
    webbrowser.open("https://github.com/richiehowelll/CatLock", new=2)


class KeyboardLock:
    def __init__(self):
        self.blocked_keys = set()
        self.program_running = True
        self.listen_for_hotkey = True
        self.hotkey_thread = threading.Thread(target=self.start_hotkey_listener, daemon=True)
        self.tray_icon_thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        self.root = None
        self.hotkey = "ctrl+shift+l"  # Default hotkey
        self.load_hotkey()

    def load_hotkey(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                if "hotkey" in config:
                    self.hotkey = config["hotkey"]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            pass  # Default to the built-in hotkey

    def save_hotkey(self):
        with open("config.json", "w") as f:
            json.dump({"hotkey": self.hotkey}, f)

    def set_hotkey(self, new_hotkey):
        self.hotkey = new_hotkey
        self.save_hotkey()

    def on_closing_hotkey_gui(self, hotkey_window):
        hotkey_window.destroy()
        gc.collect()
        self.listen_for_hotkey = True
        if self.hotkey_thread.is_alive():
            self.hotkey_thread.join()
        self.hotkey_thread.start()

    def change_hotkey(self):
        self.listen_for_hotkey = False
        if self.hotkey_thread.is_alive():
            self.hotkey_thread.join()  # Wait for the hotkey listener to stop

        self.hotkey_thread = threading.Thread(target=self.start_hotkey_listener, daemon=True)

        hotkey_window = tk.Tk()
        hotkey_window.title("Set Hotkey")
        hotkey_window.geometry("300x150")
        hotkey_window.attributes('-topmost', True)
        hotkey_window.protocol("WM_DELETE_WINDOW", lambda arg=hotkey_window: self.on_closing_hotkey_gui(arg))

        label = tk.Label(hotkey_window, text="Enter a new hotkey:")
        label.pack(pady=10)

        hotkey_entry = tk.Entry(hotkey_window, width=20)
        # Means of communication, between the gui & update threads:
        message_queue = deque()

        def event_handler(event):  # runs in main thread
            hotkey_entry.insert(tk.END, message_queue.popleft())

        hotkey_entry.bind("<<hotkey-event>>", event_handler)

        def set_hotkey_from_gui():
            new_hotkey = hotkey_entry.get()
            if new_hotkey:
                for key in self.hotkey.split("+"):
                    keyboard.release(key)
                    print(f"Key Unlocked {key}")
                self.set_hotkey(new_hotkey)
                print(f"Hotkey changed to: {new_hotkey}")
                hotkey_window.destroy()
                gc.collect()
                self.listen_for_hotkey = True
                if self.hotkey_thread.is_alive():
                    self.hotkey_thread.join()
                self.hotkey_thread.start()
            else:
                label.config(text="Invalid hotkey, try again.")

        set_hotkey_button = tk.Button(hotkey_window, text="Set Hotkey", command=set_hotkey_from_gui)
        hotkey_entry.pack(pady=10)
        hotkey_entry.focus()
        set_hotkey_button.pack(pady=10)

        def read_entry_non_blocking(entry):
            hotkey = keyboard.read_hotkey()
            message_queue.append(hotkey)
            time.sleep(1)  # Simulated delay (of 1 sec) between updates.
            print(hotkey)
            hotkey_entry.event_generate("<<hotkey-event>>")

        entry_listener_thread = threading.Thread(target=read_entry_non_blocking, args=(hotkey_entry,), daemon=True)
        entry_listener_thread.start()

        hotkey_window.mainloop()

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
        keyboard.release(self.hotkey)
        print(f"Keyboard Unlocked {self.hotkey}")

        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.destroy()
            gc.collect()

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
        keyboard.add_hotkey(self.hotkey, self.show_overlay)
        while self.program_running and self.listen_for_hotkey:
            time.sleep(1)
        keyboard.remove_hotkey(self.hotkey)

    def create_tray_icon(self):
        image = Image.open("../resources/img/icon.png")
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill="white")
        menu = Menu(
            MenuItem("About", open_about),
            MenuItem("Change Hotkey", self.change_hotkey),
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
