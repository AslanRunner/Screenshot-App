"""
Screen capture engine using MSS and Pillow.
"""

import os
import datetime
from PIL import Image
import mss
from screensnap.config import SCREENSHOTS_DIR


def capture_fullscreen() -> tuple[Image.Image, str]:
    """Captures primary monitor and saves to Screenshots directory."""
    with mss.mss() as sct:
        mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
        sct_img = sct.grab(mon)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fpath = os.path.join(SCREENSHOTS_DIR, f"screenshot_{now_str}.png")
        img.save(fpath, format="PNG")
        return img, fpath


def capture_all_monitors_image() -> tuple[Image.Image, dict]:
    """Captures all monitors bounding box without saving to disk (used by Snipping Tool)."""
    with mss.mss() as sct:
        # Monitor 0 represents all monitors combined
        mon = sct.monitors[0]
        sct_img = sct.grab(mon)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img, mon


def save_cropped_region(full_img: Image.Image, box: tuple[int, int, int, int]) -> tuple[Image.Image, str]:
    """Crops full image to box (left, top, right, bottom) and saves to Screenshots."""
    cropped = full_img.crop(box)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fpath = os.path.join(SCREENSHOTS_DIR, f"screenshot_{now_str}.png")
    cropped.save(fpath, format="PNG")
    return cropped, fpath