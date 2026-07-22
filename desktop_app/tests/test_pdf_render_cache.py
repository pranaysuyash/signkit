"""Tests for PDFViewer's page-render cache (desktop_app/pdf/viewer.py).

Re-rendering a pdfium bitmap (page.render at ~150 DPI, PIL conversion, QImage
construction) on every page switch and every zoom change is real CPU/IO work.
Users routinely revisit the same page/zoom combination — paging back and
forth, or toggling between two zoom levels — so PDFViewer now caches
rendered QPixmaps keyed by (page, zoom, dpi) and only calls
PDFRenderer.render_page again on a genuine cache miss.
"""

import tempfile
from pathlib import Path

import pytest

pytest.importorskip("reportlab")
pytest.importorskip("pypdfium2")

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from desktop_app.pdf.viewer import PDFViewer


@pytest.fixture
def two_page_pdf() -> str:
    temp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    temp.close()

    pdf = canvas.Canvas(temp.name, pagesize=letter)
    pdf.drawString(72, 700, "Page one")
    pdf.showPage()
    pdf.drawString(72, 700, "Page two")
    pdf.showPage()
    pdf.save()

    yield temp.name
    Path(temp.name).unlink(missing_ok=True)


def test_revisiting_same_page_and_zoom_skips_rerender(two_page_pdf, monkeypatch):
    viewer = PDFViewer()
    assert viewer.open_pdf(two_page_pdf)

    render_calls = []
    original_render_page = viewer.renderer.render_page

    def counting_render_page(*args, **kwargs):
        render_calls.append((args, kwargs))
        return original_render_page(*args, **kwargs)

    monkeypatch.setattr(viewer.renderer, "render_page", counting_render_page)

    # open_pdf() already rendered (page 0, zoom=1.0) before the spy was
    # installed, so use a zoom level not yet cached to force a genuine miss.
    viewer.zoom_level = 1.23
    viewer._render_current_page()
    assert len(render_calls) == 1

    # Re-rendering the identical (page, zoom, dpi) must hit the cache.
    viewer._render_current_page()
    assert len(render_calls) == 1, "expected cache hit, but render_page was called again"

    # Navigate to page 2 (a real cache miss) then back to page 1 (a hit).
    viewer.next_page()
    assert len(render_calls) == 2
    viewer.previous_page()
    assert len(render_calls) == 2, "returning to a previously rendered page should hit the cache"

    viewer.close_pdf()


def test_zoom_change_invalidates_but_returning_to_prior_zoom_hits_cache(two_page_pdf, monkeypatch):
    viewer = PDFViewer()
    assert viewer.open_pdf(two_page_pdf)

    # Establish a known baseline zoom/cache entry before installing the spy
    # (open_pdf() defaults to "Whole Page" fit, an arbitrary computed zoom).
    viewer.zoom_level = 1.0
    viewer._render_current_page()

    render_calls = []
    original_render_page = viewer.renderer.render_page
    monkeypatch.setattr(
        viewer.renderer, "render_page",
        lambda *a, **k: (render_calls.append(1) or original_render_page(*a, **k)),
    )

    viewer.zoom_level = 1.5
    viewer._render_current_page()
    assert len(render_calls) == 1  # new zoom -> cache miss

    viewer.zoom_level = 1.0
    viewer._render_current_page()
    assert len(render_calls) == 1  # back to the first (pre-cached) zoom -> cache hit

    viewer.close_pdf()


def test_cache_is_cleared_when_a_new_pdf_is_opened(two_page_pdf):
    viewer = PDFViewer()
    assert viewer.open_pdf(two_page_pdf)
    assert len(viewer._page_render_cache) >= 1

    assert viewer.open_pdf(two_page_pdf)
    # A fresh open_pdf() must not silently serve stale entries from the
    # previous document's cache, even if it happens to be the same file path.
    assert len(viewer._page_render_cache) == 1


def test_cache_is_bounded(two_page_pdf):
    """The cache must not grow without bound across many zoom levels."""
    viewer = PDFViewer()
    assert viewer.open_pdf(two_page_pdf)

    for i in range(30):
        viewer.zoom_level = 1.0 + i * 0.01
        viewer._render_current_page()

    assert len(viewer._page_render_cache) <= viewer._PAGE_RENDER_CACHE_MAX
    viewer.close_pdf()
