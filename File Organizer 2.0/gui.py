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
    "bg":          "#03050c",      # Very deep dark background (Layer 1)
    "surface":     "#0f1322",      # Frosted glass panel color (Layer 3)
    "surface2":    "#151a30",      # Lighter nested surface
    "accent":      "#00e1ff",      # Cyan/electric blue accent
    "accent_hover":"#00b4cc",
    "success":     "#00e676",      # Vibrant neon green
    "warning":     "#ff9100",      # Vibrant orange/amber
    "danger":      "#ff1744",      # Vibrant red
    "text":        "#ffffff",
    "text_dim":    "#7a84a6",      # Muted blue-grey
    "border":      "#1f253d",      # Subtly glowing dark border
    "border_light":"#2d3b6e",      # Brighter glowing border
    "card_images": "#2979ff",
    "card_pdfs":   "#ff1744",
    "card_videos": "#d500f9",
    "card_docs":   "#00e676",
    "card_music":  "#ff9100",
    "card_archives":"#ffea00",
    "card_programs":"#f50057",
    "card_code":   "#00e1ff",
    "card_others": "#9e9e9e",
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

# ── Glassmorphism Components ──────────────────────────────────────────────────

class GlassPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("fg_color", PALETTE["surface"])
        kwargs.setdefault("border_color", PALETTE["border"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("corner_radius", 14)
        super().__init__(parent, **kwargs)

class GlassButton(ctk.CTkButton):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("fg_color", PALETTE["surface2"])
        kwargs.setdefault("hover_color", PALETTE["border_light"])
        kwargs.setdefault("border_color", PALETTE["border"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("text_color", PALETTE["text"])
        kwargs.setdefault("font", ("Segoe UI", 12, "bold"))
        super().__init__(parent, **kwargs)

class GlassEntry(ctk.CTkEntry):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("fg_color", PALETTE["surface2"])
        kwargs.setdefault("border_color", PALETTE["border"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("text_color", PALETTE["text"])
        super().__init__(parent, **kwargs)
        self.bind("<FocusIn>", self._on_focus)
        self.bind("<FocusOut>", self._on_unfocus)

    def _on_focus(self, event):
        self.configure(border_color=PALETTE["accent"])

    def _on_unfocus(self, event):
        self.configure(border_color=PALETTE["border"])

class GlassProgressBar(ctk.CTkProgressBar):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("fg_color", PALETTE["surface2"])
        kwargs.setdefault("progress_color", PALETTE["accent"])
        kwargs.setdefault("border_color", PALETTE["border"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("corner_radius", 4)
        super().__init__(parent, **kwargs)

class GlassCard(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("fg_color", PALETTE["surface2"])
        kwargs.setdefault("border_color", PALETTE["border"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("corner_radius", 10)
        super().__init__(parent, **kwargs)


# ── Helper widgets ────────────────────────────────────────────────────────────

def _make_stat_card(parent, icon: str, label: str, value: str, color: str) -> ctk.CTkFrame:
    """Glass-style premium stat card widget with icon."""
    # Outer frame for border glow
    frame = ctk.CTkFrame(parent, fg_color=PALETTE["surface"],
                         border_color=color, border_width=1, corner_radius=12)
    
    # Top row: icon + label
    top = ctk.CTkFrame(frame, fg_color="transparent")
    top.pack(fill="x", padx=14, pady=(14, 4))
    
    icon_lbl = ctk.CTkLabel(top, text=icon, font=("Segoe UI", 14), text_color=color)
    icon_lbl.pack(side="left", padx=(0, 6))
    
    lbl = ctk.CTkLabel(top, text=label, font=("Segoe UI", 12),
                       text_color=PALETTE["text_dim"])
    lbl.pack(side="left")
    
    # Value
    val = ctk.CTkLabel(frame, text=value, font=("Segoe UI", 28, "bold"),
                       text_color=PALETTE["text"])
    val.pack(padx=14, pady=(0, 16))
    
    frame._val_label = val   # store reference for updates
    return frame


def format_size(size_bytes: int) -> str:
    """Format bytes to a human readable string."""
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    if i == 0:
        return f"{int(size)} {units[i]}"
    return f"{size:.1f} {units[i]}"


class ToolTip:
    """Simple tooltip implementation for Tkinter/CustomTkinter widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide_tip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.show_tip)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show_tip(self):
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("Segoe UI", 9))
        label.pack(ipadx=4, ipady=2)

    def hide_tip(self):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()


# ── Settings Dialog ───────────────────────────────────────────────────────────

class SettingsDialog(ctk.CTkToplevel):
    """Modal settings window with a tabbed interface."""

    def __init__(self, parent: "App") -> None:
        super().__init__(parent.root)
        self.parent_app = parent
        self.title("Settings")
        self.geometry("640x700")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["bg"])
        self.grab_set()

        self.settings = config_manager.load_settings()

        # ── Title ─────────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="⚙  Settings",
                     font=("Segoe UI", 18, "bold"),
                     text_color=PALETTE["text"]).pack(pady=(16, 4))
        ctk.CTkLabel(self, text="Configure how the organizer behaves.",
                     font=("Segoe UI", 12),
                     text_color=PALETTE["text_dim"]).pack(pady=(0, 12))

        # ── Tabs ──────────────────────────────────────────────────────────
        self.tabview = ctk.CTkTabview(self, width=580, height=480,
                                      fg_color=PALETTE["surface"],
                                      segmented_button_selected_color=PALETTE["accent"],
                                      segmented_button_selected_hover_color=PALETTE["accent_hover"])
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

        self.tabview.add("General")
        self.tabview.add("File Organization")
        self.tabview.add("Duplicate Handling")
        self.tabview.add("Watch Mode")

        self._build_general_tab()
        self._build_file_org_tab()
        self._build_duplicate_tab()
        self._build_watch_tab()

        # ── Save button ───────────────────────────────────────────────────
        ctk.CTkButton(self, text="✔  Save & Close",
                      fg_color=PALETTE["success"],
                      hover_color="#1ea855",
                      font=("Segoe UI", 13, "bold"),
                      height=40,
                      command=self._save_and_close).pack(pady=(10, 20), padx=24, fill="x")

    def _build_general_tab(self) -> None:
        tab = self.tabview.tab("General")
        
        # Theme
        row = ctk.CTkFrame(tab, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=16)
        ctk.CTkLabel(row, text="Theme:", font=("Segoe UI", 12),
                     text_color=PALETTE["text"]).pack(side="left")
        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "dark"))
        ctk.CTkOptionMenu(row, values=["dark", "light"], variable=self.theme_var,
                          fg_color=PALETTE["surface2"],
                          button_color=PALETTE["accent"],
                          command=self._on_theme_change).pack(side="right")

        # Confirm Organize
        self.confirm_var = ctk.BooleanVar(value=self.settings.get("confirm_organize", True))
        ctk.CTkCheckBox(tab, text="Ask for confirmation before organizing files",
                        variable=self.confirm_var,
                        font=("Segoe UI", 12), text_color=PALETTE["text"]).pack(anchor="w", padx=16, pady=10)

        # Include Subfolders
        self.recursive_var = ctk.BooleanVar(value=self.settings.get("include_subfolders", False))
        ctk.CTkCheckBox(tab, text="Include subfolders (recursive scan) by default",
                        variable=self.recursive_var,
                        font=("Segoe UI", 12), text_color=PALETTE["text"]).pack(anchor="w", padx=16, pady=10)

    def _build_file_org_tab(self) -> None:
        tab = self.tabview.tab("File Organization")

        # Custom Extensions
        ctk.CTkLabel(tab, text="Custom Extensions (Add extensions to categories)",
                     font=("Segoe UI", 13, "bold"), text_color=PALETTE["accent"]).pack(anchor="w", padx=16, pady=(12, 4))
        
        add_frame = ctk.CTkFrame(tab, fg_color="transparent")
        add_frame.pack(fill="x", padx=16, pady=4)
        
        all_cats = list(cat_module.DEFAULT_CATEGORIES.keys())
        self.cat_var = ctk.StringVar(value=all_cats[0])
        ctk.CTkOptionMenu(add_frame, values=all_cats, variable=self.cat_var,
                          width=120, fg_color=PALETTE["surface2"]).pack(side="left", padx=(0, 8))
        
        self.ext_entry = ctk.CTkEntry(add_frame, placeholder_text=".xyz, .abc", fg_color=PALETTE["surface2"])
        self.ext_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        ctk.CTkButton(add_frame, text="Add", width=60, fg_color=PALETTE["accent"],
                      command=self._add_extensions).pack(side="right")

        self.custom_display = ctk.CTkTextbox(tab, height=80, fg_color=PALETTE["surface2"], font=("Consolas", 11))
        self.custom_display.pack(fill="x", padx=16, pady=(8, 16))
        self._refresh_custom_display()

        # Rules
        ctk.CTkLabel(tab, text="Organization Rules",
                     font=("Segoe UI", 13, "bold"), text_color=PALETTE["accent"]).pack(anchor="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(tab, text="If extension is AND filename contains → move to Category",
                     font=("Segoe UI", 11), text_color=PALETTE["text_dim"]).pack(anchor="w", padx=16, pady=2)

        rule_add_frame = ctk.CTkFrame(tab, fg_color="transparent")
        rule_add_frame.pack(fill="x", padx=16, pady=4)

        self.rule_ext_entry = ctk.CTkEntry(rule_add_frame, placeholder_text="Ext (e.g. .pdf)", width=90)
        self.rule_ext_entry.pack(side="left", padx=(0, 4))

        self.rule_contains_entry = ctk.CTkEntry(rule_add_frame, placeholder_text="Contains (e.g. college)", width=130)
        self.rule_contains_entry.pack(side="left", padx=(0, 4))

        self.rule_cat_entry = ctk.CTkEntry(rule_add_frame, placeholder_text="Category Name")
        self.rule_cat_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(rule_add_frame, text="Add Rule", width=70, fg_color=PALETTE["accent"],
                      command=self._add_rule).pack(side="right")

        self.rules_display = ctk.CTkTextbox(tab, height=80, fg_color=PALETTE["surface2"], font=("Consolas", 11))
        self.rules_display.pack(fill="x", padx=16, pady=(8, 8))
        self._refresh_rules_display()

        ctk.CTkButton(tab, text="Clear Custom Extensions & Rules", fg_color=PALETTE["danger"], hover_color="#c0392b",
                      command=self._clear_rules_exts).pack(anchor="e", padx=16, pady=4)

    def _build_duplicate_tab(self) -> None:
        tab = self.tabview.tab("Duplicate Handling")
        
        ctk.CTkLabel(tab, text="When a duplicate file is detected:",
                     font=("Segoe UI", 13, "bold"), text_color=PALETTE["text"]).pack(anchor="w", padx=16, pady=(20, 10))
        
        self.dup_var = ctk.StringVar(value=self.settings.get("duplicate_action", "keep_both"))
        
        ctk.CTkRadioButton(tab, text="Keep both (auto-rename new file to file_1.ext)",
                           variable=self.dup_var, value="keep_both",
                           font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=8)
                           
        ctk.CTkRadioButton(tab, text="Skip the duplicate file",
                           variable=self.dup_var, value="skip",
                           font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=8)
                           
        ctk.CTkRadioButton(tab, text="Ask every time",
                           variable=self.dup_var, value="ask",
                           font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=8)

    def _build_watch_tab(self) -> None:
        tab = self.tabview.tab("Watch Mode")
        
        self.watch_auto_var = ctk.BooleanVar(value=self.settings.get("watch_auto_organize", True))
        ctk.CTkCheckBox(tab, text="Automatically organize new files when Watch Mode is active",
                        variable=self.watch_auto_var,
                        font=("Segoe UI", 12)).pack(anchor="w", padx=16, pady=16)

        ctk.CTkLabel(tab, text="Note: Files are organized silently in the background.",
                     font=("Segoe UI", 11), text_color=PALETTE["text_dim"]).pack(anchor="w", padx=16)

    def _on_theme_change(self, value: str) -> None:
        ctk.set_appearance_mode(value)

    def _refresh_custom_display(self) -> None:
        custom = self.settings.get("custom_categories", {})
        self.custom_display.configure(state="normal")
        self.custom_display.delete("1.0", "end")
        if custom:
            for cat, exts in custom.items():
                self.custom_display.insert("end", f"{cat}: {', '.join(exts)}\n")
        else:
            self.custom_display.insert("end", "No custom extensions added yet.")
        self.custom_display.configure(state="disabled")

    def _refresh_rules_display(self) -> None:
        rules = self.settings.get("organization_rules", [])
        self.rules_display.configure(state="normal")
        self.rules_display.delete("1.0", "end")
        if rules:
            for idx, rule in enumerate(rules, 1):
                self.rules_display.insert("end", f"[{idx}] Ext: {rule.get('extension','*')} | Contains: '{rule.get('contains','')}' → {rule.get('category','')}\n")
        else:
            self.rules_display.insert("end", "No rules added yet.")
        self.rules_display.configure(state="disabled")

    def _add_extensions(self) -> None:
        cat = self.cat_var.get()
        raw = self.ext_entry.get().strip()
        if not raw: return
        exts = [e.strip().lower() for e in raw.split(",") if e.strip()]
        exts = [(e if e.startswith(".") else "." + e) for e in exts]
        custom = self.settings.get("custom_categories", {})
        existing = set(custom.get(cat, []))
        existing.update(exts)
        custom[cat] = sorted(existing)
        self.settings["custom_categories"] = custom
        self.ext_entry.delete(0, "end")
        self._refresh_custom_display()

    def _add_rule(self) -> None:
        ext = self.rule_ext_entry.get().strip()
        contains = self.rule_contains_entry.get().strip()
        cat = self.rule_cat_entry.get().strip()
        if not cat:
            msgbox.showerror("Error", "Category Name is required.", parent=self)
            return
        rules = self.settings.get("organization_rules", [])
        rules.append({"extension": ext, "contains": contains, "category": cat})
        self.settings["organization_rules"] = rules
        self.rule_ext_entry.delete(0, "end")
        self.rule_contains_entry.delete(0, "end")
        self.rule_cat_entry.delete(0, "end")
        self._refresh_rules_display()

    def _clear_rules_exts(self) -> None:
        if msgbox.askyesno("Clear", "Remove all custom extensions and rules?", parent=self):
            self.settings["custom_categories"] = {}
            self.settings["organization_rules"] = []
            self._refresh_custom_display()
            self._refresh_rules_display()

    def _save_and_close(self) -> None:
        self.settings["theme"] = self.theme_var.get()
        self.settings["include_subfolders"] = self.recursive_var.get()
        self.settings["confirm_organize"] = self.confirm_var.get()
        self.settings["duplicate_action"] = self.dup_var.get()
        self.settings["watch_auto_organize"] = self.watch_auto_var.get()
        
        config_manager.save_settings(self.settings)
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
            self.create_text(
                10, 20, anchor="nw",
                text="Run Analyze or Preview to see data.",
                fill=PALETTE["text_dim"], font=("Segoe UI", 10)
            )
            return

        w = self.winfo_width() or 300
        h = self.winfo_height() or 200

        max_val = max(self._data.values(), default=1) or 1
        cats = [c for c, v in self._data.items() if v > 0]
        if not cats:
            return

        n = len(cats)
        n = len(cats)
        bar_h = 6
        label_w = 90
        pad = 12
        
        required_h = n * (bar_h + 16) + pad * 2
        if h < required_h:
            self.configure(height=required_h)
            h = required_h

        y = pad + 8

        for cat in cats:
            val = self._data[cat]
            color = CATEGORY_COLORS.get(cat, PALETTE["text_dim"])
            bar_max_w = w - label_w - pad * 2 - 40
            bar_w = int(bar_max_w * val / max_val)

            # Label
            self.create_text(
                pad, y + bar_h // 2,
                text=f"{CATEGORY_ICONS.get(cat, chr(8226))}  {cat}",
                anchor="w", fill=PALETTE["text"],
                font=("Segoe UI", 10),
            )
            # Bar background (thin track)
            x0, x1 = label_w, label_w + bar_max_w
            self.create_rectangle(x0, y, x1, y + bar_h, fill=PALETTE["border"], outline="", width=0)
            
            # Bar fill (thin glowing track)
            if bar_w > 0:
                self.create_rectangle(label_w, y, label_w + bar_w, y + bar_h, fill=color, outline="", width=0)
                
            # Value label in accent color
            self.create_text(
                label_w + bar_max_w + 12, y + bar_h // 2,
                text=str(val), anchor="e",
                fill=color,
                font=("Segoe UI", 10),
            )
            y += bar_h + 16




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

        self.bg_canvas = tk.Canvas(self.root, bg=PALETTE["bg"], highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        # Create very soft, large colored blobs to simulate deep ambient lighting
        self.bg_canvas.create_oval(-300, -200, 700, 700, fill="#080c21", outline="")
        self.bg_canvas.create_oval(200, -100, 900, 600, fill="#06091c", outline="")
        self.bg_canvas.create_oval(600, 300, 1500, 1200, fill="#0b071e", outline="")
        self.bg_canvas.create_oval(50, 500, 750, 1300, fill="#040f1a", outline="")
        self.bg_canvas.create_oval(800, -50, 1800, 800, fill="#050817", outline="")

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
        hdr = GlassPanel(self.root, height=80, corner_radius=12)
        hdr.pack(fill="x", side="top", padx=20, pady=(20, 10))
        hdr.pack_propagate(False)

        # Left: logo + title
        left = ctk.CTkFrame(hdr, fg_color="transparent")
        left.pack(side="left", padx=24, pady=16)
        
        icon_frame = ctk.CTkFrame(left, fg_color="transparent")
        icon_frame.pack(side="left", padx=(0, 18))
        
        # Glowing icon effect
        ctk.CTkLabel(icon_frame, text="📁", font=("Segoe UI", 38), text_color="#184b9c").place(x=2, y=2)
        ctk.CTkLabel(icon_frame, text="📁", font=("Segoe UI", 38), text_color=PALETTE["accent"]).pack()
        
        title_col = ctk.CTkFrame(left, fg_color="transparent")
        title_col.pack(side="left")
        ctk.CTkLabel(title_col, text="Advanced File Organizer",
                     font=("Segoe UI", 22, "bold"),
                     text_color=PALETTE["text"]).pack(anchor="w", pady=(0, 2))
        ctk.CTkLabel(title_col, text="v2.0  •  Smart & Safe File Management",
                     font=("Segoe UI", 12),
                     text_color=PALETTE["text_dim"]).pack(anchor="w")

        # Right: watch indicator / app status
        right_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        right_frame.pack(side="right", padx=24)
        
        self.header_status = ctk.CTkLabel(right_frame, text="● Ready", font=("Segoe UI", 12), text_color=PALETTE["success"])
        self.header_status.pack(side="right", padx=(16, 0))
        
        self.watch_indicator = ctk.CTkLabel(right_frame, text="",
                                            font=("Segoe UI", 12),
                                            text_color=PALETTE["accent"])
        self.watch_indicator.pack(side="right")

    def _build_folder_row(self) -> None:
        row = GlassPanel(self.root, corner_radius=12)
        row.pack(fill="x", padx=20, pady=4)
        row.columnconfigure(1, weight=1)

        ctk.CTkLabel(row, text="📁 Folder to Organize:",
                     font=("Segoe UI", 13),
                     text_color=PALETTE["text_dim"]).grid(row=0, column=0, padx=(24, 12), pady=(18, 4), sticky="w")

        # Make entry look like a translucent inner field
        self.folder_entry = ctk.CTkEntry(
            row,
            placeholder_text="C:/...",
            height=38,
            fg_color=PALETTE["surface2"],
            border_color=PALETTE["border"],
            border_width=1,
            corner_radius=8,
            text_color=PALETTE["text"]
        )
        self.folder_entry.grid(row=0, column=1, padx=(0, 12), pady=(18, 4), sticky="ew")

        ctk.CTkButton(
            row, text="Browse",
            fg_color="#1e2540",
            hover_color="#2a355c",
            border_color="#303c66",
            border_width=1,
            text_color=PALETTE["accent"],
            font=("Segoe UI", 12, "bold"),
            width=90, height=38,
            corner_radius=8,
            command=self._browse,
        ).grid(row=0, column=2, padx=(0, 24), pady=(18, 4))
        
        ctk.CTkCheckBox(
            row,
            text="Include Subfolders (recursive)",
            variable=self.recursive_var,
            font=("Segoe UI", 12),
            text_color=PALETTE["text_dim"],
            fg_color=PALETTE["accent"],
            hover_color=PALETTE["accent_hover"],
            border_width=1,
            border_color=PALETTE["border"],
            corner_radius=4,
            checkbox_width=20, checkbox_height=20
        ).grid(row=1, column=1, padx=(0, 12), pady=(4, 18), sticky="w")

    def _build_options_row(self) -> None:
        pass

    def _build_action_bar(self) -> None:
        bar = GlassPanel(self.root, corner_radius=12)
        bar.pack(fill="x", padx=20, pady=4)

        # Center the buttons
        btn_container = ctk.CTkFrame(bar, fg_color="transparent")
        btn_container.pack(expand=True, padx=4, pady=12)

        btn_config = [
            ("🔍 Analyze",   "transparent",         PALETTE["border_light"],     self._run_analyze, "Preview files without moving them"),
            ("👁 Preview",   "transparent",         PALETTE["border_light"], self._run_preview, "Detailed file preview before organizing"),
            ("⚡ Organize",  PALETTE["accent"],    PALETTE["accent_hover"],             self._run_organize, "Move files into category folders"),
            ("↩ Undo",       "transparent",         PALETTE["border_light"],             self._run_undo, "Restore files from the last session"),
            ("◉ Watch",    "transparent",         PALETTE["border_light"],     self._toggle_watch, "Monitor folder for new files"),
            ("📊 Activity",   "transparent",         PALETTE["border_light"],     self._open_activity, "View recent organization activity"),
            ("⚙ Settings",  "transparent",         PALETTE["border_light"],     self._open_settings, "Configure application behavior"),
        ]

        for text, fg, hover, cmd, tooltip_text in btn_config:
            is_watch = "Watch" in text
            is_organize = "Organize" in text
            
            # Subtle border for normal buttons, bright accent for organize
            border_col = PALETTE["accent"] if is_organize else PALETTE["border"]
            btn_fg = fg if is_organize else PALETTE["surface2"]
            text_color = "#ffffff" if is_organize else PALETTE["text"]
            
            btn = GlassButton(
                btn_container,
                text=text,
                fg_color=btn_fg,
                hover_color=hover,
                text_color=text_color,
                border_color=border_col,
                height=40,
                corner_radius=8,
                command=cmd,
            )
            btn.pack(side="left", padx=8, pady=2)
            if is_watch:
                self.watch_btn = btn
            ToolTip(btn, tooltip_text)

    def _build_progress_row(self) -> None:
        row = GlassPanel(self.root, corner_radius=12)
        row.pack(fill="x", padx=20, pady=4)

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=(12, 8))

        self.status_label = ctk.CTkLabel(
            inner, text="✓ Ready",
            font=("Segoe UI", 12),
            text_color=PALETTE["text_dim"],
            anchor="w",
        )
        self.status_label.pack(side="left")

        self.progress_pct = ctk.CTkLabel(
            inner, text="0%",
            font=("Segoe UI", 12, "bold"),
            text_color=PALETTE["text"],
            anchor="e"
        )
        self.progress_pct.pack(side="right")

        # Extremely thin, glowing progress line
        self.progress_bar = GlassProgressBar(row, height=2, corner_radius=0, border_width=0, progress_color=PALETTE["accent"])
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 16))

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
        frame = GlassPanel(parent)
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

        # Search / Filter row
        sf_row = ctk.CTkFrame(frame, fg_color="transparent")
        sf_row.pack(fill="x", padx=12, pady=(4, 0))

        self.search_var = ctk.StringVar()
        self.search_entry = GlassEntry(sf_row, placeholder_text="Search files...",
                                         textvariable=self.search_var,
                                         height=30)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_var.trace_add("write", lambda *args: self._filter_preview())

        self.filter_var = ctk.StringVar(value="All")
        cats_with_all = ["All"] + list(cat_module.DEFAULT_CATEGORIES.keys()) + ["Others", "Duplicates", "Errors"]
        self.filter_menu = ctk.CTkOptionMenu(sf_row, values=cats_with_all, variable=self.filter_var,
                                             fg_color=PALETTE["surface2"], button_color=PALETTE["border"],
                                             command=lambda _: self._filter_preview(), width=130)
        self.filter_menu.pack(side="right")

        # Column headers
        col_hdr = ctk.CTkFrame(frame, fg_color="transparent")
        col_hdr.pack(fill="x", padx=12, pady=(12, 0))
        for text, w in [("File Name", 190), ("Size", 60), ("→", 20), ("Category", 100), ("Status", 110)]:
            ctk.CTkLabel(col_hdr, text=text, width=w,
                         font=("Segoe UI", 11),
                         text_color=PALETTE["text"],
                         anchor="w").pack(side="left", padx=6, pady=2)
        
        sep = ctk.CTkFrame(frame, fg_color=PALETTE["border"], height=1)
        sep.pack(fill="x", padx=12, pady=(2, 4))

        # Scrollable file list
        self.preview_scroll = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            scrollbar_button_color=PALETTE["border"],
        )
        self.preview_scroll.pack(fill="both", expand=True, padx=12, pady=(4, 12))

    def _build_stats_panel(self, parent) -> None:
        frame = GlassPanel(parent, corner_radius=12)
        frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        hdr = ctk.CTkFrame(frame, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(16, 12))
        ctk.CTkLabel(hdr, text="📊 Statistics",
                     font=("Segoe UI", 14, "bold"),
                     text_color=PALETTE["text"]).pack(side="left")

        # ── Summary stat cards ────────────────────────────────────────────
        cards_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=16, pady=(0, 8))
        cards_frame.columnconfigure((0, 1), weight=1)

        self.card_total = _make_stat_card(cards_frame, "📄", "Total Files", "0", PALETTE["accent"])
        self.card_total.grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        self.card_moved = _make_stat_card(cards_frame, "✓", "Organized", "0", PALETTE["success"])
        self.card_moved.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        self.card_dups = _make_stat_card(cards_frame, "◇", "Duplicates", "0", PALETTE["warning"])
        self.card_dups.grid(row=1, column=0, padx=6, pady=6, sticky="ew")

        self.card_errors = _make_stat_card(cards_frame, "⚠", "Errors", "0", PALETTE["danger"])
        self.card_errors.grid(row=1, column=1, padx=6, pady=6, sticky="ew")

        self.card_others = _make_stat_card(cards_frame, "📁", "Others", "0", PALETTE["text_dim"])
        self.card_others.grid(row=2, column=0, padx=6, pady=6, sticky="ew")

        self.card_size = _make_stat_card(cards_frame, "💾", "Total Size", "0 B", PALETTE["accent"])
        self.card_size.grid(row=2, column=1, padx=6, pady=6, sticky="ew")

        # ── Bar chart ─────────────────────────────────────────────────────
        ctk.CTkLabel(frame, text="Category Breakdown",
                     font=("Segoe UI", 12, "bold"),
                     text_color=PALETTE["text_dim"]).pack(anchor="w", padx=16, pady=(4, 2))

        chart_frame = ctk.CTkScrollableFrame(frame, fg_color="transparent", scrollbar_button_color=PALETTE["border"])
        chart_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.bar_chart = BarChart(chart_frame, bg=PALETTE["surface"])
        self.bar_chart.pack(fill="both", expand=True, padx=2, pady=2)
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
        # Prefix a dot indicator based on nature of message
        if msg.startswith(("✔", "Done", "✓")):
            display = f"✓  {msg.lstrip('✔✓').strip()}"
            header_display = "● Done"
            header_color = PALETTE["success"]
        elif "error" in msg.lower() or "❌" in msg:
            display = f"●  {msg}"
            header_display = "● Error"
            header_color = PALETTE["danger"]
        elif "Analyzing" in msg or "Building" in msg or "Organizing" in msg or "Undoing" in msg or "Monitoring" in msg:
            display = f"●  {msg}"
            header_display = "● Working"
            header_color = PALETTE["accent"]
        else:
            display = msg
            header_display = "● Ready"
            header_color = PALETTE["text_dim"]

        self.status_label.configure(text=display, text_color=color)
        self.header_status.configure(text=header_display, text_color=header_color)
        self.root.update_idletasks()

    def _set_progress(self, value: float) -> None:
        """value: 0.0 – 1.0"""
        self.progress_bar.set(value)
        self.progress_pct.configure(text=f"{int(value * 100)}%")
        self.root.update_idletasks()

    def _restore_last_folder(self) -> None:
        last = config_manager.get("last_folder", "")
        if last and Path(last).is_dir():
            self.folder_entry.insert(0, last)

    def _clear_preview(self) -> None:
        for widget in self.preview_scroll.winfo_children():
            widget.destroy()
        self.preview_count_label.configure(text="")

    def _update_stat_cards(self, total=0, moved=0, dups=0, errors=0, others=0, total_size=0) -> None:
        self.card_total._val_label.configure(text=str(total))
        self.card_moved._val_label.configure(text=str(moved))
        self.card_dups._val_label.configure(text=str(dups))
        self.card_errors._val_label.configure(text=str(errors))
        self.card_others._val_label.configure(text=str(others))
        self.card_size._val_label.configure(text=format_size(total_size))

    # ── Preview list rendering ────────────────────────────────────────────────

    def _filter_preview(self) -> None:
        if self._current_preview:
            self._render_preview(self._current_preview)

    def _render_preview(self, preview: org_module.PreviewResult, empty_message: str = "") -> None:
        self._clear_preview()

        search_text = self.search_var.get().lower()
        filter_cat = self.filter_var.get()

        visible_count = 0

        for fp in preview.file_previews:
            if search_text and search_text not in fp.filename.lower():
                continue
            if filter_cat != "All":
                if filter_cat == "Duplicates" and not (fp.is_name_conflict or fp.is_content_duplicate):
                    continue
                elif filter_cat == "Errors":
                    pass # Not tracked here, let's keep it simple
                elif filter_cat not in ["Duplicates", "Errors"] and fp.destination_category != filter_cat:
                    continue
            
            visible_count += 1
            row_color = PALETTE["surface2"] if visible_count % 2 == 0 else PALETTE["surface"]
            row = ctk.CTkFrame(self.preview_scroll,
                               fg_color=row_color, corner_radius=5)
            row.pack(fill="x", pady=1)

            # File name
            ctk.CTkLabel(row, text=fp.filename, width=190,
                         anchor="w", font=("Segoe UI", 11),
                         text_color=PALETTE["text"]).pack(side="left", padx=(8, 4), pady=5)

            # Size
            ctk.CTkLabel(row, text=format_size(fp.file_size), width=60,
                         anchor="e", font=("Segoe UI", 11),
                         text_color=PALETTE["text_dim"]).pack(side="left", padx=4)

            # Arrow
            ctk.CTkLabel(row, text="→", width=20,
                         font=("Segoe UI", 11),
                         text_color=PALETTE["text_dim"]).pack(side="left")

            # Category badge
            cat_color = CATEGORY_COLORS.get(fp.destination_category, PALETTE["text_dim"])
            cat_lbl = ctk.CTkLabel(row,
                                   text=f"{CATEGORY_ICONS.get(fp.destination_category, '•')}  {fp.destination_category}",
                                   width=100,
                                   anchor="w",
                                   font=("Segoe UI", 11),
                                   text_color=cat_color)
            cat_lbl.pack(side="left", padx=4)

            # Status chip
            if fp.is_content_duplicate:
                chip_text, chip_color = "⊟ Content Dup", PALETTE["warning"]
            elif fp.is_name_conflict:
                chip_text, chip_color = "⚠ Name Conflict", PALETTE["warning"]
            else:
                chip_text, chip_color = "✔ Ready", PALETTE["success"]

            ctk.CTkLabel(row, text=chip_text, width=110,
                         anchor="w",
                         font=("Segoe UI", 11),
                         text_color=chip_color).pack(side="left", padx=4)

        if visible_count == 0:
            msg = empty_message or "No files found in this folder."
            lbl = ctk.CTkLabel(self.preview_scroll, text=msg,
                               font=("Segoe UI", 13, "italic"),
                               text_color=PALETTE["text_dim"])
            lbl.pack(pady=40)
            self.preview_count_label.configure(text="")
        else:
            self.preview_count_label.configure(text=f"{visible_count} file{'s' if visible_count != 1 else ''} shown")

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
            total_size=result.total_size,
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
            total_size=result.total_size,
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
            total_size=result.total_size,
        )
        self.bar_chart.update_data(result.category_stats)

        # Refresh preview
        preview = org_module.scan_folder(folder, self.recursive_var.get())
        if result.moved > 0:
            msg = f"✓ Organized {result.moved} file(s). Select another folder to continue."
        else:
            msg = "No files to display."
        self._render_preview(preview, empty_message=msg)

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
            self.watch_btn.configure(text="◉  Watch",
                                     fg_color=PALETTE["surface2"],
                                     border_color=PALETTE["border"])
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

        self.watch_btn.configure(text="●  Watching",
                                 fg_color=PALETTE["success"],
                                 border_color=PALETTE["success"],
                                 hover_color="#1ea855")
        self.watch_indicator.configure(text="● Watching", text_color=PALETTE["success"])
        self._set_status(f"👁  Monitoring: {folder}", PALETTE["success"])

    def _open_activity(self) -> None:
        ActivityDialog(self)

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

# ── Activity Dialog ───────────────────────────────────────────────────────────

class ActivityDialog(ctk.CTkToplevel):
    """Shows history of organized files."""
    def __init__(self, parent: App) -> None:
        super().__init__(parent.root)
        self.title("Recent Activity")
        self.geometry("600x500")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["bg"])
        self.grab_set()

        ctk.CTkLabel(self, text="🕰  Recent Organization Activity",
                     font=("Segoe UI", 18, "bold"), text_color=PALETTE["text"]).pack(pady=(20, 10))

        scroll = ctk.CTkScrollableFrame(self, fg_color=PALETTE["surface"], corner_radius=10)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        summaries = parent.undo_mgr.get_all_sessions_summary()
        if not summaries:
            ctk.CTkLabel(scroll, text="No activity recorded.", text_color=PALETTE["text_dim"]).pack(pady=20)
            return

        for s in reversed(summaries):
            card = ctk.CTkFrame(scroll, fg_color=PALETTE["surface2"], corner_radius=8)
            card.pack(fill="x", pady=6, padx=4)
            
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(10, 2))
            
            ctk.CTkLabel(top_row, text=s["timestamp"], font=("Segoe UI", 11, "bold"), text_color=PALETTE["text"]).pack(side="left")
            ctk.CTkLabel(top_row, text=f"ID: {s['session_id'][:8]}", font=("Segoe UI", 10), text_color=PALETTE["text_dim"]).pack(side="right")
            
            mid_row = ctk.CTkFrame(card, fg_color="transparent")
            mid_row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(mid_row, text=f"Folder: {s['folder']}", font=("Segoe UI", 11), text_color=PALETTE["text"]).pack(side="left")
            
            bot_row = ctk.CTkFrame(card, fg_color="transparent")
            bot_row.pack(fill="x", padx=10, pady=(2, 10))
            
            ctk.CTkLabel(bot_row, text=f"Moved: {s['file_count']}", font=("Segoe UI", 11), text_color=PALETTE["success"]).pack(side="left", padx=(0, 10))
            if s.get("errors", 0):
                ctk.CTkLabel(bot_row, text=f"Errors: {s['errors']}", font=("Segoe UI", 11), text_color=PALETTE["danger"]).pack(side="left", padx=(0, 10))
            if s.get("skipped", 0):
                ctk.CTkLabel(bot_row, text=f"Skipped: {s['skipped']}", font=("Segoe UI", 11), text_color=PALETTE["warning"]).pack(side="left")
