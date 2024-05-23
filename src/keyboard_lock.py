import threading
import time
import tkinter as tk
from queue import Queue

import keyboard

from src.config import Config
from src.notifications import send_notification_in_thread
from src.tray_icon import TrayIcon


class KeyboardLock:
    def __init__(self):
        self.blocked_keys = set()
        self.program_running = True
        self.listen_for_hotkey = True
        self.hotkey_lock = threading.Lock()
        self.hotkey_thread = None
        self.tray_icon_thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        self.root = None
        self.config = Config()
        self.show_overlay_queue = Queue()
        self.show_change_hotkey_queue = Queue()
        self.start_hotkey_listener_thread()
        self.tray_icon_thread.start()

    def create_tray_icon(self):
        TrayIcon(kl=self)

    def set_hotkey(self, new_hotkey):
        self.config.hotkey = new_hotkey
        self.config.save()

    def change_hotkey(self):
        self.listen_for_hotkey = False
        if self.hotkey_thread.is_alive():
            self.hotkey_thread.join()

        with self.hotkey_lock:

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
            hotkey_entry.config(state='readonly')
            entry_queue = Queue()

            def poll_queue():
                while True:
                    if not entry_queue.empty():
                        keys_pressed = entry_queue.get(block=False)
                        hotkey_entry.config(state='normal')
                        hotkey_entry.delete(0, 'end')
                        hotkey_entry.insert(tk.END, keys_pressed)
                        hotkey_entry.config(state='readonly')
                        keyboard.stash_state()
                        start_entry_listener_thread()
                    break
                hotkey_window.after(100, poll_queue)

            def set_hotkey_from_gui():
                new_hotkey = hotkey_entry.get()
                if new_hotkey:
                    self.set_hotkey(new_hotkey)
                    print(f"Key Unlocked {self.config.hotkey}")
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

        entry_listener_thread = None

        def start_entry_listener_thread():
            nonlocal entry_listener_thread
            if entry_listener_thread and entry_listener_thread.is_alive():
                entry_listener_thread.join()
            keyboard.stash_state()
            entry_listener_thread = threading.Thread(target=read_user_inp, daemon=True)
            entry_listener_thread.start()

        start_entry_listener_thread()
        hotkey_window.after(100, poll_queue)
        hotkey_window.mainloop()

    def lock_keyboard(self):
        self.blocked_keys.clear()
        for i in range(150):
            keyboard.block_key(i)
            self.blocked_keys.add(i)
        send_notification_in_thread(self.config.notifications_enabled)

    def unlock_keyboard(self, event=None):
        for key in self.blocked_keys:
            keyboard.unblock_key(key)
        self.blocked_keys.clear()

        # Manually release the hotkey keys to ensure they're not stuck
        keyboard.release(self.config.hotkey)
        print(f"Keyboard Unlocked {self.config.hotkey}")
        if self.root:
            self.root.destroy()

    def show_overlay(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', self.config.opacity)
        self.root.bind('<Button-1>', self.unlock_keyboard)

        self.lock_keyboard()
        self.root.mainloop()

    def send_hotkey_signal(self):
        self.show_overlay_queue.put(True)

    def send_change_hotkey_signal(self):
        self.show_change_hotkey_queue.put(True)

    def start_hotkey_listener_thread(self):
        keyboard.stash_state()
        with self.hotkey_lock:
            self.listen_for_hotkey = True
            if self.hotkey_thread and threading.current_thread() is not self.hotkey_thread and self.hotkey_thread.is_alive():
                self.hotkey_thread.join()
            self.hotkey_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
            self.hotkey_thread.start()

    def hotkey_listener(self):
        keyboard.add_hotkey(self.config.hotkey, self.send_hotkey_signal)
        while self.listen_for_hotkey:
            time.sleep(1)
        keyboard.remove_hotkey(self.config.hotkey)

    def quit_program(self, icon, item):
        self.program_running = False
        self.unlock_keyboard()
        icon.stop()
        print("Program Exiting")

    def start(self):
        print("Program Starting")
        while self.program_running:
            if not self.show_overlay_queue.empty():
                self.show_overlay_queue.get(block=False)
                self.show_overlay()
            elif not self.show_change_hotkey_queue.empty():
                self.show_change_hotkey_queue.get(block=False)
                self.change_hotkey()
            time.sleep(.1)
