"""
ScreenSnap Studio — Entry Point
"""

import sys
import os
import tkinter as tk

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from screensnap.app import ScreenSnapApp


def main():
    root = tk.Tk()
    app = ScreenSnapApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()