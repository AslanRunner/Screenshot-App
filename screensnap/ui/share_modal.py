"""
Cloud share success modal dialog.
"""

import os
import webbrowser
import tkinter as tk
import pyperclip
from screensnap.config import THEME, FONT_FAMILY, FONT_MONO


class ShareSuccessModal(tk.Toplevel):
    def __init__(self, parent, fpath: str, url: str):
        super().__init__(parent)
        self.title("Screenshot Shared")
        self.geometry("560x280")
        self.resizable(False, False)
        self.configure(bg=THEME["bg_surface"])
        self.transient(parent)
        self.grab_set()

        # Success Title
        tk.Label(
            self, text="⚡ SCREENSHOT SHARED ONLINE",
            font=(FONT_FAMILY, 13, "bold"), fg=THEME["cyan_electric"], bg=THEME["bg_surface"]
        ).pack(pady=(24, 4))

        tk.Label(
            self, text=f"File: {os.path.basename(fpath)}   •   Expires in 1 hour (tmpfiles.org)",
            font=(FONT_FAMILY, 8), fg=THEME["text_muted"], bg=THEME["bg_surface"]
        ).pack(pady=(0, 16))

        # Direct Link Container
        url_box = tk.Frame(self, bg=THEME["bg_surface_alt"], padx=12, pady=10, bd=1, relief=tk.SOLID)
        url_box.pack(fill=tk.X, padx=24, pady=(0, 18))

        url_entry = tk.Entry(
            url_box, font=(FONT_MONO, 9), fg=THEME["cyan_electric"],
            bg=THEME["bg_surface_alt"], relief=tk.FLAT, bd=0
        )
        url_entry.insert(0, url)
        url_entry.configure(state="readonly")
        url_entry.pack(fill=tk.X)

        # Action Buttons
        btn_frame = tk.Frame(self, bg=THEME["bg_surface"])
        btn_frame.pack(pady=4)

        def _copy():
            pyperclip.copy(url)
            btn_copy.config(text="✓ Copied!", bg=THEME["mint_bg"], fg=THEME["mint_text"])

        btn_copy = tk.Button(
            btn_frame, text="📋 Copy Direct Link", font=(FONT_FAMILY, 9, "bold"),
            fg=THEME["bg_abyss"], bg=THEME["cyan_electric"], activebackground=THEME["cyan_hover"],
            relief=tk.FLAT, bd=0, cursor="hand2", padx=16, pady=8, command=_copy
        )
        btn_copy.pack(side=tk.LEFT, padx=6)

        tk.Button(
            btn_frame, text="🌐 Open Browser", font=(FONT_FAMILY, 9),
            fg=THEME["text_primary"], bg=THEME["bg_surface_alt"], activebackground=THEME["bg_surface_hover"],
            relief=tk.FLAT, bd=0, cursor="hand2", padx=14, pady=8, command=lambda: webbrowser.open(url)
        ).pack(side=tk.LEFT, padx=6)

        tk.Button(
            btn_frame, text="Done", font=(FONT_FAMILY, 9),
            fg=THEME["text_muted"], bg=THEME["bg_surface"], relief=tk.FLAT, bd=0,
            cursor="hand2", padx=12, pady=8, command=self.destroy
        ).pack(side=tk.LEFT, padx=6)