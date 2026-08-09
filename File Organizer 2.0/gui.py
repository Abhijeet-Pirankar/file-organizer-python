"""
gui.py
------
Main GUI for File Organizer v2.0.
Built with CustomTkinter for a modern, professional look on Windows.

Layout:
  ┌─────────────────────────────────────────────────────────┐
  │  Header (title + version)                               │
  ├─────────────────────────────────────────────────────────┤
  │  Folder Selector (entry + Browse)                       │
  ├─────────────────────────────────────────────────────────┤
  │  Action Bar (Analyze | Preview | Organize | Undo | …)   │
  ├─────────────────────────────────────────────────────────┤
  │  Progress Bar + Status Label                            │
  ├──────────────────────┬──────────────────────────────────┤
  │  Preview Panel       │  Statistics Dashboard            │
  │  (scrollable list)   │  (stat cards + bar chart)       │
  └──────────────────────┴──────────────────────────────────┘
"""

import threading
import tkinter as tk
import tkinter.messagebox as msgbox
from pathlib import Path
from tkinter import filedialog
from typing import Optional

import customtkinter as ctk

import categories as cat_module
import config_manager
import organizer as org_module
import undo_manager as undo_module
from duplicate_detector import DuplicateInfo
from file_monitor import WATCHDOG_AVAILABLE, FolderMonitor
from organizer import DuplicateAction, FilePreview


# ── Theme & palette ───────────────────────────────────────────────────────────

PALETTE = {
    "bg":          "#0f1117",
    "surface":     "#1a1d27",
    "surface2":    "#22263a",
    "accent":      "#4f8ef7",
    "accent_hover":"#3a7ae0",
    "success":     "#27c96b",
    "warning":     "#f5a623",
    "danger":      "#e05252",
    "text":        "#e8eaf0",
    "text_dim":    "#8a8fa8",
    "border":      "#2d3148",
    "card_images": "#4f8ef7",
    "card_pdfs":   "#e05252",
    "card_videos": "#9b59b6",
    "card_docs":   "#27c96b",
    "card_music":  "#f5a623",
    "card_archives":"#1abc9c",
    "card_programs":"#e67e22",
    "card_code":   "#3498db",
    "card_others": "#7f8c8d",
}

CATEGORY_COLORS = {
    "Images":   PALETTE["card_images"],
    "PDFs":     PALETTE["card_pdfs"],
    "Videos":   PALETTE["card_videos"],
    "Docs":     PALETTE["card_docs"],
    "Music":    PALETTE["card_music"],
    "Archives": PALETTE["card_archives"],
    "Programs": PALETTE["card_programs"],
    "Code":     PALETTE["card_code"],
    "Others":   PALETTE["card_others"],
}

CATEGORY_ICONS = {
    "Images":   "🖼",
    "PDFs":     "📄",
    "Videos":   "🎬",
    "Docs":     "📝",
    "Music":    "🎵",
    "Archives": "🗜",
    "Programs": "⚙",
    "Code":     "💻",
    "Others":   "📦",
}


# ── Helper widgets ────────────────────────────────────────────────────────────

def _make_stat_card(parent, label: str, value: str, color: str) -> ctk.CTkFrame:
    """Compact colored stat card widget."""
    frame = ctk.CTkFrame(parent, fg_color=PALETTE["surface2"],
                         corner_radius=10, border_width=2,
                         border_color=color)
    lbl = ctk.CTkLabel(frame, text=label, font=("Segoe UI", 11),
                        text_color=PALETTE["text_dim"])
    lbl.pack(padx=12, pady=(10, 0))
    val = ctk.CTkLabel(frame, text=value, font=("Segoe UI", 22, "bold"),
                        text_color=color)
    val.pack(padx=12, pady=(0, 10))
    frame._val_label = val   # store reference for updates
    return frame


# ── Settings Dialog ───────────────────────────────────────────────────────────

