import os
import signal
from pathlib import Path

home = str(Path.home())
LOCKFILE_PATH = os.path.join(home, '.catlock', 'lockfile.lock')


def check_lockfile():
    if os.path.exists(LOCKFILE_PATH):
        with open(LOCKFILE_PATH, 'r') as f:
            pid = int(f.read().strip())
            try:
                os.kill(pid, signal.SIGTERM)  # Kill the old process
                print(f"Killed process {pid}")
            except Exception as e:
                print(f"Process {pid} not found. It might have already been terminated.")
    with open(LOCKFILE_PATH, 'w') as f:
        f.write(str(os.getpid()))
    print(f"Current PID {os.getpid()} written to lockfile")


def remove_lockfile():
    if os.path.exists(LOCKFILE_PATH):
        os.remove(LOCKFILE_PATH)
    print("Lockfile removed")
