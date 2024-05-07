import json
import threading
import time
import tkinter as tk
import webbrowser
from queue import Queue
import plyer

import keyboard
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

DEFAULT_HOTKEY = "ctrl+shift+l"
CONFIG_FILE = "config.json"


def open_about():
    webbrowser.open("https://github.com/richiehowelll/CatLock", new=2)


class KeyboardLock:
    def __init__(self):
        self.blocked_keys = set()
        self.program_running = True
        self.listen_for_hotkey = True
        self.hotkey_lock = threading.Lock()
        self.hotkey_thread = None
        self.tray_icon_thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        self.root = None
        self.hotkey = DEFAULT_HOTKEY
        self.load_config()
        self.show_overlay_queue = Queue()
        self.show_change_hotkey_queue = Queue()
        self.start_hotkey_listener_thread()
        self.tray_icon_thread.start()
        self.opacity = .5
        self.notifications_enabled = True

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.hotkey = config.get("hotkey", DEFAULT_HOTKEY)
                self.opacity = config.get("opacity", 0.5)
                self.notifications_enabled = config.get("notificationEnabled", True)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Fall back to the default hotkey

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            config = {
                "hotkey": self.hotkey,
                "opacity": self.opacity,
                "notificationEnabled": self.notifications_enabled,
            }
            json.dump(config, f)

    def send_lock_notification(self):
        if self.notifications_enabled:
            plyer.notification.notify(
                app_name="CatLock",
                title="Keyboard Locked",
                message="Click on screen to unlock",
                app_icon="../resources/img/icon.ico",
                timeout=3,
            )
            time.sleep(.1)

    def send_notification_in_thread(self):
        if self.notifications_enabled:
            notification_thread = threading.Thread(target=self.send_lock_notification, daemon=True)
            notification_thread.start()
            notification_thread.join()

    def set_opacity(self, opacity):
        self.opacity = opacity
        self.save_config()

    def set_hotkey(self, new_hotkey):
        self.hotkey = new_hotkey
        self.save_config()

    def toggle_notifications(self):
        self.notifications_enabled = not self.notifications_enabled
        self.save_config()

    def change_hotkey(self):
        self.listen_for_hotkey = False
        if self.hotkey_thread.is_alive():
            self.hotkey_thread.join()

        with self.hotkey_lock:
            self.hotkey_thread = threading.Thread(target=self.start_hotkey_listener_thread, daemon=True)

            hotkey_window = tk.Tk()
            hotkey_window.title("Set Hotkey")
            hotkey_window.geometry("300x150")
            hotkey_window.attributes('-topmost', True)

            def on_closing():
                hotkey_window.destroy()
                self.start_hotkey_listener_thread()

            hotkey_window.protocol("WM_DELETE_WINDOW", on_closing)

            label = tk.Label(hotkey_window, text="Enter a new hotkey:")
            label.pack(pady=10)

            hotkey_entry = tk.Entry(hotkey_window, width=20)
            entry_queue = Queue()

            def poll_queue():
                while True:
                    if not entry_queue.empty():
                        hotkey_entry.insert(tk.END, entry_queue.get(block=False))
                    break
                hotkey_window.after(100, poll_queue)

            def set_hotkey_from_gui():
                new_hotkey = hotkey_entry.get()
                if new_hotkey:
                    for key in self.hotkey.split("+"):
                        keyboard.release(key)
                        print(f"Key Unlocked {key}")
                    self.set_hotkey(new_hotkey)
                    print(f"Hotkey changed to: {new_hotkey}")
                    on_closing()
                else:
                    label.config(text="Invalid hotkey, try again.")

            set_hotkey_button = tk.Button(hotkey_window, text="Set Hotkey", command=set_hotkey_from_gui)
            hotkey_entry.pack(pady=10)
            hotkey_entry.focus_force()
            set_hotkey_button.pack(pady=10)

        def read_user_inp():
            hotkey = keyboard.read_hotkey()
            entry_queue.put(hotkey)
            time.sleep(.5)
            print(hotkey)

        entry_listener_thread = threading.Thread(target=read_user_inp, daemon=True)
        entry_listener_thread.start()
        hotkey_window.after(100, poll_queue)
        hotkey_window.mainloop()
        entry_listener_thread.join()

    def lock_keyboard(self):
        self.blocked_keys.clear()
        for i in range(150):
            keyboard.block_key(i)
            self.blocked_keys.add(i)
        self.send_notification_in_thread()

    def unlock_keyboard(self, event=None):
        for key in self.blocked_keys:
            keyboard.unblock_key(key)
        self.blocked_keys.clear()

        # Manually release the hotkey keys to ensure they're not stuck
        keyboard.release(self.hotkey)
        print(f"Keyboard Unlocked {self.hotkey}")

        self.root.destroy()

    def show_overlay(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', self.opacity)
        self.root.bind('<Button-1>', self.unlock_keyboard)
        # message = tk.Label(self.root, text="", bg='black', fg='white', font=("Arial", 24))
        # message.pack(expand=True)

        self.lock_keyboard()
        self.root.mainloop()

    def send_hotkey_signal(self):
        self.show_overlay_queue.put(True)

    def send_change_hotkey_signal(self):
        self.show_change_hotkey_queue.put(True)

    def start_hotkey_listener_thread(self):
        with self.hotkey_lock:
            self.listen_for_hotkey = True
            if self.hotkey_thread and threading.current_thread() is not self.hotkey_thread and self.hotkey_thread.is_alive():
                self.hotkey_thread.join()
            self.hotkey_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
            self.hotkey_thread.start()

    def hotkey_listener(self):
        keyboard.add_hotkey(self.hotkey, self.send_hotkey_signal)
        while self.listen_for_hotkey:
            time.sleep(1)
        keyboard.remove_hotkey(self.hotkey)

    def create_tray_icon(self):
        image = Image.open("../resources/img/icon.png")
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill="white")
        menu = Menu(
            MenuItem("About", open_about),
            MenuItem("Change Hotkey", self.send_change_hotkey_signal),
            MenuItem(
                "Enable/Disable Notifications",
                self.toggle_notifications,
                checked=lambda item: self.notifications_enabled,  # Display current status
            ),
            MenuItem("Set Opacity", Menu(
                MenuItem("5%", lambda: self.set_opacity(0.05)),
                MenuItem("10%", lambda: self.set_opacity(0.1)),
                MenuItem("30%", lambda: self.set_opacity(0.3)),
                MenuItem("50%", lambda: self.set_opacity(0.5)),
                MenuItem("70%", lambda: self.set_opacity(0.7)),
                MenuItem("90%", lambda: self.set_opacity(0.9)),
            )),
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
        while self.program_running:
            if not self.show_overlay_queue.empty():
                print(self.show_overlay_queue.get(block=False))
                self.show_overlay()
            elif not self.show_change_hotkey_queue.empty():
                self.show_change_hotkey_queue.get(block=False)
                self.change_hotkey()
            time.sleep(.1)
