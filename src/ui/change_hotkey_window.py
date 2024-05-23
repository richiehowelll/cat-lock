import threading
import time
import tkinter as tk
from queue import Queue

import keyboard


class ChangeHotkeyWindow:
    def __init__(self, main):
        self.main = main

    def open(self):
        self.main.listen_for_hotkey = False
        if self.main.hotkey_thread.is_alive():
            self.main.hotkey_thread.join()

        with self.main.hotkey_lock:
            self.main.changing_hotkey_queue.put(True)
            hotkey_window = tk.Tk()
            hotkey_window.title("Set Hotkey")
            hotkey_window.geometry("300x150")
            hotkey_window.attributes('-topmost', True)

            def on_closing():
                hotkey_window.destroy()
                self.main.changing_hotkey_queue.get(block=False)
                self.main.start_hotkey_listener()

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
                        if keys_pressed == 'backspace':
                            entry = hotkey_entry.get()
                            if '+' in entry:
                                new_text = entry[:entry.rfind('+')]
                            else:
                                new_text = ''
                            hotkey_entry.delete(0, 'end')
                            hotkey_entry.insert(tk.END, new_text)
                        else:
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
                    self.main.set_hotkey(new_hotkey)
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