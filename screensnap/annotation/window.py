"""
Annotation Studio Window with Undo, Redo, Reset, and Tool Palette.
"""

import os
import math
import tkinter as tk
from tkinter import ttk, colorchooser, simpledialog, messagebox, filedialog
from PIL import Image, ImageTk
from screensnap.config import THEME, FONT_FAMILY, FONT_MONO
from screensnap.annotation.engine import (
    draw_arrow, draw_rectangle, draw_circle, draw_highlight,
    apply_blur_pixelation, draw_text_label
)


class AnnotatorWindow(tk.Toplevel):
    def __init__(self, parent, image_path: str, on_save_callback=None):
        super().__init__(parent)
        self.title(f"ScreenSnap - Annotator: {os.path.basename(image_path)}")
        self.geometry("1140x840")
        self.minsize(920, 640)
        self.image_path = image_path
        self.on_save_callback = on_save_callback

        self.configure(bg=THEME["bg_base"])

        # Tool states
        self.current_tool = "arrow"
        self.current_color = THEME["cyan_electric"]
        self.current_thickness = 4

        # Image & History Stack
        self.original_image = None
        self.base_image = None
        self.display_image_ref = None
        self.scale_factor = 1.0
        self.img_offset_x = 0
        self.img_offset_y = 0

        self.undo_stack = []
        self.redo_stack = []
        self.max_undo = 50

        self.start_x = 0
        self.start_y = 0
        self.temp_canvas_item = None

        self._build_ui()
        self._bind_events()
        self._load_image()

    def _build_ui(self):
        # Main Toolbar
        toolbar = tk.Frame(self, bg=THEME["bg_surface"], height=62)
        toolbar.pack(fill=tk.X, side=tk.TOP, padx=16, pady=(16, 8))
        toolbar.pack_propagate(False)

        # Tool buttons
        tk.Label(toolbar, text="TOOL", font=(FONT_MONO, 8, "bold"), fg=THEME["cyan_electric"], bg=THEME["bg_surface"]).pack(side=tk.LEFT, padx=(16, 8), pady=16)

        self.tool_btns = {}
        tool_items = [
            ("arrow", "Arrow"),
            ("rectangle", "Rectangle"),
            ("circle", "Circle"),
            ("text", "Text"),
            ("highlight", "Highlight"),
            ("blur", "Blur")
        ]

        for tid, tname in tool_items:
            is_active = (tid == self.current_tool)
            btn = tk.Button(
                toolbar,
                text=tname,
                font=(FONT_FAMILY, 9, "bold" if is_active else "normal"),
                fg=THEME["text_hero"] if is_active else THEME["text_secondary"],
                bg=THEME["cyan_dim"] if is_active else THEME["bg_surface_alt"],
                activebackground=THEME["cyan_hover"],
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                padx=10,
                pady=5,
                command=lambda t=tid: self.set_tool(t)
            )
            btn.pack(side=tk.LEFT, padx=3, pady=12)
            self.tool_btns[tid] = btn

        tk.Frame(toolbar, bg=THEME["border_subtle"], width=1, height=28).pack(side=tk.LEFT, padx=10, pady=16)

        # Line thickness
        tk.Label(toolbar, text="LINE", font=(FONT_MONO, 8, "bold"), fg=THEME["amber_electric"], bg=THEME["bg_surface"]).pack(side=tk.LEFT, padx=(4, 6), pady=16)
        self.thick_btns = {}
        for th in [2, 4, 6, 8, 12]:
            is_act = (th == self.current_thickness)
            btn = tk.Button(
                toolbar,
                text=f"{th}px",
                font=(FONT_MONO, 8, "bold" if is_act else "normal"),
                fg=THEME["text_hero"] if is_act else THEME["text_secondary"],
                bg=THEME["amber_dim"] if is_act else THEME["bg_surface_alt"],
                activebackground=THEME["amber_hover"],
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                padx=6,
                pady=3,
                command=lambda t=th: self.set_thickness(t)
            )
            btn.pack(side=tk.LEFT, padx=2, pady=14)
            self.thick_btns[th] = btn

        tk.Frame(toolbar, bg=THEME["border_subtle"], width=1, height=28).pack(side=tk.LEFT, padx=10, pady=16)

        # Color palette
        preset_colors = [THEME["cyan_electric"], THEME["amber_electric"], THEME["mint_neon"], THEME["rose_neon"], THEME["purple_electric"], "#FACC15", "#FFFFFF", "#000000"]
        self.c_btns = []
        for col in preset_colors:
            is_sel = (col == self.current_color)
            b = tk.Button(
                toolbar,
                bg=col,
                activebackground=col,
                relief=tk.SOLID if is_sel else tk.FLAT,
                bd=2 if is_sel else 0,
                width=2,
                height=1,
                cursor="hand2",
                command=lambda c=col: self.set_color(c)
            )
            b.pack(side=tk.LEFT, padx=2, pady=18)
            self.c_btns.append((col, b))

        tk.Button(
            toolbar, text="Color", font=(FONT_FAMILY, 9), bg=THEME["bg_surface_alt"], fg=THEME["text_primary"],
            relief=tk.FLAT, bd=0, cursor="hand2", padx=8, pady=3, command=self.pick_custom_color
        ).pack(side=tk.LEFT, padx=(3, 10), pady=14)

        # Right Action Buttons
        btn_save = tk.Button(
            toolbar, text="Save Annotated", font=(FONT_FAMILY, 9, "bold"),
            fg=THEME["bg_abyss"], bg=THEME["cyan_electric"], activebackground=THEME["cyan_hover"],
            relief=tk.FLAT, bd=0, cursor="hand2", padx=16, pady=6, command=self.save_annotated
        )
        btn_save.pack(side=tk.RIGHT, padx=(4, 16), pady=12)

        self.btn_reset = tk.Button(
            toolbar, text="Reset", font=(FONT_FAMILY, 8, "bold"),
            fg=THEME["rose_neon"], bg=THEME["bg_surface_alt"], activebackground=THEME["rose_bg"],
            relief=tk.FLAT, bd=0, cursor="hand2", padx=8, pady=4, command=self.reset_to_original
        )
        self.btn_reset.pack(side=tk.RIGHT, padx=4, pady=14)

        self.btn_redo = tk.Button(
            toolbar, text="Redo Ctrl+Y", font=(FONT_FAMILY, 8, "bold"),
            fg=THEME["text_secondary"], bg=THEME["bg_surface_alt"], activebackground=THEME["bg_surface_hover"],
            relief=tk.FLAT, bd=0, cursor="hand2", padx=10, pady=4, command=self.redo
        )
        self.btn_redo.pack(side=tk.RIGHT, padx=4, pady=14)

        self.btn_undo = tk.Button(
            toolbar, text="Undo Ctrl+Z", font=(FONT_FAMILY, 8, "bold"),
            fg=THEME["text_hero"], bg=THEME["bg_surface_alt"], activebackground=THEME["bg_surface_hover"],
            relief=tk.FLAT, bd=0, cursor="hand2", padx=10, pady=4, command=self.undo
        )
        self.btn_undo.pack(side=tk.RIGHT, padx=4, pady=14)

        # Center Canvas
        center = tk.Frame(self, bg=THEME["bg_base"])
        center.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))

        self.canvas_box = tk.Frame(center, bg=THEME["bg_canvas"], bd=1, relief=tk.SOLID)
        self.canvas_box.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_box, bg=THEME["bg_canvas"], highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self._on_resize)

        # Status Bar
        status = tk.Frame(self, bg=THEME["bg_abyss"], height=32)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        status.pack_propagate(False)

        self.status_lbl = tk.Label(
            status, text=f"File: {os.path.basename(self.image_path)}",
            font=(FONT_MONO, 8), fg=THEME["text_muted"], bg=THEME["bg_abyss"]
        )
        self.status_lbl.pack(side=tk.LEFT, padx=16, pady=6)

        self.history_lbl = tk.Label(
            status, text="Undo: 0 | Redo: 0",
            font=(FONT_MONO, 8, "bold"), fg=THEME["cyan_electric"], bg=THEME["bg_abyss"]
        )
        self.history_lbl.pack(side=tk.RIGHT, padx=16, pady=6)

    def _bind_events(self):
        for key in ["<Control-z>", "<Control-Z>", "<Control-Key-z>"]:
            self.bind(key, lambda e: self.undo())
        for key in ["<Control-y>", "<Control-Y>", "<Control-Key-y>", "<Control-Shift-Z>", "<Control-Shift-z>"]:
            self.bind(key, lambda e: self.redo())
        self.bind("<Control-s>", lambda e: self.save_annotated())
        self.bind("<Control-S>", lambda e: self.save_annotated())

        self.canvas.bind("<ButtonPress-1>", self._on_down)
        self.canvas.bind("<B1-Motion>", self._on_move)
        self.canvas.bind("<ButtonRelease-1>", self._on_up)

    def _load_image(self):
        try:
            self.original_image = Image.open(self.image_path).convert("RGB")
            self.base_image = self.original_image.copy()
            self.undo_stack = [self.base_image.copy()]
            self.redo_stack.clear()
            self._update_history_labels()
            self.after(50, self._render)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{e}", parent=self)

    def _push_undo(self, new_img: Image.Image):
        self.base_image = new_img
        self.undo_stack.append(new_img.copy())
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self._update_history_labels()
        self._render()

    def undo(self):
        if len(self.undo_stack) > 1:
            current = self.undo_stack.pop()
            self.redo_stack.append(current)
            self.base_image = self.undo_stack[-1].copy()
            self._update_history_labels()
            self._render()
            self.status_lbl.config(text="Undone last action.", fg=THEME["cyan_electric"])
        else:
            self.status_lbl.config(text="Nothing to undo.", fg=THEME["text_muted"])

    def redo(self):
        if self.redo_stack:
            restored = self.redo_stack.pop()
            self.undo_stack.append(restored)
            self.base_image = restored.copy()
            self._update_history_labels()
            self._render()
            self.status_lbl.config(text="Redone action.", fg=THEME["cyan_electric"])
        else:
            self.status_lbl.config(text="Nothing to redo.", fg=THEME["text_muted"])

    def reset_to_original(self):
        if messagebox.askyesno("Reset Annotations", "Discard all annotations and reset to original image?", parent=self):
            if self.original_image:
                self._push_undo(self.original_image.copy())
                self.status_lbl.config(text="Reset to original image.", fg=THEME["amber_electric"])

    def _update_history_labels(self):
        u_count = max(0, len(self.undo_stack) - 1)
        r_count = len(self.redo_stack)
        self.history_lbl.config(text=f"Undo: {u_count} | Redo: {r_count}")

        self.btn_undo.config(fg=THEME["text_hero"] if u_count > 0 else THEME["text_muted"])
        self.btn_redo.config(fg=THEME["text_hero"] if r_count > 0 else THEME["text_muted"])

    def set_tool(self, tool_id):
        self.current_tool = tool_id
        for tid, btn in self.tool_btns.items():
            is_active = (tid == tool_id)
            btn.config(
                bg=THEME["cyan_dim"] if is_active else THEME["bg_surface_alt"],
                fg=THEME["text_hero"] if is_active else THEME["text_secondary"],
                font=(FONT_FAMILY, 9, "bold" if is_active else "normal")
            )

    def set_thickness(self, th):
        self.current_thickness = th
        for t, btn in self.thick_btns.items():
            is_act = (t == th)
            btn.config(
                bg=THEME["amber_dim"] if is_act else THEME["bg_surface_alt"],
                fg=THEME["text_hero"] if is_act else THEME["text_secondary"],
                font=(FONT_MONO, 8, "bold" if is_act else "normal")
            )

    def set_color(self, hex_col):
        self.current_color = hex_col
        for col, btn in self.c_btns:
            is_sel = (col.upper() == hex_col.upper())
            btn.config(relief=tk.SOLID if is_sel else tk.FLAT, bd=2 if is_sel else 0)

    def pick_custom_color(self):
        col = colorchooser.askcolor(initialcolor=self.current_color, title="Pick Color", parent=self)
        if col and col[1]:
            self.set_color(col[1])

    def _render(self):
        if not self.base_image:
            return
        cw = self.canvas.winfo_width() or 900
        ch = self.canvas.winfo_height() or 560
        iw, ih = self.base_image.size
        scale = min((cw - 32) / iw, (ch - 32) / ih)
        self.scale_factor = scale
        dw, dh = max(1, int(iw * scale)), max(1, int(ih * scale))
        resized = self.base_image.resize((dw, dh), Image.Resampling.LANCZOS)
        self.display_image_ref = ImageTk.PhotoImage(resized)
        self.img_offset_x = (cw - dw) // 2
        self.img_offset_y = (ch - dh) // 2
        self.canvas.delete("all")
        self.canvas.create_image(self.img_offset_x, self.img_offset_y, image=self.display_image_ref, anchor=tk.NW)

    def _on_resize(self, event):
        if self.base_image:
            self._render()

    def _canvas_to_img(self, cx, cy):
        if not self.base_image or self.scale_factor <= 0:
            return 0, 0
        ix = (cx - self.img_offset_x) / self.scale_factor
        iy = (cy - self.img_offset_y) / self.scale_factor
        return max(0, min(self.base_image.width, ix)), max(0, min(self.base_image.height, iy))

    def _on_down(self, event):
        if not self.base_image:
            return
        self.start_x, self.start_y = event.x, event.y
        if self.current_tool == "text":
            self._add_text(event.x, event.y)

    def _on_move(self, event):
        if not self.base_image or self.current_tool == "text":
            return
        if self.temp_canvas_item:
            self.canvas.delete(self.temp_canvas_item)
            self.temp_canvas_item = None
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y
        th = max(2, int(self.current_thickness * self.scale_factor))

        if self.current_tool == "arrow":
            self.temp_canvas_item = self.canvas.create_line(x1, y1, x2, y2, fill=self.current_color, width=th, arrow=tk.LAST, arrowshape=(14, 18, 5))
        elif self.current_tool == "rectangle":
            self.temp_canvas_item = self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.current_color, width=th)
        elif self.current_tool == "circle":
            self.temp_canvas_item = self.canvas.create_oval(x1, y1, x2, y2, outline=self.current_color, width=th)
        elif self.current_tool in ("highlight", "blur"):
            self.temp_canvas_item = self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.current_color if self.current_tool == "highlight" else THEME["cyan_electric"], width=2, dash=(4, 4))

    def _on_up(self, event):
        if not self.base_image or self.current_tool == "text":
            return
        if self.temp_canvas_item:
            self.canvas.delete(self.temp_canvas_item)
            self.temp_canvas_item = None

        ix1, iy1 = self._canvas_to_img(self.start_x, self.start_y)
        ix2, iy2 = self._canvas_to_img(event.x, event.y)

        if math.hypot(ix2 - ix1, iy2 - iy1) < 4:
            return

        p1, p2 = (int(ix1), int(iy1)), (int(ix2), int(iy2))
        tool = self.current_tool
        col = self.current_color
        th = self.current_thickness

        if tool == "arrow":
            new_img = draw_arrow(self.base_image, p1, p2, col, th)
        elif tool == "rectangle":
            new_img = draw_rectangle(self.base_image, p1, p2, col, th)
        elif tool == "circle":
            new_img = draw_circle(self.base_image, p1, p2, col, th)
        elif tool == "highlight":
            new_img = draw_highlight(self.base_image, p1, p2, col)
        elif tool == "blur":
            new_img = apply_blur_pixelation(self.base_image, p1, p2)
        else:
            return

        self._push_undo(new_img)
        self.status_lbl.config(text=f"Added {tool.capitalize()}", fg=THEME["mint_neon"])

    def _add_text(self, cx, cy):
        ix, iy = self._canvas_to_img(cx, cy)
        text = simpledialog.askstring("Add Text", "Enter annotation text:", parent=self)
        if not text:
            return

        pos = (int(ix), int(iy))
        new_img = draw_text_label(self.base_image, pos, text, self.current_color, self.current_thickness)
        self._push_undo(new_img)
        self.status_lbl.config(text="Added text label", fg=THEME["mint_neon"])

    def save_annotated(self):
        if not self.base_image:
            return
        orig_dir = os.path.dirname(self.image_path)
        orig_name = os.path.basename(self.image_path)
        base_name, _ = os.path.splitext(orig_name)
        out_name = f"{base_name}_annotated.png" if not base_name.endswith("_annotated") else f"{base_name}.png"

        save_path = filedialog.asksaveasfilename(
            initialdir=orig_dir, initialfile=out_name, defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All files", "*.*")], parent=self
        )
        if save_path:
            try:
                self.base_image.save(save_path)
                messagebox.showinfo("Saved", f"Annotated image saved:\n{save_path}", parent=self)
                if self.on_save_callback:
                    self.on_save_callback()
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{e}", parent=self)