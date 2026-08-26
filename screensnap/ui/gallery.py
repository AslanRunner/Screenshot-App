"""
Gallery and Screenshot Card UI components.
"""

import os
import datetime
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pyperclip

from screensnap.config import THEME, FONT_FAMILY, FONT_MONO, SCREENSHOTS_DIR, IS_WINDOWS, IS_MAC
from screensnap.cloud.uploader import CloudUploader
from screensnap.ui.share_modal import ShareSuccessModal
from screensnap.annotation.window import AnnotatorWindow


class GalleryView(tk.Frame):
    def __init__(self, parent, uploader: CloudUploader, status_callback=None):
        super().__init__(parent, bg=THEME["bg_base"])
        self.uploader = uploader
        self.status_callback = status_callback
        self.thumbnail_cache = {}
        self.selected_item = None

        self._build_ui()
        self._setup_context_menu()

    def _build_ui(self):
        self.canvas = tk.Canvas(self, bg=THEME["bg_base"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.gallery_frame = tk.Frame(self.canvas, bg=THEME["bg_base"])

        self.gallery_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.gallery_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if IS_MAC:
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _setup_context_menu(self):
        self.context_menu = tk.Menu(
            self, tearoff=0, bg=THEME["bg_surface"], fg=THEME["text_primary"],
            activebackground=THEME["cyan_dim"], activeforeground=THEME["cyan_electric"]
        )
        self.context_menu.add_command(label="🚀 Share Online (Upload to Cloud)", command=self._ctx_share_online)
        self.context_menu.add_command(label="✏️ Annotate & Draw", command=self._ctx_open_annotator)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔗 Copy Direct Cloud Link", command=self._ctx_copy_link)
        self.context_menu.add_command(label="📋 Copy Local Path", command=self._ctx_copy_path)
        self.context_menu.add_command(label="👁️ Open with Default App", command=self._ctx_open_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Delete Screenshot", command=self._ctx_delete_file)

    def refresh(self):
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()

        if not os.path.exists(SCREENSHOTS_DIR):
            os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

        valid_exts = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
        files = []
        try:
            for fname in os.listdir(SCREENSHOTS_DIR):
                ext = os.path.splitext(fname)[1].lower()
                if ext in valid_exts:
                    fpath = os.path.join(SCREENSHOTS_DIR, fname)
                    mtime = os.path.getmtime(fpath)
                    files.append((fpath, mtime))
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"Error reading folder: {e}", THEME["rose_neon"])
            return 0

        files.sort(key=lambda x: x[1], reverse=True)

        if not files:
            empty_box = tk.Frame(self.gallery_frame, bg=THEME["bg_base"], pady=80)
            empty_box.pack(fill=tk.BOTH, expand=True)
            tk.Label(
                empty_box,
                text="📂 No screenshots in storage\n\n• Press [F1] for Instant Fullscreen Capture\n• Press [F2] and Drag Mouse to Select Any Screen Region",
                font=(FONT_FAMILY, 12),
                fg=THEME["text_muted"],
                bg=THEME["bg_base"],
                justify=tk.CENTER
            ).pack()
            return 0

        for fpath, mtime in files:
            self._create_screenshot_card(fpath, mtime)

        return len(files)

    def _create_screenshot_card(self, fpath: str, mtime: float):
        fname = os.path.basename(fpath)
        is_shared = self.uploader.is_shared(fpath)

        card = tk.Frame(self.gallery_frame, bg=THEME["bg_surface"], bd=1, relief=tk.SOLID)
        card.pack(fill=tk.X, pady=8, padx=4)

        # Thumbnail
        thumb = self._get_thumbnail(fpath, (150, 95))
        thumb_lbl = tk.Label(card, image=thumb, bg=THEME["bg_canvas"], width=150, height=95, cursor="hand2")
        thumb_lbl.image = thumb
        thumb_lbl.pack(side=tk.LEFT, padx=12, pady=12)
        thumb_lbl.bind("<Double-Button-1>", lambda e, p=fpath: self.open_annotator(p))

        # Metadata column
        info_frame = tk.Frame(card, bg=THEME["bg_surface"])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=12)

        title_row = tk.Frame(info_frame, bg=THEME["bg_surface"])
        title_row.pack(fill=tk.X, anchor="w")

        name_lbl = tk.Label(title_row, text=fname, font=(FONT_MONO, 10, "bold"), fg=THEME["text_hero"], bg=THEME["bg_surface"])
        name_lbl.pack(side=tk.LEFT)

        if is_shared:
            shared_badge = tk.Label(
                title_row, text="⚡ SHARED ONLINE", font=(FONT_MONO, 7, "bold"),
                fg=THEME["mint_text"], bg=THEME["mint_bg"], padx=8, pady=2
            )
            shared_badge.pack(side=tk.LEFT, padx=12)

        size_bytes = os.path.getsize(fpath)
        size_kb = size_bytes / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
        dt_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")

        meta_lbl = tk.Label(
            info_frame, text=f"📅 {dt_str}   •   💾 {size_str}   •   PNG",
            font=(FONT_FAMILY, 8), fg=THEME["text_muted"], bg=THEME["bg_surface"]
        )
        meta_lbl.pack(anchor="w", pady=(6, 8))

        if is_shared:
            link_url = self.uploader.get_shared_url(fpath)
            link_box = tk.Frame(info_frame, bg=THEME["bg_surface_alt"], padx=8, pady=3)
            link_box.pack(anchor="w")

            link_txt = tk.Label(link_box, text=f"🔗 {link_url}", font=(FONT_MONO, 8),
                                fg=THEME["cyan_electric"], bg=THEME["bg_surface_alt"], cursor="hand2")
            link_txt.pack(side=tk.LEFT)
            link_txt.bind("<Button-1>", lambda e, url=link_url: self._copy_and_notify_link(url))

        # Actions column
        actions_col = tk.Frame(card, bg=THEME["bg_surface"])
        actions_col.pack(side=tk.RIGHT, padx=16, pady=12)

        btn_share = tk.Button(
            actions_col,
            text="🚀 Share Online" if not is_shared else "📋 Copy Link",
            font=(FONT_FAMILY, 9, "bold"),
            fg=THEME["bg_abyss"] if not is_shared else THEME["mint_text"],
            bg=THEME["cyan_electric"] if not is_shared else THEME["mint_bg"],
            activebackground=THEME["cyan_hover"],
            relief=tk.FLAT, bd=0, cursor="hand2", padx=12, pady=6,
            command=lambda p=fpath: self.upload_and_share(p) if not is_shared else self._copy_and_notify_link(self.uploader.get_shared_url(p))
        )
        btn_share.pack(fill=tk.X, pady=3)

        btn_edit = tk.Button(
            actions_col, text="✏️ Annotate", font=(FONT_FAMILY, 8, "bold"),
            fg=THEME["text_primary"], bg=THEME["bg_surface_alt"], activebackground=THEME["bg_surface_hover"],
            relief=tk.FLAT, bd=0, cursor="hand2", padx=12, pady=4,
            command=lambda p=fpath: self.open_annotator(p)
        )
        btn_edit.pack(fill=tk.X, pady=3)

        def _popup_menu(event, path=fpath):
            self.selected_item = path
            self.context_menu.tk_popup(event.x_root, event.y_root)

        for w in [card, thumb_lbl, info_frame, name_lbl, meta_lbl]:
            w.bind("<Button-3>", _popup_menu)
            w.bind("<Button-2>", _popup_menu)

    def _get_thumbnail(self, fpath: str, size=(150, 95)):
        mtime = os.path.getmtime(fpath)
        cache_key = f"{fpath}_{mtime}"
        if cache_key in self.thumbnail_cache:
            return self.thumbnail_cache[cache_key]

        try:
            with Image.open(fpath) as img:
                img_copy = img.copy()
                img_copy.thumbnail(size, Image.Resampling.LANCZOS)
                thumb_img = Image.new("RGB", size, (10, 11, 16))
                offset_x = (size[0] - img_copy.width) // 2
                offset_y = (size[1] - img_copy.height) // 2
                thumb_img.paste(img_copy, (offset_x, offset_y))
                tk_thumb = ImageTk.PhotoImage(thumb_img)
                self.thumbnail_cache[cache_key] = tk_thumb
                return tk_thumb
        except Exception:
            fallback = Image.new("RGB", size, (21, 24, 36))
            tk_thumb = ImageTk.PhotoImage(fallback)
            return tk_thumb

    def upload_and_share(self, fpath: str):
        fname = os.path.basename(fpath)
        if self.status_callback:
            self.status_callback(f"⚡ Uploading '{fname}' to cloud...", THEME["cyan_electric"])

        def _worker():
            try:
                url = self.uploader.upload_file(fpath)
                self.after(0, lambda: self._on_upload_success(fpath, url))
            except Exception as e:
                self.after(0, lambda: self._on_upload_error(str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_upload_success(self, fpath: str, url: str):
        if self.status_callback:
            self.status_callback("✓ Upload complete! Link copied to clipboard.", THEME["mint_neon"])
        self.refresh()
        ShareSuccessModal(self.winfo_toplevel(), fpath, url)

    def _on_upload_error(self, err: str):
        if self.status_callback:
            self.status_callback(f"Upload failed: {err}", THEME["rose_neon"])
        messagebox.showerror("Upload Error", f"Cloud upload failed:\n\n{err}")

    def _copy_and_notify_link(self, url: str):
        pyperclip.copy(url)
        if self.status_callback:
            self.status_callback(f"✓ Copied: {url}", THEME["mint_neon"])

    def open_annotator(self, fpath: str):
        AnnotatorWindow(self.winfo_toplevel(), fpath, on_save_callback=self.refresh)

    def _ctx_share_online(self):
        if self.selected_item:
            self.upload_and_share(self.selected_item)

    def _ctx_open_annotator(self):
        if self.selected_item:
            self.open_annotator(self.selected_item)

    def _ctx_copy_link(self):
        if self.selected_item and self.uploader.is_shared(self.selected_item):
            self._copy_and_notify_link(self.uploader.get_shared_url(self.selected_item))
        else:
            messagebox.showinfo("Not Shared", "Please upload this screenshot first.")

    def _ctx_copy_path(self):
        if self.selected_item:
            pyperclip.copy(self.selected_item)
            if self.status_callback:
                self.status_callback("✓ Local path copied to clipboard!", THEME["cyan_electric"])

    def _ctx_open_file(self):
        if self.selected_item and os.path.exists(self.selected_item):
            if IS_WINDOWS:
                os.startfile(self.selected_item)
            elif IS_MAC:
                subprocess.Popen(["open", self.selected_item])
            else:
                subprocess.Popen(["xdg-open", self.selected_item])

    def _ctx_delete_file(self):
        if self.selected_item and os.path.exists(self.selected_item):
            fname = os.path.basename(self.selected_item)
            if messagebox.askyesno("Delete", f"Delete '{fname}' permanently?"):
                try:
                    os.remove(self.selected_item)
                    self.uploader.delete_history_entry(self.selected_item)
                    self.refresh()
                    if self.status_callback:
                        self.status_callback(f"Deleted {fname}", THEME["text_muted"])
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete file:\n{e}")