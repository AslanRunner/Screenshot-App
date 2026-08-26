# ScreenSnap Studio — Modular Screenshot, Annotation & Cloud Share Suite

A modular, developer-grade desktop screenshot suite built with **Python**, **Tkinter**, **Pillow**, **mss**, **pynput**, **requests**, and **pyperclip**.

---

## 🚀 Key Improvements & Features

### 1. 🌐 Global Background Hotkeys (Works when Minimized!)
- **`F1` (Fullscreen Grab)**: Takes a fullscreen screenshot anywhere on your system without needing the application window focused.
- **`F2` (Interactive Drag-to-Snip Region)**: Freezes the entire screen, dims the surroundings, and lets you drag a rectangular selection box with live pixel dimensions (`W × H`). Releasing the mouse instantly crops and saves the screenshot. Press `Esc` or right-click to cancel.

### 2. ✏️ Rock-Solid Undo, Redo & Reset in Annotator
- **`↶ Undo (Ctrl+Z)`**: Reverts the last annotation step cleanly across all tools.
- **`↷ Redo (Ctrl+Y)`**: Re-applies undone annotations.
- **`🗑️ Reset to Original`**: 1-click reset to discard all edits and start fresh from the original capture.
- **Live History Counter**: Shows active undo and redo depth in the status bar.
- **Tools Included**: Arrow, Rectangle, Circle, Text (with contrast badge), Highlight, Blur / Pixelation.

### 3. ☁️ Instant Cloud Sharing (`tmpfiles.org`)
- **1-Click & Right-Click Cloud Upload**: Upload any screenshot directly to `tmpfiles.org` (no account/API keys required).
- **Auto Clipboard Copy**: Automatically copies the direct link (`https://tmpfiles.org/dl/...`) to your clipboard.
- **Modal Link Dialog**: Share popup dialog with `📋 Copy Direct Link` and `🌐 Open in Browser`.

### 4. 🧩 Clean Modular Architecture

```
.
├── main.py                   # Main application entry point
├── solution.py               # Compatibility entry point (python solution.py)
├── requirements.txt          # Dependencies
├── README.md                 # Documentation
│
└── screensnap/               # Modular application package
    ├── __init__.py
    ├── config.py             # Theme palette, paths, typography tokens
    ├── app.py                # Main app controller
    │
    ├── capture/              # Screen capture & hotkey subsystem
    │   ├── __init__.py
    │   ├── engine.py         # MSS multi-monitor grabber
    │   ├── snipping.py       # Interactive drag-to-snip overlay
    │   └── hotkeys.py        # Global background hotkey listener (pynput)
    │
    ├── annotation/           # Image editing & drawing subsystem
    │   ├── __init__.py
    │   ├── engine.py         # Pillow primitives (arrow, shapes, text, blur)
    │   └── window.py         # Annotator studio with Undo / Redo / Reset
    │
    ├── cloud/                # Cloud sharing subsystem
    │   ├── __init__.py
    │   └── uploader.py       # tmpfiles.org async uploader & history tracker
    │
    └── ui/                   # UI components
        ├── __init__.py
        ├── gallery.py        # Scrollable gallery & thumbnail cards
        └── share_modal.py    # Cloud share success modal
```

---

## 💻 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python main.py
# or
python solution.py
```

---

## ⌨️ Global Shortcuts

| Shortcut | Context | Action |
| --- | --- | --- |
| `F1` | **Global (Background)** | Instant Fullscreen Screenshot |
| `F2` | **Global (Background)** | Interactive Drag-to-Snip Region Overlay |
| `Esc` | During Snipping | Cancel Snipping Tool |
| `Ctrl + Z` | Annotator Window | Undo Annotation |
| `Ctrl + Y` | Annotator Window | Redo Annotation |
| `Ctrl + S` | Annotator Window | Save Annotated Image |
| `F5` | Gallery Window | Refresh Screenshots Gallery |