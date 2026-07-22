"""Standalone utility functions and helpers for the extraction tab.

This module contains code that has no dependency on ``self`` or any mixin
state.  Everything here is importable from any module without circular
import risk.
"""

from __future__ import annotations

import sys
from typing import Any, Callable, Dict, Optional

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QPushButton, QSizePolicy, QWidget

# ---------------------------------------------------------------------------
# Async helpers
# ---------------------------------------------------------------------------
#
# AsyncRunner/run_async/dispatch are generic (no dependency on the extraction
# tab) and now live in desktop_app/widgets/async_utils.py, which is a valid
# shared dependency for both desktop_app/views/ and desktop_app/pdf/.
# Re-exported here for backward compatibility with existing imports.

from desktop_app.widgets.async_utils import AsyncRunner, dispatch, run_async  # noqa: F401


def run_signature_preview(
    *,
    extractor,
    is_forensic: bool,
    session_id: str,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    threshold_value: int,
    color_hex: str,
    auto_clean: bool,
    persist_fn: Callable[[], None],
    request_id: int,
    start_time: float,
) -> Dict[str, Any]:
    """Run signature extraction + quality analysis off the UI thread.

    This is the body of what used to be ``on_preview`` before extraction and
    quality analysis were moved onto a QThreadPool worker. It has no
    dependency on any Qt widget, so it is safe to run from a worker thread
    and safe to unit-test without a QApplication.

    All failure modes are captured in the returned dict rather than raised,
    so the caller's ``AsyncRunner.finished`` signal (queued back onto the
    main/UI thread) is the single delivery path for both success and error
    outcomes. This keeps the request_id staleness check in one place instead
    of duplicating it across a success signal and an error signal.

    Returns a dict with keys:
      - request_id, start_time: echoed back so the UI-thread handler can
        discard results superseded by a newer request.
      - ok: whether extraction succeeded.
      - png_bytes, quality, quality_error: present when ok is True.
      - error: the exception, present when ok is False.
    """
    try:
        if is_forensic:
            png_bytes = extractor.process_selection_kmeans(
                session_id=session_id, x1=x1, y1=y1, x2=x2, y2=y2, k=2
            )
        else:
            png_bytes = extractor.process_selection(
                session_id=session_id,
                x1=x1, y1=y1, x2=x2, y2=y2,
                color=color_hex,
                threshold=threshold_value,
                auto_clean=auto_clean,
            )

        # Best-effort backend sync; must never fail the local preview.
        try:
            persist_fn()
        except Exception:
            pass  # persist_fn already logs; local processing is source of truth.

        quality = None
        quality_error = None
        try:
            quality = extractor.analyze_quality(
                session_id=session_id, x1=x1, y1=y1, x2=x2, y2=y2
            )
        except Exception as exc:
            quality_error = exc

        return {
            "ok": True,
            "request_id": request_id,
            "start_time": start_time,
            "png_bytes": png_bytes,
            "quality": quality,
            "quality_error": quality_error,
        }
    except Exception as exc:
        return {
            "ok": False,
            "request_id": request_id,
            "start_time": start_time,
            "error": exc,
        }


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _rgba(color: QColor) -> str:
    """Return a Qt stylesheet-friendly RGBA string for *color*."""
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"


# ---------------------------------------------------------------------------
# Button factory
# ---------------------------------------------------------------------------

def _create_button(
    text: str = "",
    parent: QWidget = None,
    *,
    use_modern_mac: bool = None,
    primary: bool = False,
    destructive: bool = False,
    color: str = 'blue',
    compact: bool = False,
) -> QPushButton:
    """Create a platform-appropriate button.

    On macOS the function tries to use ``ModernMacButton`` (glassmorphism).
    Falls back to a standard ``QPushButton`` on other platforms or if the
    custom widget is unavailable.
    """
    if use_modern_mac is None:
        use_modern_mac = sys.platform == "darwin"

    resolved_color = 'red' if destructive and color == 'blue' else color

    if use_modern_mac:
        try:
            from desktop_app.widgets.modern_mac_button import ModernMacButton
            btn = ModernMacButton(
                text, parent,
                primary=primary,
                color=resolved_color,
                glass=True,
                compact=compact,
            )
            if destructive:
                btn.setProperty("destructive", True)
            return btn
        except (NameError, TypeError):
            pass

    btn = QPushButton(text, parent)
    if primary:
        btn.setProperty("primary", True)
    if destructive:
        btn.setProperty("destructive", True)
    if compact:
        btn.setProperty("compact", True)
    return btn


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------

def _clear_layout(layout) -> None:
    """Remove and delete all items from *layout*."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()
        else:
            sub = item.layout()
            if sub:
                _clear_layout(sub)
