"""
Background Global Hotkeys Listener (F1 Fullscreen, F2 Drag-to-Snip Region).
Works even when application window is minimized or out of focus.
"""

import threading
from pynput import keyboard


class GlobalHotkeyManager:
    def __init__(self, on_f1_fullscreen=None, on_f2_snipping=None):
        self.on_f1_fullscreen = on_f1_fullscreen
        self.on_f2_snipping = on_f2_snipping
        self.listener = None

    def start(self):
        """Starts background listener in non-blocking thread."""
        try:
            hotkeys = {}
            if self.on_f1_fullscreen:
                hotkeys["<f1>"] = self._handle_f1
            if self.on_f2_snipping:
                hotkeys["<f2>"] = self._handle_f2

            self.listener = keyboard.GlobalHotKeys(hotkeys)
            self.listener.start()
        except Exception as e:
            print(f"[Warning] Global hotkey initialization error: {e}")

    def stop(self):
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass

    def _handle_f1(self):
        if self.on_f1_fullscreen:
            self.on_f1_fullscreen()

    def _handle_f2(self):
        if self.on_f2_snipping:
            self.on_f2_snipping()