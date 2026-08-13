#!/usr/bin/env python3
"""Run a native Qt proof of the signature candidate confirmation dialog.

This intentionally does not set ``QT_QPA_PLATFORM=offscreen``. It is a local
operator-observation aid and must be run in a session with a usable desktop.
The output image is an ignored artifact when written below ``.codex-test-tmp``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox

# Running a tools script by path does not automatically put the repository
# root on sys.path. Keep the proof self-contained and runnable from any cwd.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from desktop_app.processing.extractor import SignatureCandidate
from desktop_app.views.signature_candidate_dialog import SignatureCandidateDialog


def _image() -> QImage:
    image = QImage(640, 480, QImage.Format.Format_RGB32)
    image.fill(0xFFFFFFFF)
    return image


def _buttons(dialog: SignatureCandidateDialog) -> QDialogButtonBox:
    buttons = dialog.findChild(QDialogButtonBox)
    if buttons is None:
        raise AssertionError("candidate dialog has no button box")
    return buttons


def _show(dialog: SignatureCandidateDialog) -> None:
    dialog.show()
    if not QTest.qWaitForWindowExposed(dialog, 3000):
        raise AssertionError("candidate dialog did not become visible in native GUI")
    QTest.qWait(100)


def run(output: Path | None) -> dict[str, object]:
    app = QApplication.instance() or QApplication([])
    candidates = (
        SignatureCandidate((40, 60, 300, 220), 0.91, "blue-ink"),
        SignatureCandidate((330, 240, 620, 430), 0.80, "grayscale-fallback"),
    )

    cancel_dialog = SignatureCandidateDialog(candidates, _image())
    _show(cancel_dialog)
    cancel_dialog.candidate_combo.setFocus(Qt.FocusReason.OtherFocusReason)
    if not cancel_dialog.candidate_combo.hasFocus():
        raise AssertionError("candidate selector did not receive keyboard focus")
    if cancel_dialog.preview.pixmap() is None or cancel_dialog.preview.pixmap().isNull():
        raise AssertionError("native candidate preview did not render")
    if "not a probability" not in cancel_dialog.details.text():
        raise AssertionError("non-probabilistic score boundary is not visible")
    screenshot_sha256 = None
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        if not cancel_dialog.grab().save(str(output)):
            raise AssertionError(f"could not save screenshot: {output}")
        screenshot_sha256 = hashlib.sha256(output.read_bytes()).hexdigest()
    cancel_button = _buttons(cancel_dialog).button(QDialogButtonBox.StandardButton.Cancel)
    if cancel_button is None:
        raise AssertionError("candidate dialog has no Cancel button")
    QTest.mouseClick(cancel_button, Qt.MouseButton.LeftButton)
    QTest.qWait(50)
    if cancel_dialog.result() != int(QDialog.DialogCode.Rejected):
        raise AssertionError("cancel did not reject the candidate dialog")
    cancel_dialog.close()

    confirm_dialog = SignatureCandidateDialog(candidates, _image())
    _show(confirm_dialog)
    confirm_dialog.candidate_combo.setCurrentIndex(1)
    ok_button = _buttons(confirm_dialog).button(QDialogButtonBox.StandardButton.Ok)
    if ok_button is None:
        raise AssertionError("candidate dialog has no OK button")
    QTest.mouseClick(ok_button, Qt.MouseButton.LeftButton)
    QTest.qWait(50)
    if confirm_dialog.result() != int(QDialog.DialogCode.Accepted):
        raise AssertionError("confirm did not accept the candidate dialog")
    if confirm_dialog.selected_candidate() != candidates[1]:
        raise AssertionError("confirm did not preserve the selected candidate")
    confirm_dialog.close()

    failure_dialog = SignatureCandidateDialog(candidates, None)
    _show(failure_dialog)
    if failure_dialog.preview.text() != "Preview unavailable":
        raise AssertionError("missing source image did not show bounded failure messaging")
    failure_dialog.close()
    app.processEvents()
    return {
        "native_gui": True,
        "cancel": "rejected",
        "confirm": "accepted candidate 2",
        "keyboard_focus": True,
        "preview": "rendered",
        "failure_message": "Preview unavailable",
        "screenshot": str(output) if output else None,
        "screenshot_sha256": screenshot_sha256,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional screenshot path")
    args = parser.parse_args()
    print(json.dumps(run(args.output), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
