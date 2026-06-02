import ctypes
import os
import sys
from ctypes import wintypes

ERROR_ALREADY_EXISTS = 183
MUTEX_NAME = "Local\\CatLock.SingleInstance"

_mutex_handle = None


def acquire_single_instance_guard():
    """Acquire the app-wide single-instance guard."""
    if os.name != "nt":
        return

    global _mutex_handle
    if _mutex_handle:
        return

    kernel32 = _kernel32()
    handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())

    if ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(handle)
        _show_already_running_message()
        sys.exit(0)

    _mutex_handle = handle


def release_single_instance_guard():
    """Release the single-instance guard held by this process."""
    global _mutex_handle
    if not _mutex_handle or os.name != "nt":
        return

    kernel32 = _kernel32()
    kernel32.CloseHandle(_mutex_handle)
    _mutex_handle = None


def _kernel32():
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.argtypes = [
        wintypes.LPVOID,
        wintypes.BOOL,
        wintypes.LPCWSTR,
    ]
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    return kernel32


def _show_already_running_message() -> None:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.MessageBoxW.argtypes = [
        wintypes.HWND,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        wintypes.UINT,
    ]
    user32.MessageBoxW.restype = ctypes.c_int
    user32.MessageBoxW(
        None,
        "CatLock is already running.",
        "CatLock",
        0x00000040, # Displays OK button + Information Icon
    )
