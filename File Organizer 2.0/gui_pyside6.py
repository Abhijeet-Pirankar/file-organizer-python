"""
gui.py
------
Main GUI for File Organizer v2.0.
Redesigned with PySide6 for a premium glassmorphism aesthetic.
"""

import threading
import time
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QObject, Signal, QTimer, QSize, QPoint
from PySide6.QtGui import (
    QColor, QFont, QRadialGradient, QPainter, QBrush, QPen, QPainterPath,
    QLinearGradient, QIcon
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialog, QMessageBox, QFileDialog, QScrollArea, QFrame, QSizePolicy, QTabWidget,
    QCheckBox, QApplication
)
from PySide6.QtWidgets import QGraphicsDropShadowEffect

import categories as cat_module
import config_manager
import organizer as org_module
import undo_manager as undo_module
from duplicate_detector import DuplicateInfo
from file_monitor import WATCHDOG_AVAILABLE, FolderMonitor
from organizer import DuplicateAction, FilePreview

PALETTE = {
    "bg_base": QColor("#03050c"),
    "glow_cyan": QColor(0, 225, 255, 30),
    "glow_purple": QColor(138, 43, 226, 40),
    "glow_blue": QColor(41, 121, 255, 30),
    "surface": QColor(15, 19, 34, 180),
    "surface_hover": QColor(25, 35, 60, 200),
    "surface_card": QColor(10, 15, 25, 160),
    "accent": QColor("#00e1ff"),
    "success": QColor("#00e676"),
    "warning": QColor("#ff9100"),
    "danger": QColor("#ff1744"),
    "text": QColor("#ffffff"),
    "text_dim": QColor("#7a84a6"),
    "border": QColor(45, 59, 110, 100),
    "border_light": QColor(0, 225, 255, 80),
}

CATEGORY_COLORS = {
    "Images":   "#2979ff",
    "PDFs":     "#ff1744",
    "Videos":   "#d500f9",
    "Docs":     "#00e676",
    "Music":    "#ff9100",
    "Archives": "#ffea00",
    "Programs": "#f50057",
    "Code":     "#00e1ff",
    "Others":   "#9e9e9e",
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

class Dispatcher(QObject):
    dispatch = Signal(object)
    def __init__(self):
        super().__init__()
        self.dispatch.connect(self._exec)
    def _exec(self, func):
        func()

def add_shadow(widget, radius=15, alpha=100, y_offset=4):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(radius)
    shadow.setColor(QColor(0, 0, 0, alpha))
    shadow.setOffset(0, y_offset)
    widget.setGraphicsEffect(shadow)

class GlassPanel(QFrame):
    def __init__(self, parent=None, radius=12, fill_color=PALETTE["surface"]):
        super().__init__(parent)
        self.radius = radius
        self.fill_color = fill_color
        self.setAttribute(Qt.WA_TranslucentBackground)
        add_shadow(self, 20, 120, 5)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(1, 1, -1, -1), self.radius, self.radius)
        painter.fillPath(path, self.fill_color)
        pen = QPen(PALETTE["border"], 1)
        painter.setPen(pen)
        painter.drawPath(path)
        hl_pen = QPen(QColor(255, 255, 255, 10), 1)
        painter.setPen(hl_pen)
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), self.radius, self.radius)