class SettingsDialog(ctk.CTkToplevel):
    """Modal settings window for theme, recursive scan, and custom categories."""

    def __init__(self, parent: "App") -> None:
        super().__init__(parent.root)
        self.parent_app = parent
        self.title("Settings")
        self.geometry("560x620")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["bg"])
        self.grab_set()

        settings = config_manager.load_settings()

        # ── Title ─────────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="⚙  Settings",
                     font=("Segoe UI", 18, "bold"),
                     text_color=PALETTE["text"]).pack(pady=(20, 4))
        ctk.CTkLabel(self, text="Changes are saved automatically.",
                     font=("Segoe UI", 12),
                     text_color=PALETTE["text_dim"]).pack(pady=(0, 16))

        # ── Appearance ────────────────────────────────────────────────────
        section = ctk.CTkFrame(self, fg_color=PALETTE["surface"],
                               corner_radius=12)
        section.pack(fill="x", padx=24, pady=6)
        ctk.CTkLabel(section, text="Appearance",
                     font=("Segoe UI", 13, "bold"),
                     text_color=PALETTE["accent"]).pack(anchor="w", padx=16, pady=(12, 4))

        row = ctk.CTkFrame(section, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkLabel(row, text="Theme:", font=("Segoe UI", 12),
                     text_color=PALETTE["text"]).pack(side="left")
        self.theme_var = ctk.StringVar(value=settings.get("theme", "dark"))
        ctk.CTkOptionMenu(row, values=["dark", "light"], variable=self.theme_var,
                          fg_color=PALETTE["surface2"],
                          button_color=PALETTE["accent"],
                          command=self._on_theme_change).pack(side="right")

        # ── Scan Options ──────────────────────────────────────────────────
        section2 = ctk.CTkFrame(self, fg_color=PALETTE["surface"],
                                corner_radius=12)
        section2.pack(fill="x", padx=24, pady=6)
        ctk.CTkLabel(section2, text="Scan Options",
                     font=("Segoe UI", 13, "bold"),
                     text_color=PALETTE["accent"]).pack(anchor="w", padx=16, pady=(12, 4))

        self.recursive_var = ctk.BooleanVar(value=settings.get("include_subfolders", False))
        ctk.CTkCheckBox(section2, text="Include subfolders (recursive scan)",
                        variable=self.recursive_var,
                        font=("Segoe UI", 12),
                        text_color=PALETTE["text"],
                        fg_color=PALETTE["accent"],
                        hover_color=PALETTE["accent_hover"]).pack(anchor="w", padx=16, pady=(0, 12))

        # ── Custom Categories ─────────────────────────────────────────────
        section3 = ctk.CTkFrame(self, fg_color=PALETTE["surface"],
                                corner_radius=12)
        section3.pack(fill="both", expand=True, padx=24, pady=6)
        ctk.CTkLabel(section3, text="Custom Extensions",
                     font=("Segoe UI", 13, "bold"),
                     text_color=PALETTE["accent"]).pack(anchor="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(section3,
                     text="Add extensions to categories (comma-separated, e.g. .xyz, .abc)",
                     font=("Segoe UI", 11),
                     text_color=PALETTE["text_dim"],
                     wraplength=480,
                     justify="left").pack(anchor="w", padx=16, pady=(0, 8))

        # Category selector
        cat_row = ctk.CTkFrame(section3, fg_color="transparent")
        cat_row.pack(fill="x", padx=16, pady=(0, 6))
        ctk.CTkLabel(cat_row, text="Category:", font=("Segoe UI", 12),
                     text_color=PALETTE["text"]).pack(side="left")
        all_cats = list(cat_module.DEFAULT_CATEGORIES.keys())
        self.cat_var = ctk.StringVar(value=all_cats[0])
        ctk.CTkOptionMenu(cat_row, values=all_cats, variable=self.cat_var,
                          fg_color=PALETTE["surface2"],
                          button_color=PALETTE["accent"]).pack(side="right")

        # Extensions entry
        ext_row = ctk.CTkFrame(section3, fg_color="transparent")
        ext_row.pack(fill="x", padx=16, pady=(0, 6))
        ctk.CTkLabel(ext_row, text="Extensions:", font=("Segoe UI", 12),
                     text_color=PALETTE["text"]).pack(side="left")
        self.ext_entry = ctk.CTkEntry(ext_row, placeholder_text=".xyz, .abc",
                                      fg_color=PALETTE["surface2"],
                                      border_color=PALETTE["border"],
                                      text_color=PALETTE["text"])
        self.ext_entry.pack(side="right", fill="x", expand=True, padx=(8, 0))

        ctk.CTkButton(section3, text="Add Extensions",
                      fg_color=PALETTE["accent"],
                      hover_color=PALETTE["accent_hover"],
                      command=self._add_extensions).pack(padx=16, pady=(0, 8))

        # Display current custom
        self.custom_display = ctk.CTkTextbox(section3, height=80,
                                              fg_color=PALETTE["surface2"],
                                              text_color=PALETTE["text_dim"],
                                              font=("Consolas", 11))
        self.custom_display.pack(fill="x", padx=16, pady=(0, 12))
        self._refresh_custom_display()

        # ── Save button ───────────────────────────────────────────────────
        ctk.CTkButton(self, text="✔  Save & Close",
                      fg_color=PALETTE["success"],
                      hover_color="#1ea855",
                      font=("Segoe UI", 13, "bold"),
                      height=40,
                      command=self._save_and_close).pack(pady=16, padx=24, fill="x")

    def _on_theme_change(self, value: str) -> None:
        ctk.set_appearance_mode(value)

    def _refresh_custom_display(self) -> None:
        custom = config_manager.get("custom_categories", {})
        self.custom_display.configure(state="normal")
        self.custom_display.delete("1.0", "end")
        if custom:
            for cat, exts in custom.items():
                self.custom_display.insert("end", f"{cat}: {', '.join(exts)}\n")
        else:
            self.custom_display.insert("end", "No custom extensions added yet.")
        self.custom_display.configure(state="disabled")

    def _add_extensions(self) -> None:
        cat = self.cat_var.get()
        raw = self.ext_entry.get().strip()
        if not raw:
            return
        exts = [e.strip().lower() for e in raw.split(",") if e.strip()]
        exts = [(e if e.startswith(".") else "." + e) for e in exts]

        custom = config_manager.get("custom_categories", {})
        existing = set(custom.get(cat, []))
        existing.update(exts)
        custom[cat] = sorted(existing)
        config_manager.set_value("custom_categories", custom)

        self.ext_entry.delete(0, "end")
        self._refresh_custom_display()
        msgbox.showinfo("Extensions Added",
                        f"Added {', '.join(exts)} to {cat}.", parent=self)

    def _save_and_close(self) -> None:
        config_manager.set_value("theme", self.theme_var.get())
        config_manager.set_value("include_subfolders", self.recursive_var.get())
        self.parent_app.recursive_var.set(self.recursive_var.get())
        self.destroy()


# ── Duplicate Resolution Dialog ───────────────────────────────────────────────

class DuplicateDialog(ctk.CTkToplevel):
    """
    Shown when a file conflict is detected during organization.
    User chooses Skip / Keep Both / Replace.
    """

    def __init__(self, parent, preview: FilePreview, dup: DuplicateInfo) -> None:
        super().__init__(parent)
        self.title("Duplicate File Detected")
        self.geometry("480x340")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["bg"])
        self.grab_set()
        self.result = DuplicateAction.KEEP_BOTH  # default

        icon = "⚠" if not dup.content_duplicate else "🔁"
        dup_type = "content-identical" if dup.content_duplicate else "same filename"

        ctk.CTkLabel(self, text=f"{icon}  Duplicate Detected",
                     font=("Segoe UI", 17, "bold"),
                     text_color=PALETTE["warning"]).pack(pady=(20, 4))

        ctk.CTkLabel(self,
                     text=f"File:  {preview.filename}",
                     font=("Segoe UI", 12),
                     text_color=PALETTE["text"]).pack(pady=2)
        ctk.CTkLabel(self,
                     text=f"Type:  {dup_type}",
                     font=("Segoe UI", 12),
                     text_color=PALETTE["text_dim"]).pack(pady=2)
        ctk.CTkLabel(self,
                     text=f"Destination:  {preview.destination_path.parent}",
                     font=("Segoe UI", 11),
                     text_color=PALETTE["text_dim"],
                     wraplength=440).pack(pady=(2, 16))

        ctk.CTkLabel(self, text="What would you like to do?",
                     font=("Segoe UI", 13),
                     text_color=PALETTE["text"]).pack(pady=(0, 12))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=4)

        ctk.CTkButton(btn_frame, text="⏭  Skip",
                      fg_color=PALETTE["surface2"],
                      hover_color=PALETTE["border"],
                      text_color=PALETTE["text"],
                      width=130,
                      command=lambda: self._choose(DuplicateAction.SKIP)).grid(
                          row=0, column=0, padx=6)
        ctk.CTkButton(btn_frame, text="📋  Keep Both",
                      fg_color=PALETTE["accent"],
                      hover_color=PALETTE["accent_hover"],
                      width=130,
                      command=lambda: self._choose(DuplicateAction.KEEP_BOTH)).grid(
                          row=0, column=1, padx=6)

        if not dup.content_duplicate:
            ctk.CTkButton(btn_frame, text="♻  Replace",
                          fg_color=PALETTE["danger"],
                          hover_color="#c0392b",
                          width=130,
                          command=self._confirm_replace).grid(
                              row=0, column=2, padx=6)

        ctk.CTkLabel(self,
                     text="Files are never deleted automatically.",
                     font=("Segoe UI", 11),
                     text_color=PALETTE["text_dim"]).pack(pady=(16, 0))

    def _choose(self, action: str) -> None:
        self.result = action
        self.destroy()

    def _confirm_replace(self) -> None:
        if msgbox.askyesno(
            "Confirm Replace",
            "This will overwrite the existing file.\n\nAre you absolutely sure?",
            icon="warning",
            parent=self,
        ):
            self._choose(DuplicateAction.REPLACE)


