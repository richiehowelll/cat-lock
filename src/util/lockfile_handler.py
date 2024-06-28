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
            except Exception as e:
                # Process not found. It might have already been terminated.
                pass
    with open(LOCKFILE_PATH, 'w') as f:
        f.write(str(os.getpid()))


def remove_lockfile():
    if os.path.exists(LOCKFILE_PATH):
        os.remove(LOCKFILE_PATH)