class GlassButton(QPushButton):
    def __init__(self, text="", parent=None, primary=False):
        super().__init__(text, parent)
        self.primary = primary
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(36)
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))
        add_shadow(self, 10, 80, 2)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {"rgba(0, 225, 255, 0.2)" if primary else "rgba(25, 35, 60, 0.6)"};
                color: {"#ffffff" if primary else "#e0e0e0"};
                border: 1px solid {"rgba(0, 225, 255, 0.6)" if primary else "rgba(45, 59, 110, 0.6)"};
                border-radius: 6px;
                padding: 0 15px;
            }}
            QPushButton:hover {{
                background-color: {"rgba(0, 225, 255, 0.4)" if primary else "rgba(35, 45, 80, 0.8)"};
                border: 1px solid {"rgba(0, 225, 255, 0.8)" if primary else "rgba(65, 80, 130, 0.8)"};
            }}
            QPushButton:pressed {{
                background-color: {"rgba(0, 225, 255, 0.1)" if primary else "rgba(15, 20, 40, 0.8)"};
            }}
        """)

class GlassEntry(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet("""
            QLineEdit {
                background-color: rgba(10, 15, 25, 0.5);
                color: #ffffff;
                border: 1px solid rgba(45, 59, 110, 0.8);
                border-radius: 6px;
                padding: 0 10px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(0, 225, 255, 0.8);
                background-color: rgba(15, 20, 35, 0.7);
            }
        """)

class GlowLabel(QLabel):
    def __init__(self, text, color=PALETTE["accent"], size=10, bold=False):
        super().__init__(text)
        font = QFont("Segoe UI", size, QFont.Bold if bold else QFont.Normal)
        self.setFont(font)
        self.setStyleSheet(f"color: {color.name()};")
        if color in (PALETTE["accent"], PALETTE["success"], PALETTE["warning"], PALETTE["danger"]):
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(15)
            shadow.setColor(color)
            shadow.setOffset(0, 0)
            self.setGraphicsEffect(shadow)

class DuplicateDialog(QDialog):
    def __init__(self, parent, preview: FilePreview, dup: DuplicateInfo):
        super().__init__(parent)
        self.setWindowTitle("Duplicate Detected")
        self.setFixedSize(450, 300)
        self.setStyleSheet(f"background-color: {PALETTE['bg_base'].name()}; color: white;")
        self.result_action = DuplicateAction.KEEP_BOTH
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = GlowLabel("Duplicate Detected", PALETTE["warning"], 14, True)
        layout.addWidget(title)
        
        existing_path_str = str(dup.existing_path) if dup.existing_path else "(unknown)"
        info = QLabel(f"File: {preview.filename}\nDestination: {existing_path_str}\n"
                      f"New File Size: {preview.file_size:,} bytes")
        info.setStyleSheet("color: #cccccc;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        btn_layout = QHBoxLayout()
        btn_keep_both = GlassButton("Keep Both (Rename)")
        btn_replace = GlassButton("Replace Existing", primary=True)
        btn_skip = GlassButton("Skip")
        
        btn_keep_both.clicked.connect(lambda: self._choose(DuplicateAction.KEEP_BOTH))
        btn_replace.clicked.connect(self._confirm_replace)
        btn_skip.clicked.connect(lambda: self._choose(DuplicateAction.SKIP))
        
        btn_layout.addWidget(btn_keep_both)
        btn_layout.addWidget(btn_replace)
        btn_layout.addWidget(btn_skip)
        
        layout.addStretch()
        layout.addLayout(btn_layout)

    def _choose(self, action):
        self.result_action = action
        self.accept()
        
    def _confirm_replace(self):
        reply = QMessageBox.question(self, 'Confirm Replace', 
                                     'Replace the existing file? This cannot be undone.',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._choose(DuplicateAction.REPLACE)

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(500, 400)
        self.setStyleSheet(f"background-color: {PALETTE['bg_base'].name()}; color: white;")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Settings (Config logic moved here)"))
        btn = GlassButton("Close")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

class ActivityDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Activity Log")
        self.resize(600, 400)
        self.setStyleSheet(f"background-color: {PALETTE['bg_base'].name()}; color: white;")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Activity Log Placeholder"))
        btn = GlassButton("Close")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Organizer 2.0")
        self.resize(1100, 750)
        self.setMinimumSize(900, 600)
        
        self.undo_mgr = undo_module.UndoManager()
        self.monitor = None
        self._current_preview = None
        self.dispatcher = Dispatcher()
        
        self._build_ui()
        self._restore_last_folder()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), PALETTE["bg_base"])
        
        grad1 = QRadialGradient(QPoint(int(self.width()*0.2), int(self.height()*0.2)), 400)
        grad1.setColorAt(0, PALETTE["glow_blue"])
        grad1.setColorAt(1, Qt.transparent)
        painter.fillRect(self.rect(), grad1)
        
        grad2 = QRadialGradient(QPoint(int(self.width()*0.8), int(self.height()*0.8)), 500)
        grad2.setColorAt(0, PALETTE["glow_purple"])
        grad2.setColorAt(1, Qt.transparent)
        painter.fillRect(self.rect(), grad2)
        
        grad3 = QRadialGradient(QPoint(int(self.width()*0.5), int(self.height()*1.0)), 300)
        grad3.setColorAt(0, PALETTE["glow_cyan"])
        grad3.setColorAt(1, Qt.transparent)
        painter.fillRect(self.rect(), grad3)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        header = QHBoxLayout()
        title = GlowLabel("✨ Advanced File Organizer", PALETTE["accent"], 18, True)
        subtitle = QLabel("v2.0 • Smart & Safe")
        subtitle.setStyleSheet(f"color: {PALETTE['text_dim'].name()}; font: 12pt 'Segoe UI';")
        header.addWidget(title)
        header.addWidget(subtitle)
        header.addStretch()
        self.status_label = GlowLabel("● Ready", PALETTE["success"], 10, True)
        header.addWidget(self.status_label)
        main_layout.addLayout(header)
        
        folder_card = GlassPanel(self, radius=12)
        fc_layout = QHBoxLayout(folder_card)
        fc_layout.addWidget(QLabel("📁"))
        self.folder_entry = GlassEntry()
        fc_layout.addWidget(self.folder_entry, 1)
        self.browse_btn = GlassButton("Browse", primary=True)
        self.browse_btn.clicked.connect(self._browse)
        fc_layout.addWidget(self.browse_btn)
        self.recursive_var = QCheckBox("Include Subfolders")
        self.recursive_var.setStyleSheet("color: white;")
        fc_layout.addWidget(self.recursive_var)
        main_layout.addWidget(folder_card)
        
        action_card = GlassPanel(self, radius=12)
        ab_layout = QHBoxLayout(action_card)
        btn_analyze = GlassButton("Analyze")
        btn_preview = GlassButton("Preview")
        btn_organize = GlassButton("Organize", primary=True)
        btn_undo = GlassButton("Undo")
        self.watch_btn = GlassButton("Watch")
        btn_activity = GlassButton("Activity")
        btn_settings = GlassButton("Settings")
        
        btn_analyze.clicked.connect(self._run_analyze)
        btn_preview.clicked.connect(self._run_preview)
        btn_organize.clicked.connect(self._run_organize)
        btn_undo.clicked.connect(self._run_undo)
        self.watch_btn.clicked.connect(self._toggle_watch)
        btn_activity.clicked.connect(self._open_activity)
        btn_settings.clicked.connect(self._open_settings)
        
        for btn in [btn_analyze, btn_preview, btn_organize, btn_undo, self.watch_btn, btn_activity, btn_settings]:
            ab_layout.addWidget(btn)
        ab_layout.addStretch()
        main_layout.addWidget(action_card)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{ background-color: {PALETTE['border'].name()}; border: none; border-radius: 2px; }}
            QProgressBar::chunk {{ background-color: {PALETTE['accent'].name()}; border-radius: 2px; }}
        """)
        main_layout.addWidget(self.progress_bar)
        
        content_layout = QHBoxLayout()
        
        self.preview_panel = GlassPanel(self, radius=12)
        pp_layout = QVBoxLayout(self.preview_panel)
        self.preview_lbl = GlowLabel("File Preview", PALETTE["text"], 12, True)
        pp_layout.addWidget(self.preview_lbl)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Name", "Size", "Category", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{ background-color: transparent; color: white; border: none; }}
            QHeaderView::section {{ background-color: {PALETTE['surface_card'].name()}; color: {PALETTE['text_dim'].name()}; border: none; padding: 5px; }}
            QTableWidget::item {{ border-bottom: 1px solid {PALETTE['border'].name()}; padding: 5px; }}
        """)
        pp_layout.addWidget(self.table)
        content_layout.addWidget(self.preview_panel, 2)
        
        self.stats_panel = GlassPanel(self, radius=12)
        sp_layout = QVBoxLayout(self.stats_panel)
        sp_layout.addWidget(GlowLabel("Statistics", PALETTE["text"], 12, True))
        
        self.stat_cards = {}
        grid = QVBoxLayout()
        for stat in ["Total Files", "Organized", "Duplicates", "Errors", "Others", "Total Size"]:
            card = GlassPanel(self, radius=8, fill_color=PALETTE["surface_card"])
            clayout = QHBoxLayout(card)
            clayout.addWidget(QLabel(stat, styleSheet=f"color: {PALETTE['text_dim'].name()};"))
            clayout.addStretch()
            val_lbl = GlowLabel("0", PALETTE["text"], 14, True)
            self.stat_cards[stat] = val_lbl
            clayout.addWidget(val_lbl)
            grid.addWidget(card)
        sp_layout.addLayout(grid)
        
        sp_layout.addWidget(GlowLabel("Category Breakdown", PALETTE["text"], 12, True))
        self.cat_bars = {}
        cat_scroll = QScrollArea()
        cat_scroll.setWidgetResizable(True)
        cat_scroll.setStyleSheet("background: transparent; border: none;")
        cat_content = QWidget()
        cat_content.setStyleSheet("background: transparent;")
        cat_layout = QVBoxLayout(cat_content)
        
        for cat in CATEGORY_COLORS:
            row = QHBoxLayout()
            lbl = QLabel(f"{CATEGORY_ICONS.get(cat, '')} {cat}")
            lbl.setStyleSheet("color: white; width: 60px;")
            row.addWidget(lbl)
            bar = QProgressBar()
            bar.setTextVisible(False)
            bar.setFixedHeight(8)
            color = CATEGORY_COLORS[cat]
            bar.setStyleSheet(f"""
                QProgressBar {{ background-color: {PALETTE['border'].name()}; border-radius: 4px; }}
                QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}
            """)
            row.addWidget(bar)
            val = QLabel("0")
            val.setStyleSheet("color: #aaa;")
            row.addWidget(val)
            self.cat_bars[cat] = (bar, val)
            cat_layout.addLayout(row)
            
        cat_scroll.setWidget(cat_content)
        sp_layout.addWidget(cat_scroll)
        
        content_layout.addWidget(self.stats_panel, 1)
        main_layout.addLayout(content_layout)

    def _set_status(self, msg, color=PALETTE["text"]):
        self.status_label.setText(msg)
        self.status_label.setStyleSheet(f"color: {color.name()};")

    def _set_progress(self, pct):
        self.progress_bar.setValue(int(pct * 100))

    def _restore_last_folder(self):
        folder = config_manager.get("last_folder", "")
        if folder and Path(folder).exists():
            self.folder_entry.setText(folder)

    def _get_folder(self):
        raw = self.folder_entry.text().strip()
        if not raw:
            self._set_status('⚠ Please select a folder.', PALETTE['warning'])
            return None
        p = Path(raw)
        if not p.is_dir():
            self._set_status('❌ Invalid folder.', PALETTE['danger'])
            return None
        return p

    def _browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Organize")
        if folder:
            self.folder_entry.setText(folder)
            config_manager.set_value('last_folder', folder)
            self._set_status(f'📁 Selected: {folder}', PALETTE['text_dim'])

    def _update_stat_cards(self, total=0, moved=0, dups=0, errors=0, others=0, total_size=0):
        self.stat_cards["Total Files"].setText(str(total))
        self.stat_cards["Organized"].setText(str(moved))
        self.stat_cards["Duplicates"].setText(str(dups))
        self.stat_cards["Errors"].setText(str(errors))
        self.stat_cards["Others"].setText(str(others))
        size_mb = total_size / (1024*1024)
        self.stat_cards["Total Size"].setText(f"{size_mb:.1f} MB")

    def _clear_preview(self):
        self.table.setRowCount(0)
        self.preview_lbl.setText("File Preview (0 files)")

    def _render_preview(self, result: org_module.PreviewResult):
        self._clear_preview()
        files = result.file_previews[:200]
        self.preview_lbl.setText(f"File Preview ({result.total_files} files)")
        self.table.setRowCount(len(files))
        for i, f in enumerate(files):
            self.table.setItem(i, 0, QTableWidgetItem(f.filename))
            size_kb = f.file_size / 1024
            self.table.setItem(i, 1, QTableWidgetItem(f"{size_kb:.1f} KB"))
            
            cat_item = QTableWidgetItem(f"{CATEGORY_ICONS.get(f.destination_category, '')} {f.destination_category}")
            cat_item.setForeground(QColor(CATEGORY_COLORS.get(f.destination_category, "#ffffff")))
            self.table.setItem(i, 2, cat_item)
            
            status_item = QTableWidgetItem("Ready")
            status_item.setForeground(PALETTE["success"])
            if f.is_name_conflict or f.is_content_duplicate:
                status_item.setText("Duplicate")
                status_item.setForeground(PALETTE["warning"])
            self.table.setItem(i, 3, status_item)

    def _run_analyze(self):
        folder = self._get_folder()
        if not folder: return
        self._set_status('🔍 Analyzing...', PALETTE['accent'])
        self._set_progress(0.3)
        def _worker():
            res = org_module.scan_folder(folder, self.recursive_var.isChecked())
            self.dispatcher.dispatch.emit(lambda: self._on_analyze_done(res))
        threading.Thread(target=_worker, daemon=True).start()

    def _on_analyze_done(self, result):
        self._current_preview = result
        self._set_progress(1.0)
        self._update_stat_cards(total=result.total_files, moved=result.organizable, 
                                dups=result.name_conflicts + result.content_duplicates, 
                                others=result.going_to_others, total_size=result.total_size)
        self._update_bars(result.category_counts, result.total_files)
        self._set_status(f'✔ Analysis done — {result.total_files} files.', PALETTE['success'])

    def _update_bars(self, counts, total):
        for cat, (bar, val_lbl) in self.cat_bars.items():
            cnt = counts.get(cat, 0)
            val_lbl.setText(str(cnt))
            bar.setMaximum(max(total, 1))
            bar.setValue(cnt)

    def _run_preview(self):
        folder = self._get_folder()
        if not folder: return
        self._clear_preview()
        self._set_status('👁 Building preview...', PALETTE['accent'])
        self._set_progress(0.0)
        def _worker():
            res = org_module.scan_folder(folder, self.recursive_var.isChecked())
            self.dispatcher.dispatch.emit(lambda: self._on_preview_done(res))
        threading.Thread(target=_worker, daemon=True).start()

    def _on_preview_done(self, result):
        self._current_preview = result
        self._render_preview(result)
        self._set_progress(1.0)
        self._update_stat_cards(total=result.total_files, moved=result.organizable, 
                                dups=result.name_conflicts + result.content_duplicates, 
                                others=result.going_to_others, total_size=result.total_size)
        self._update_bars(result.category_counts, result.total_files)
        self._set_status(f'👁 Preview ready — {result.total_files} files.', PALETTE['accent'])

    def _run_organize(self):
        folder = self._get_folder()
        if not folder: return
        
        reply = QMessageBox.question(self, 'Confirm', f'Ready to organize files in {folder}?', 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No: return
        
        self._set_status('⚡ Organizing...', PALETTE['accent'])
        self._set_progress(0.0)
        self._clear_preview()
        
        def _on_progress(filename, cat, idx, total_f):
            pct = idx / max(total_f, 1)
            self.dispatcher.dispatch.emit(lambda: self._set_progress(pct))
            self.dispatcher.dispatch.emit(lambda: self._set_status(f'⚡ {idx}/{total_f} {filename} → {cat}', PALETTE['accent']))

        def _on_duplicate(fp: FilePreview, dup: DuplicateInfo) -> str:
            result_holder = [DuplicateAction.KEEP_BOTH]
            done_event = threading.Event()
            def _show_dialog():
                dlg = DuplicateDialog(self, fp, dup)
                dlg.exec()
                result_holder[0] = dlg.result_action
                done_event.set()
            self.dispatcher.dispatch.emit(_show_dialog)
            done_event.wait()
            return result_holder[0]

        def _worker():
            org_result = org_module.organize_folder(folder, self.recursive_var.isChecked(), 
                                                    _on_progress, _on_duplicate, self.undo_mgr)
            self.dispatcher.dispatch.emit(lambda: self._on_organize_done(org_result, folder))
            
        threading.Thread(target=_worker, daemon=True).start()

    def _on_organize_done(self, result, folder):
        self._set_progress(1.0)
        self._update_stat_cards(total=result.total_files, moved=result.moved, 
                                dups=0, errors=result.errors,
                                others=result.category_stats.get('Others', 0), total_size=result.total_size)
        self._update_bars(result.category_stats, result.total_files)
        
        if result.errors:
            self._set_status(f'⚠ Done: {result.moved} moved, {result.errors} error(s).', PALETTE['warning'])
            QMessageBox.warning(self, "Completed with Errors",
                                f"Organized {result.moved} files.\n{result.errors} error(s) occurred.\n\nDetails:\n" +
                                "\n".join(result.error_messages[:10]))
        else:
            self._set_status(f'✔ Done! {result.moved} files organized.', PALETTE['success'])
            QMessageBox.information(self, "Success", f"✔ {result.moved} files organized successfully!")
            
    def _run_undo(self):
        if not self.undo_mgr.can_undo():
            self._set_status('↩ Nothing to undo.', PALETTE['text_dim'])
            QMessageBox.information(self, 'Undo', 'No operation to undo.')
            return
        
        reply = QMessageBox.question(self, 'Undo', 'Restore files to original locations?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No: return
        
        self._set_status('↩ Undoing...', PALETTE['warning'])
        self._set_progress(0.3)
        def _worker():
            res = self.undo_mgr.undo_last()
            self.dispatcher.dispatch.emit(lambda: self._on_undo_done(res))
        threading.Thread(target=_worker, daemon=True).start()
        
    def _on_undo_done(self, result):
        self._set_progress(1.0)
        restored = result['restored']
        errors = result.get('errors', [])
        if errors:
            self._set_status(f'↩ Restored {restored}, {len(errors)} errors.', PALETTE['warning'])
        else:
            self._set_status(f'↩ Restored {restored} files.', PALETTE['success'])
            QMessageBox.information(self, "Undo", f"✔ {restored} files restored.")

    def _toggle_watch(self):
        if not WATCHDOG_AVAILABLE:
            QMessageBox.critical(self, "Error", "Install watchdog to use monitoring.")
            return
        if self.monitor and self.monitor.is_running:
            self.monitor.stop()
            self.monitor = None
            self.watch_btn.setText("Watch")
            self._set_status('⏹ Monitoring stopped.', PALETTE['text_dim'])
            return
        folder = self._get_folder()
        if not folder: return
        
        def _on_organized(filename, status):
            self.dispatcher.dispatch.emit(lambda: self._set_status(f'👁 {filename} {status}', PALETTE['success']))
            
        self.monitor = FolderMonitor(folder, _on_organized)
        self.monitor.start()
        self.watch_btn.setText("● Watching")
        self._set_status(f'👁 Monitoring: {folder}', PALETTE['success'])

    def _open_activity(self):
        ActivityDialog(self).exec()

    def _open_settings(self):
        SettingsDialog(self).exec()

    def closeEvent(self, event):
        if self.monitor and self.monitor.is_running:
            self.monitor.stop()
        folder = self.folder_entry.text().strip()
        if folder:
            config_manager.set_value('last_folder', folder)
        event.accept()

    def run(self):
        pass