# ── Bar Chart Canvas ──────────────────────────────────────────────────────────

class BarChart(tk.Canvas):
    """Simple horizontal bar chart drawn with tkinter.Canvas (no matplotlib)."""

    def __init__(self, parent, **kwargs) -> None:
        kwargs.setdefault("bg", PALETTE["surface2"])
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, **kwargs)
        self._data: dict = {}

    def update_data(self, data: dict[str, int]) -> None:
        self._data = data
        self._draw()

    def _draw(self) -> None:
        self.delete("all")
        if not self._data:
            return

        w = self.winfo_width() or 300
        h = self.winfo_height() or 200

        max_val = max(self._data.values(), default=1) or 1
        cats = [c for c, v in self._data.items() if v > 0]
        if not cats:
            return

        bar_h = min(22, (h - 24) // max(len(cats), 1))
        label_w = 80
        pad = 12
        y = pad

        for cat in cats:
            val = self._data[cat]
            color = CATEGORY_COLORS.get(cat, PALETTE["text_dim"])
            bar_max_w = w - label_w - pad * 2 - 36
            bar_w = int(bar_max_w * val / max_val)

            # Label
            self.create_text(
                pad, y + bar_h // 2,
                text=f"{CATEGORY_ICONS.get(cat, '•')} {cat}",
                anchor="w", fill=PALETTE["text_dim"],
                font=("Segoe UI", 9),
            )
            # Bar background
            self.create_rectangle(
                label_w, y, label_w + bar_max_w, y + bar_h,
                fill=PALETTE["border"], outline="",
            )
            # Bar fill
            if bar_w > 0:
                self.create_rectangle(
                    label_w, y, label_w + bar_w, y + bar_h,
                    fill=color, outline="",
                )
            # Value text
            self.create_text(
                label_w + bar_max_w + 6, y + bar_h // 2,
                text=str(val), anchor="w",
                fill=PALETTE["text_dim"],
                font=("Segoe UI", 9),
            )
            y += bar_h + 4


# ── Main Application Window ───────────────────────────────────────────────────

class App:
    """Main application class for File Organizer v2.0."""

    def __init__(self) -> None:
        settings = config_manager.load_settings()

        ctk.set_appearance_mode(settings.get("theme", "dark"))
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Advanced File Organizer v2.0")
        self.root.geometry("1100x760")
        self.root.minsize(900, 640)
        self.root.configure(fg_color=PALETTE["bg"])

        self.undo_mgr = undo_module.UndoManager()
        self.monitor: Optional[FolderMonitor] = None
        self.recursive_var = ctk.BooleanVar(value=settings.get("include_subfolders", False))
        self._organize_thread: Optional[threading.Thread] = None

        self._current_preview: Optional[org_module.PreviewResult] = None

        self._build_ui()
        self._restore_last_folder()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        """Assemble the full UI layout."""
        self._build_header()
        self._build_folder_row()
        self._build_options_row()
        self._build_action_bar()
        self._build_progress_row()
        self._build_main_area()

    def _build_header(self) -> None:
        hdr = ctk.CTkFrame(self.root, fg_color=PALETTE["surface"],
                           corner_radius=0, height=64)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        # Left: logo + title
        left = ctk.CTkFrame(hdr, fg_color="transparent")
        left.pack(side="left", padx=24, pady=8)
        ctk.CTkLabel(left, text="📂", font=("Segoe UI", 28)).pack(side="left", padx=(0, 8))
        title_col = ctk.CTkFrame(left, fg_color="transparent")
        title_col.pack(side="left")
        ctk.CTkLabel(title_col, text="Advanced File Organizer",
                     font=("Segoe UI", 18, "bold"),
                     text_color=PALETTE["text"]).pack(anchor="w")
        ctk.CTkLabel(title_col, text="v2.0 — Smart & Safe File Management",
                     font=("Segoe UI", 11),
                     text_color=PALETTE["text_dim"]).pack(anchor="w")

        # Right: watch indicator
        self.watch_indicator = ctk.CTkLabel(hdr, text="",
                                            font=("Segoe UI", 12),
                                            text_color=PALETTE["success"])
        self.watch_indicator.pack(side="right", padx=24)

    def _build_folder_row(self) -> None:
        row = ctk.CTkFrame(self.root, fg_color=PALETTE["surface"],
                           corner_radius=12)
        row.pack(fill="x", padx=16, pady=(12, 4))

        ctk.CTkLabel(row, text="📁  Folder to Organize:",
                     font=("Segoe UI", 13),
                     text_color=PALETTE["text"]).pack(side="left", padx=(16, 8), pady=12)

        self.folder_entry = ctk.CTkEntry(
            row,
            placeholder_text="Select or type a folder path…",
            fg_color=PALETTE["surface2"],
            border_color=PALETTE["border"],
            text_color=PALETTE["text"],
            font=("Segoe UI", 12),
            height=38,
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=10)

        ctk.CTkButton(
            row, text="Browse",
            fg_color=PALETTE["accent"],
            hover_color=PALETTE["accent_hover"],
            font=("Segoe UI", 12),
            width=90, height=38,
            command=self._browse,
        ).pack(side="right", padx=(0, 16), pady=10)

    def _build_options_row(self) -> None:
        row = ctk.CTkFrame(self.root, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 4))

        ctk.CTkCheckBox(
            row,
            text="Include Subfolders (recursive)",
            variable=self.recursive_var,
            font=("Segoe UI", 12),
            text_color=PALETTE["text_dim"],
            fg_color=PALETTE["accent"],
            hover_color=PALETTE["accent_hover"],
        ).pack(side="left", padx=4)

    def _build_action_bar(self) -> None:
        bar = ctk.CTkFrame(self.root, fg_color=PALETTE["surface"],
                           corner_radius=12)
        bar.pack(fill="x", padx=16, pady=4)

        btn_config = [
            ("🔍  Analyze",   PALETTE["surface2"],  PALETTE["border"],     self._run_analyze),
            ("👁  Preview",   PALETTE["accent"],     PALETTE["accent_hover"], self._run_preview),
            ("⚡  Organize",  PALETTE["success"],    "#1ea855",             self._run_organize),
            ("↩  Undo",       PALETTE["warning"],    "#d4911d",             self._run_undo),
            ("👁‍🗨  Watch",    PALETTE["surface2"],  PALETTE["border"],     self._toggle_watch),
            ("⚙  Settings",  PALETTE["surface2"],  PALETTE["border"],     self._open_settings),
        ]

        for text, fg, hover, cmd in btn_config:
            is_watch = "Watch" in text
            btn = ctk.CTkButton(
                bar,
                text=text,
                fg_color=fg,
                hover_color=hover,
                text_color=PALETTE["text"],
                font=("Segoe UI", 12, "bold"),
                height=40,
                corner_radius=8,
                command=cmd,
            )
            btn.pack(side="left", padx=6, pady=10)
            if is_watch:
                self.watch_btn = btn

    def _build_progress_row(self) -> None:
        row = ctk.CTkFrame(self.root, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(4, 0))

        self.progress_bar = ctk.CTkProgressBar(
            row,
            fg_color=PALETTE["surface2"],
            progress_color=PALETTE["accent"],
            height=8,
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", side="left", expand=True, padx=(0, 12))

        self.status_label = ctk.CTkLabel(
            row, text="Ready",
            font=("Segoe UI", 12),
            text_color=PALETTE["text_dim"],
            width=260,
            anchor="e",
        )
        self.status_label.pack(side="right")

    def _build_main_area(self) -> None:
        """Two-column layout: preview panel (left) + stats dashboard (right)."""
        main = ctk.CTkFrame(self.root, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=16, pady=10)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        self._build_preview_panel(main)
        self._build_stats_panel(main)

    def _build_preview_panel(self, parent) -> None:
        frame = ctk.CTkFrame(parent, fg_color=PALETTE["surface"],
                             corner_radius=12)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Header row
        hdr = ctk.CTkFrame(frame, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(hdr, text="📋  File Preview",
                     font=("Segoe UI", 14, "bold"),
                     text_color=PALETTE["text"]).pack(side="left")
        self.preview_count_label = ctk.CTkLabel(hdr, text="",
                                                 font=("Segoe UI", 11),
                                                 text_color=PALETTE["text_dim"])
        self.preview_count_label.pack(side="right")

        # Column headers
        col_hdr = ctk.CTkFrame(frame, fg_color=PALETTE["surface2"],
                               corner_radius=6)
        col_hdr.pack(fill="x", padx=12, pady=(8, 0))
        for text, w in [("File Name", 220), ("→", 20), ("Category", 100), ("Status", 120)]:
            ctk.CTkLabel(col_hdr, text=text, width=w,
                         font=("Segoe UI", 11, "bold"),
                         text_color=PALETTE["text_dim"],
                         anchor="w").pack(side="left", padx=6, pady=4)

        # Scrollable file list
        self.preview_scroll = ctk.CTkScrollableFrame(
            frame,
            fg_color=PALETTE["surface"],
            scrollbar_button_color=PALETTE["border"],
        )
        self.preview_scroll.pack(fill="both", expand=True, padx=12, pady=(4, 12))

    def _build_stats_panel(self, parent) -> None:
        frame = ctk.CTkFrame(parent, fg_color=PALETTE["surface"],
                             corner_radius=12)
        frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(frame, text="📊  Statistics",
                     font=("Segoe UI", 14, "bold"),
                     text_color=PALETTE["text"]).pack(anchor="w", padx=16, pady=(12, 8))

        # ── Summary stat cards ────────────────────────────────────────────
        cards_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=12, pady=(0, 8))
        cards_frame.columnconfigure((0, 1), weight=1)

        self.card_total = _make_stat_card(cards_frame, "Total Files", "0", PALETTE["text_dim"])
        self.card_total.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        self.card_moved = _make_stat_card(cards_frame, "Organized", "0", PALETTE["success"])
        self.card_moved.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        self.card_dups = _make_stat_card(cards_frame, "Duplicates", "0", PALETTE["warning"])
        self.card_dups.grid(row=1, column=0, padx=4, pady=4, sticky="ew")

        self.card_errors = _make_stat_card(cards_frame, "Errors", "0", PALETTE["danger"])
        self.card_errors.grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        self.card_others = _make_stat_card(cards_frame, "Others", "0", PALETTE["card_others"])
        self.card_others.grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky="ew")

        # ── Bar chart ─────────────────────────────────────────────────────
        ctk.CTkLabel(frame, text="Category Breakdown",
                     font=("Segoe UI", 12, "bold"),
                     text_color=PALETTE["text_dim"]).pack(anchor="w", padx=16, pady=(4, 2))

        chart_frame = ctk.CTkFrame(frame, fg_color=PALETTE["surface2"],
                                   corner_radius=8)
        chart_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.bar_chart = BarChart(chart_frame, bg=PALETTE["surface2"])
        self.bar_chart.pack(fill="both", expand=True, padx=8, pady=8)
        self.bar_chart.bind("<Configure>", lambda e: self.bar_chart._draw())

    # ── Internal state helpers ────────────────────────────────────────────────

    def _get_folder(self) -> Optional[Path]:
        raw = self.folder_entry.get().strip()
        if not raw:
            self._set_status("⚠  Please select a folder first.", PALETTE["warning"])
            return None
        p = Path(raw)
        if not p.is_dir():
            self._set_status("❌  Invalid folder path.", PALETTE["danger"])
            msgbox.showerror("Invalid Path",
                             f"The folder does not exist:\n{raw}")
            return None
        return p

    def _set_status(self, msg: str, color: str = "") -> None:
        color = color or PALETTE["text_dim"]
        self.status_label.configure(text=msg, text_color=color)
        self.root.update_idletasks()

    def _set_progress(self, value: float) -> None:
        """value: 0.0 – 1.0"""
        self.progress_bar.set(value)
        self.root.update_idletasks()

    def _restore_last_folder(self) -> None:
        last = config_manager.get("last_folder", "")
        if last and Path(last).is_dir():
            self.folder_entry.insert(0, last)

    def _clear_preview(self) -> None:
        for widget in self.preview_scroll.winfo_children():
            widget.destroy()
        self.preview_count_label.configure(text="")

    def _update_stat_cards(self, total=0, moved=0, dups=0, errors=0, others=0) -> None:
        self.card_total._val_label.configure(text=str(total))
        self.card_moved._val_label.configure(text=str(moved))
        self.card_dups._val_label.configure(text=str(dups))
        self.card_errors._val_label.configure(text=str(errors))
        self.card_others._val_label.configure(text=str(others))

    # ── Preview list rendering ────────────────────────────────────────────────

    def _render_preview(self, preview: org_module.PreviewResult) -> None:
        self._clear_preview()

        for fp in preview.file_previews:
            row = ctk.CTkFrame(self.preview_scroll,
                               fg_color=PALETTE["surface2"],
                               corner_radius=6)
            row.pack(fill="x", pady=2)

            # File name
            ctk.CTkLabel(row, text=fp.filename, width=220,
                         anchor="w", font=("Segoe UI", 11),
                         text_color=PALETTE["text"]).pack(side="left", padx=(8, 4), pady=5)

            # Arrow
            ctk.CTkLabel(row, text="→", width=20,
                         font=("Segoe UI", 11),
                         text_color=PALETTE["text_dim"]).pack(side="left")

            # Category badge
            cat_color = CATEGORY_COLORS.get(fp.destination_category, PALETTE["text_dim"])
            cat_lbl = ctk.CTkLabel(row,
                                   text=f"{CATEGORY_ICONS.get(fp.destination_category, '•')} {fp.destination_category}",
                                   width=110,
                                   anchor="w",
                                   font=("Segoe UI", 11, "bold"),
                                   text_color=cat_color)
            cat_lbl.pack(side="left", padx=4)

            # Status chip
            if fp.is_content_duplicate:
                chip_text, chip_color = "⊟ Content Dup", PALETTE["warning"]
            elif fp.is_name_conflict:
                chip_text, chip_color = "⚠ Name Conflict", PALETTE["warning"]
            else:
                chip_text, chip_color = "✔ Ready", PALETTE["success"]

            ctk.CTkLabel(row, text=chip_text, width=120,
                         anchor="w",
                         font=("Segoe UI", 11),
                         text_color=chip_color).pack(side="left", padx=4)

        count = len(preview.file_previews)
        self.preview_count_label.configure(text=f"{count} file{'s' if count != 1 else ''}")

    # ── Actions ───────────────────────────────────────────────────────────────

    def _browse(self) -> None:
        folder = filedialog.askdirectory(title="Select Folder to Organize")
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            config_manager.set_value("last_folder", folder)
            self._set_status(f"📁  Selected: {folder}", PALETTE["text_dim"])

    def _run_analyze(self) -> None:
        """Quick stats scan — no file list in preview panel."""
        folder = self._get_folder()
        if folder is None:
            return
        self._set_status("🔍  Analyzing folder…", PALETTE["accent"])
        self._set_progress(0.3)

        def _worker():
            result = org_module.scan_folder(folder, self.recursive_var.get())
            self.root.after(0, lambda: self._on_analyze_done(result))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_analyze_done(self, result: org_module.PreviewResult) -> None:
        self._current_preview = result
        self._set_progress(1.0)
        self._update_stat_cards(
            total=result.total_files,
            moved=result.organizable,
            dups=result.name_conflicts + result.content_duplicates,
            errors=0,
            others=result.going_to_others,
        )
        self.bar_chart.update_data(result.category_counts)
        self._set_status(
            f"✔  Analysis done — {result.total_files} files found.",
            PALETTE["success"],
        )

    def _run_preview(self) -> None:
        """Full scan with file-by-file preview list."""
        folder = self._get_folder()
        if folder is None:
            return
        self._clear_preview()
        self._set_status("👁  Building preview…", PALETTE["accent"])
        self._set_progress(0.0)

        def _worker():
            result = org_module.scan_folder(folder, self.recursive_var.get())
            self.root.after(0, lambda: self._on_preview_done(result))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_preview_done(self, result: org_module.PreviewResult) -> None:
        self._current_preview = result
        self._render_preview(result)
        self._set_progress(1.0)
        self._update_stat_cards(
            total=result.total_files,
            moved=result.organizable,
            dups=result.name_conflicts + result.content_duplicates,
            errors=0,
            others=result.going_to_others,
        )
        self.bar_chart.update_data(result.category_counts)
        self._set_status(
            f"👁  Preview ready — {result.total_files} files.",
            PALETTE["accent"],
        )

    def _run_organize(self) -> None:
        """Ask for confirmation, then organize in a background thread."""
        folder = self._get_folder()
        if folder is None:
            return

        # Optional: show a quick analyze first if not yet done
        if self._current_preview is None:
            result = org_module.scan_folder(folder, self.recursive_var.get())
            self._current_preview = result

        total = self._current_preview.total_files
        confirmed = msgbox.askyesno(
            "Confirm Organization",
            f"Ready to organize {total} file(s) in:\n\n{folder}\n\n"
            f"• Files will be moved into category subfolders.\n"
            f"• This action can be undone.\n\n"
            f"Proceed?",
            icon="question",
        )
        if not confirmed:
            self._set_status("Cancelled.", PALETTE["text_dim"])
            return

        self._set_status("⚡  Organizing…", PALETTE["accent"])
        self._set_progress(0.0)
        self._clear_preview()

        def _on_progress(filename: str, cat: str, idx: int, total_f: int) -> None:
            pct = idx / max(total_f, 1)
            self.root.after(0, lambda: self._set_progress(pct))
            self.root.after(0, lambda: self._set_status(
                f"⚡  {idx}/{total_f}  {filename} → {cat}", PALETTE["accent"]
            ))

        def _on_duplicate(fp: FilePreview, dup: DuplicateInfo) -> str:
            result_holder = [DuplicateAction.KEEP_BOTH]

            def _show_dialog():
                dlg = DuplicateDialog(self.root, fp, dup)
                self.root.wait_window(dlg)
                result_holder[0] = dlg.result

            self.root.after(0, _show_dialog)
            # Wait for dialog (spin in background thread — safe because
            # dialog runs on main thread via after())
            import time
            time.sleep(0.1)
            while self.root.winfo_exists():
                try:
                    if not any(
                        isinstance(w, DuplicateDialog)
                        for w in self.root.winfo_children()
                    ):
                        break
                except Exception:
                    break
                time.sleep(0.05)
            return result_holder[0]

        def _worker():
            org_result = org_module.organize_folder(
                folder_path=folder,
                recursive=self.recursive_var.get(),
                on_progress=_on_progress,
                on_duplicate=_on_duplicate,
                undo_mgr=self.undo_mgr,
            )
            self.root.after(0, lambda: self._on_organize_done(org_result, folder))

        self._organize_thread = threading.Thread(target=_worker, daemon=True)
        self._organize_thread.start()

    def _on_organize_done(self, result: org_module.OrganizeResult, folder: Path) -> None:
        self._set_progress(1.0)
        self._update_stat_cards(
            total=result.total_files,
            moved=result.moved,
            dups=0,
            errors=result.errors,
            others=result.category_stats.get("Others", 0),
        )
        self.bar_chart.update_data(result.category_stats)

        # Refresh preview
        preview = org_module.scan_folder(folder, self.recursive_var.get())
        self._render_preview(preview)

        if result.errors:
            self._set_status(
                f"⚠  Done: {result.moved} moved, {result.errors} error(s).",
                PALETTE["warning"],
            )
            err_text = "\n".join(result.error_messages[:10])
            msgbox.showwarning(
                "Completed with Errors",
                f"Organized {result.moved} file(s). {result.errors} error(s):\n\n{err_text}",
            )
        else:
            self._set_status(
                f"✔  Done! {result.moved} file(s) organized.",
                PALETTE["success"],
            )
            msgbox.showinfo(
                "Organization Complete",
                f"✔  {result.moved} file(s) organized successfully!\n\n"
                f"• log.txt and report.txt saved in:\n  {folder}\n\n"
                f"• Use Undo to reverse this operation.",
            )

    def _run_undo(self) -> None:
        if not self.undo_mgr.can_undo():
            self._set_status("↩  Nothing to undo.", PALETTE["text_dim"])
            msgbox.showinfo("Undo", "There is no previous operation to undo.")
            return

        summary = self.undo_mgr.get_last_session_summary()
        confirmed = msgbox.askyesno(
            "Undo Last Organization",
            f"Restore {summary['file_count']} file(s) to their original locations?\n\n"
            f"Folder: {summary['folder']}\n"
            f"Session: {summary['session_id']}\n\n"
            f"Files will be moved back. This cannot be re-undone.",
            icon="warning",
        )
        if not confirmed:
            return

        self._set_status("↩  Undoing…", PALETTE["warning"])
        self._set_progress(0.3)

        def _worker():
            undo_result = self.undo_mgr.undo_last()
            self.root.after(0, lambda: self._on_undo_done(undo_result))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_undo_done(self, result: dict) -> None:
        self._set_progress(1.0)
        restored = result["restored"]
        errors = result["errors"]
        skipped = result.get("skipped", 0)

        if errors or skipped:
            self._set_status(
                f"↩  Restored {restored}, {len(errors)} error(s).",
                PALETTE["warning"],
            )
            err_text = "\n".join(errors[:8])
            msgbox.showwarning("Undo Complete",
                               f"Restored {restored} file(s).\n\nIssues:\n{err_text}")
        else:
            self._set_status(f"↩  Restored {restored} file(s).", PALETTE["success"])
            msgbox.showinfo("Undo Complete",
                            f"✔  {restored} file(s) restored to their original locations.")

    def _toggle_watch(self) -> None:
        if not WATCHDOG_AVAILABLE:
            msgbox.showerror(
                "Watchdog Not Installed",
                "Install watchdog to use folder monitoring:\n\npip install watchdog",
            )
            return

        if self.monitor and self.monitor.is_running:
            self.monitor.stop()
            self.monitor = None
            self.watch_btn.configure(text="👁‍🗨  Watch",
                                     fg_color=PALETTE["surface2"])
            self.watch_indicator.configure(text="")
            self._set_status("⏹  Folder monitoring stopped.", PALETTE["text_dim"])
            return

        folder = self._get_folder()
        if folder is None:
            return

        def _on_organized(filename: str, status: str) -> None:
            self.root.after(0, lambda: self._set_status(
                f"👁  {filename} {status}", PALETTE["success"]
            ))

        self.monitor = FolderMonitor(folder, _on_organized)
        self.monitor.start()

        self.watch_btn.configure(text="⏹  Stop Watch",
                                 fg_color=PALETTE["danger"])
        self.watch_indicator.configure(text="● Watching")
        self._set_status(f"👁  Monitoring: {folder}", PALETTE["success"])

    def _open_settings(self) -> None:
        SettingsDialog(self)

    def _on_close(self) -> None:
        """Clean up before exit."""
        if self.monitor and self.monitor.is_running:
            self.monitor.stop()
        folder = self.folder_entry.get().strip()
        if folder:
            config_manager.set_value("last_folder", folder)
        self.root.destroy()

    # ── Main loop ──────────────────────────────────────────────────────────────

    def run(self) -> None:
        self.root.mainloop()
