"""Process-wide serialization for pypdfium2 operations."""

from __future__ import annotations

from contextlib import contextmanager
from threading import RLock
from typing import Iterator


PDFIUM_LOCK = RLock()


@contextmanager
def pdfium_operation() -> Iterator[None]:
    """Serialize one complete PDFium operation, including native cleanup."""

    with PDFIUM_LOCK:
        yield
