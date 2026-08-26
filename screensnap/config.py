"""
Application configuration, theme tokens, and typography constants.
"""

import os
import platform

# Base Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "Screenshots")
HISTORY_FILE = os.path.join(BASE_DIR, ".shared_history.json")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Theme Palette (Cyber Obsidian / Electric Cyan & Amber)
THEME = {
    # Surfaces
    "bg_abyss": "#08090E",
    "bg_base": "#0E1017",
    "bg_surface": "#151824",
    "bg_surface_alt": "#1C2132",
    "bg_surface_hover": "#252B42",
    "bg_canvas": "#0A0B10",
    
    # Borders
    "border_subtle": "#1F2438",
    "border_medium": "#2D3450",
    "border_glow": "#00F0FF",
    
    # Accents
    "cyan_electric": "#00E5FF",
    "cyan_hover": "#00B4D8",
    "cyan_dim": "#004753",
    "amber_electric": "#FF9F1C",
    "amber_hover": "#F77F00",
    "amber_dim": "#4D2D00",
    "mint_neon": "#10B981",
    "mint_bg": "#064E3B",
    "mint_text": "#6EE7B7",
    "rose_neon": "#FF2A6D",
    "rose_bg": "#4C0519",
    "purple_electric": "#A855F7",
    
    # Typography
    "text_hero": "#FFFFFF",
    "text_primary": "#F1F5F9",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "text_subtle": "#475569"
}

# Typography
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"

FONT_FAMILY = "Segoe UI" if IS_WINDOWS else ("SF Pro Display" if IS_MAC else "Helvetica")
FONT_MONO = "Cascadia Code" if IS_WINDOWS else ("Menlo" if IS_MAC else "Courier New")