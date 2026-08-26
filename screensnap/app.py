"""
Main Application Controller for ScreenSnap Studio.
Integrates Gallery, Global Hotkeys, Capture Engine, Snipping Tool and Cloud Sharing.
"""

import os
import subprocess
import tkinter as tk
from tkinter import messagebox

from screensnap.config import THEME, FONT_FAMILY, FONT_MONO, SCREENSHOTS_DIR, IS_WINDOWS, IS_MAC
from screensnap.cloud.uploader import CloudUploader
from screensnap.capture.engine import capture_fullscreen
from screensnap.capture.snipping import SnippingOverlay
from screensnap.capture.hotkeys import GlobalHotkeyManager
from screensnap.ui.gallery import GalleryView


class ScreenSnapApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ScreenSnap - Desktop Capture and Cloud Share")
        self.root.geometry("1140x780")
        self.root.minsize(920, 620)
        self.root.configure(bg=THEME["bg_base"])

        self.uploader = CloudUploader()

        self._build_ui()
        self._init_hotkeys()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.refresh()

    def _build_ui(self):
        # Top Header Bar
        header = tk.Frame(self.root, bg=THEME["bg_surface"], height=72)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        brand_box = tk.Frame(header, bg=THEME["bg_surface"])
        brand_box.pack(side=tk.LEFT, padx=24, pady=12)

        title_row = tk.Frame(brand_box, bg=THEME["bg_surface"])
        title_row.pack(anchor="w")

        tk.Label(title_row, text="SCREEN", font=(FONT_FAMILY, 15, "bold"), fg=THEME["text_hero"], bg=THEME["bg_surface"]).pack(side=tk.LEFT)
        tk.Label(title_row, text="SNAP", font=(FONT_FAMILY, 15, "bold"), fg=THEME["cyan_electric"], bg=THEME["bg_surface"]).pack(side=tk.LEFT)

        badge_studio = tk.Label(title_row, text="STUDIO", font=(FONT_MONO, 7, "bold"), fg=THEME["bg_abyss"], bg=THEME["amber_electric"], padx=6, pady=1)
        badge_studio.pack(side=tk.LEFT, padx=(8, 0))

        tk.Label(
            brand_box,
            text="Global Hotkeys: F1 Fullscreen | F2 Drag to Snip Region",
            font=(FONT_FAMILY, 8), fg=THEME["text_secondary"], bg=THEME["bg_surface"]
        ).pack(anchor="w", pady=(2, 0))

        # Top Action Buttons
        btn_box = tk.Frame(header, bg=THEME["bg_surface"])
        btn_box.pack(side=tk.RIGHT, padx=24, pady=16)

        tk.Button(
            btn_box, text="Fullscreen F1", font=(FONT_FAMILY, 9, "bold"),
            fg=THEME["bg_abyss"], bg=THEME["cyan_electric"], activebackground=THEME["cyan_hover"],
            relief=tk.FLAT, bd=0, cursor="hand2", padx=14, pady=7, command=self.trigger_fullscreen_capture
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_box, text="Snip Region F2", font=(FONT_FAMILY, 9, "bold"),
            fg=THEME["bg_abyss"], bg=THEME["amber_electric"], activebackground=THEME["amber_hover"],
            relief=tk.FLAT, bd=0, cursor="hand2", padx=14, pady=7, command=self.trigger_snipping_tool
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_box, text="Refresh", font=(FONT_FAMILY, 9),
            fg=THEME["text_primary"], bg=THEME["bg_surface_alt"], activebackground=THEME["bg_surface_hover"],
            relief=tk.FLAT, bd=0, cursor="hand2", padx=10, pady=7, command=self.refresh
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_box, text="Open Folder", font=(FONT_FAMILY, 9),
            fg=THEME["text_secondary"], bg=THEME["bg_surface_alt"], activebackground=THEME["bg_surface_hover"],
            relief=tk.FLAT, bd=0, cursor="hand2", padx=10, pady=7, command=self.open_screenshots_folder
        ).pack(side=tk.LEFT, padx=4)

        # Main Gallery Container
        self.gallery = GalleryView(self.root, self.uploader, status_callback=self.update_status)
        self.gallery.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

        # Status Bar
        self.status_bar = tk.Frame(self.root, bg=THEME["bg_abyss"], height=34)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)

        self.status_lbl = tk.Label(
            self.status_bar,
            text="Ready. Press F1 for Fullscreen or F2 for Region Snip.",
            font=(FONT_FAMILY, 9),
            fg=THEME["text_secondary"],
            bg=THEME["bg_abyss"]
        )
        self.status_lbl.pack(side=tk.LEFT, padx=24, pady=6)

        self.stats_lbl = tk.Label(
            self.status_bar,
            text="0 screenshots",
            font=(FONT_MONO, 8, "bold"),
            fg=THEME["cyan_electric"],
            bg=THEME["bg_abyss"]
        )
        self.stats_lbl.pack(side=tk.RIGHT, padx=24, pady=6)

    def _init_hotkeys(self):
        self.hotkey_mgr = GlobalHotkeyManager(
            on_f1_fullscreen=lambda: self.root.after(0, self.trigger_fullscreen_capture),
            on_f2_snipping=lambda: self.root.after(0, self.trigger_snipping_tool)
        )
        self.hotkey_mgr.start()

    def update_status(self, text: str, color: str = None):
        self.status_lbl.config(text=text, fg=color or THEME["text_secondary"])

    def refresh(self):
        count = self.gallery.refresh()
        self.stats_lbl.config(text=f"{count} SCREENSHOTS")

    def trigger_fullscreen_capture(self):
        self.update_status("Capturing fullscreen...", THEME["cyan_electric"])
        self.root.withdraw()
        self.root.after(250, self._do_fullscreen_capture)

    def _do_fullscreen_capture(self):
        try:
            img, fpath = capture_fullscreen()
            self.refresh()
            self.update_status(f"Saved: {os.path.basename(fpath)}", THEME["mint_neon"])
        except Exception as e:
            messagebox.showerror("Error", f"Fullscreen capture error:\n{e}")
        finally:
            self.root.deiconify()
            self.root.lift()

    def trigger_snipping_tool(self):
        self.update_status("Drag mouse to select screen region...", THEME["amber_electric"])
        self.root.withdraw()
        self.root.after(250, self._launch_snipping_overlay)

    def _launch_snipping_overlay(self):
        try:
            SnippingOverlay(self.root, on_complete_callback=self._on_snip_completed)
        except Exception as e:
            self.root.deiconify()
            messagebox.showerror("Snipping Error", f"Failed to start snipping tool:\n{e}")

    def _on_snip_completed(self, img, fpath):
        self.root.deiconify()
        self.root.lift()
        self.refresh()
        self.update_status(f"Snip saved: {os.path.basename(fpath)}", THEME["mint_neon"])

    def open_screenshots_folder(self):
        if not os.path.exists(SCREENSHOTS_DIR):
            os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        try:
            if IS_WINDOWS:
                os.startfile(SCREENSHOTS_DIR)
            elif IS_MAC:
                subprocess.Popen(["open", SCREENSHOTS_DIR])
            else:
                subprocess.Popen(["xdg-open", SCREENSHOTS_DIR])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open directory:\n{e}")

    def _on_close(self):
        if hasattr(self, "hotkey_mgr") and self.hotkey_mgr:
            self.hotkey_mgr.stop()
        self.root.destroy()