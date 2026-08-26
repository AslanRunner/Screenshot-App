"""
Interactive Snipping Tool Overlay.
Freezes desktop, dims surroundings, highlights selected rectangle with live dimensions.
"""

import math
import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
from screensnap.capture.engine import capture_all_monitors_image, save_cropped_region
from screensnap.config import THEME, FONT_MONO


class SnippingOverlay(tk.Toplevel):
    def __init__(self, parent, on_complete_callback=None):
        super().__init__(parent)
        self.on_complete_callback = on_complete_callback

        # Grab frozen screenshot of screen
        self.full_screenshot, self.monitor_info = capture_all_monitors_image()

        # Create dimmed background version for outer overlay
        enhancer = ImageEnhance.Brightness(self.full_screenshot)
        self.dimmed_image = enhancer.enhance(0.45)

        # Setup borderless fullscreen window
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        screen_w = self.monitor_info["width"]
        screen_h = self.monitor_info["height"]
        screen_x = self.monitor_info["left"]
        screen_y = self.monitor_info["top"]

        self.geometry(f"{screen_w}x{screen_h}+{screen_x}+{screen_y}")
        self.configure(cursor="crosshair", bg="#000000")

        # Canvas setup
        self.canvas = tk.Canvas(self, width=screen_w, height=screen_h, highlightthickness=0, bg="#000000")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.dimmed_photo = ImageTk.PhotoImage(self.dimmed_image)
        self.canvas.create_image(0, 0, image=self.dimmed_photo, anchor=tk.NW, tags="dimmed_bg")

        # Instruction HUD
        self.hud = self.canvas.create_text(
            screen_w // 2, 40,
            text="Click and drag to select screen region - Press Esc to cancel",
            font=(FONT_MONO, 11, "bold"),
            fill="#FFFFFF"
        )

        # Drag coordinates
        self.start_x = 0
        self.start_y = 0
        self.active_rect = None
        self.active_crop_photo = None
        self.active_crop_img_id = None
        self.dim_label_id = None

        self._bind_events()
        self.focus_force()

    def _bind_events(self):
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Button-3>", lambda e: self._cancel())
        self.bind("<Button-2>", lambda e: self._cancel())

    def _on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def _on_drag(self, event):
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y

        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        w, h = max_x - min_x, max_y - min_y

        if w < 4 or h < 4:
            return

        box = (min_x, min_y, max_x, max_y)
        cropped_clear = self.full_screenshot.crop(box)
        self.active_crop_photo = ImageTk.PhotoImage(cropped_clear)

        if self.active_crop_img_id:
            self.canvas.delete(self.active_crop_img_id)
        self.active_crop_img_id = self.canvas.create_image(min_x, min_y, image=self.active_crop_photo, anchor=tk.NW)

        if self.active_rect:
            self.canvas.delete(self.active_rect)
        self.active_rect = self.canvas.create_rectangle(min_x, min_y, max_x, max_y, outline=THEME["cyan_electric"], width=2)

        if self.dim_label_id:
            self.canvas.delete(self.dim_label_id)
        self.dim_label_id = self.canvas.create_text(
            max_x, max_y + 16,
            text=f"{w} x {h} px",
            font=(FONT_MONO, 9, "bold"),
            fill=THEME["cyan_electric"],
            anchor=tk.E
        )

    def _on_release(self, event):
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y

        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        w, h = max_x - min_x, max_y - min_y

        self.destroy()

        if w > 8 and h > 8:
            box = (min_x, min_y, max_x, max_y)
            cropped_img, fpath = save_cropped_region(self.full_screenshot, box)
            if self.on_complete_callback:
                self.on_complete_callback(cropped_img, fpath)

    def _cancel(self):
        self.destroy()