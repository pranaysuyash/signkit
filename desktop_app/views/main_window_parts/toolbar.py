from __future__ import annotations

import sys

from typing import cast

from PySide6.QtCore import QObject, QSize, Qt
from PySide6.QtGui import QAction
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QToolBar, QWidget

from desktop_app.resources.icons import get_icon


class ToolbarMixin:
    """Creates the macOS-style toolbar with commonly used actions."""

    def _setup_main_toolbar(self) -> None:
        if sys.platform != "darwin":
            self.undo_action = None
            self.redo_action = None
            self._toolbar = None
            self._toolbar_open_action = None
            self._toolbar_export_action = None
            self._toolbar_save_action = None
            self._toolbar_help_action = None
            return

        toolbar = QToolBar("Quick Actions", cast(QWidget, self))
        toolbar.setObjectName("mainToolbar")
        toolbar.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(22, 22))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        # Remove custom stylesheet to allow native macOS styling
        # The unified title/toolbar handles appearance automatically

        parent = cast(QObject, self)

        # Primary workflow actions
        open_action = QAction(get_icon("open"), "Open", parent)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open an image for signature extraction or a PDF for signing")
        open_action.triggered.connect(self._handle_toolbar_open)
        toolbar.addAction(open_action)

        export_action = QAction(get_icon("export"), "Export", parent)
        export_action.setShortcut("Meta+E")
        export_action.setStatusTip("Export the processed signature to a file")
        export_action.triggered.connect(self._handle_toolbar_export)
        toolbar.addAction(export_action)

        save_library_action = QAction(get_icon("save"), "Save", parent)
        save_library_action.setShortcut(QKeySequence.StandardKey.Save)
        save_library_action.setStatusTip("Save the signature to your personal library for later use")
        save_library_action.triggered.connect(self.on_save_to_library)
        toolbar.addAction(save_library_action)

        self.addToolBar(toolbar)
        self.setUnifiedTitleAndToolBarOnMac(True)

        self._toolbar = toolbar
        self._toolbar_open_action = open_action
        self._toolbar_export_action = export_action
        self._toolbar_save_action = save_library_action
        self._toolbar_help_action = None

        self._update_toolbar_for_tab(self.tab_widget.currentIndex())
        self._refresh_toolbar_action_states()

    def _handle_toolbar_open(self) -> None:
        pdf_index = getattr(self, "_pdf_tab_index", -1)
        if pdf_index >= 0 and getattr(self, "tab_widget", None) and self.tab_widget.currentIndex() == pdf_index:
            if hasattr(self, "_on_pdf_tab_open"):
                self._on_pdf_tab_open()
            elif hasattr(self, "on_pdf_open"):
                self.on_pdf_open()
            return
        if hasattr(self, "on_open"):
            self.on_open()

    def _handle_toolbar_export(self) -> None:
        pdf_index = getattr(self, "_pdf_tab_index", -1)
        if pdf_index >= 0 and getattr(self, "tab_widget", None) and self.tab_widget.currentIndex() == pdf_index:
            if hasattr(self, "_on_pdf_tab_save"):
                self._on_pdf_tab_save()
            elif hasattr(self, "on_pdf_save"):
                self.on_pdf_save()
            return
        if hasattr(self, "on_export"):
            self.on_export()

    def _update_toolbar_for_tab(self, index: int) -> None:
        if not getattr(self, "_toolbar_open_action", None):
            return
        pdf_index = getattr(self, "_pdf_tab_index", -1)
        extraction_index = getattr(self, "_extraction_tab_index", 0)
        is_pdf_tab = pdf_index >= 0 and index == pdf_index

        # Keep consistent text to prevent visual shifting
        self._toolbar_open_action.setText("Open")
        self._toolbar_export_action.setText("Export")
        if self._toolbar_save_action:
            self._toolbar_save_action.setVisible(not is_pdf_tab)

        self._refresh_toolbar_action_states()

    def _refresh_toolbar_action_states(self) -> None:
        if not getattr(self, "_toolbar_open_action", None):
            return
        current_index = self.tab_widget.currentIndex() if getattr(self, "tab_widget", None) else -1
        extraction_index = getattr(self, "_extraction_tab_index", 0)
        pdf_index = getattr(self, "_pdf_tab_index", -1)

        if current_index == extraction_index:
            export_enabled = getattr(self, "export_btn", None)
            save_enabled = getattr(self, "save_to_library_btn", None)
            if export_enabled:
                self._toolbar_export_action.setEnabled(export_enabled.isEnabled())
            if self._toolbar_save_action and save_enabled:
                self._toolbar_save_action.setEnabled(save_enabled.isEnabled())
        elif current_index == pdf_index:
            has_pdf = bool(getattr(self, "_current_pdf_path", None))
            self._toolbar_export_action.setEnabled(has_pdf)
            if self._toolbar_save_action:
                self._toolbar_save_action.setEnabled(False)
        else:
            self._toolbar_export_action.setEnabled(True)
            if self._toolbar_save_action:
                self._toolbar_save_action.setEnabled(True)


__all__ = ["ToolbarMixin"]
