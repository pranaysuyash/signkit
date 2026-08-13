"""Accessible local confirmation dialog for ranked signature candidates."""

from __future__ import annotations

from typing import Optional, Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from desktop_app.processing.extractor import SignatureCandidate


class SignatureCandidateDialog(QDialog):
    """Let the operator inspect and confirm a ranked auto-detect candidate."""

    def __init__(
        self,
        candidates: Sequence[SignatureCandidate],
        source_image: Optional[QImage],
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Confirm signature region")
        self.setModal(True)
        self.setMinimumWidth(420)
        self._candidates = tuple(candidates)
        self._source_image = source_image

        layout = QVBoxLayout(self)
        intro = QLabel(
            "Auto-detect found ranked candidates. Confirm the region before previewing it."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        form = QFormLayout()
        self.candidate_combo = QComboBox(self)
        self.candidate_combo.setAccessibleName("Signature candidate")
        for index, candidate in enumerate(self._candidates, start=1):
            x1, y1, x2, y2 = candidate.bbox
            self.candidate_combo.addItem(
                f"Candidate {index}: {candidate.source} · score {candidate.confidence:.2f}",
                userData=index - 1,
            )
            self.candidate_combo.setItemData(
                index - 1,
                f"Bounding box: ({x1}, {y1}) to ({x2}, {y2})",
                Qt.ItemDataRole.ToolTipRole,
            )
        form.addRow("Region", self.candidate_combo)
        layout.addLayout(form)

        self.preview = QLabel("Preview unavailable")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(360, 180)
        self.preview.setFrameShape(QFrame.Shape.Panel)
        self.preview.setFrameShadow(QFrame.Shadow.Sunken)
        self.preview.setAccessibleName("Selected signature candidate preview")
        layout.addWidget(self.preview)

        self.details = QLabel()
        self.details.setWordWrap(True)
        self.details.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.details)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.candidate_combo.currentIndexChanged.connect(self._render_candidate)
        if self._candidates:
            self._render_candidate(0)
        else:
            buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    def selected_candidate(self) -> Optional[SignatureCandidate]:
        """Return the confirmed candidate, or ``None`` when no choice exists."""

        if not self._candidates:
            return None
        index = self.candidate_combo.currentData()
        if not isinstance(index, int) or not 0 <= index < len(self._candidates):
            return None
        return self._candidates[index]

    def _render_candidate(self, index: int) -> None:
        if not 0 <= index < len(self._candidates):
            self.preview.clear()
            self.details.clear()
            return
        candidate = self._candidates[index]
        x1, y1, x2, y2 = candidate.bbox
        self.details.setText(
            f"Source: {candidate.source}\n"
            f"Ranking score: {candidate.confidence:.2f} (not a probability)\n"
            f"Bounds: ({x1}, {y1}) to ({x2}, {y2})"
        )
        if self._source_image is None or self._source_image.isNull():
            self.preview.setText("Preview unavailable")
            return
        image_bounds = self._source_image.rect()
        if x2 <= x1 or y2 <= y1:
            self.preview.setText("Preview unavailable")
            return
        # Use explicit clipping so malformed detector output cannot request an
        # unbounded QImage copy.
        left = max(image_bounds.left(), min(x1, image_bounds.right()))
        top = max(image_bounds.top(), min(y1, image_bounds.bottom()))
        right = max(left + 1, min(x2, image_bounds.right() + 1))
        bottom = max(top + 1, min(y2, image_bounds.bottom() + 1))
        crop = self._source_image.copy(left, top, right - left, bottom - top)
        pixmap = QPixmap.fromImage(crop).scaled(
            self.preview.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview.setPixmap(pixmap)


__all__ = ["SignatureCandidateDialog"]
