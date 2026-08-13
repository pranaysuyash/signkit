from __future__ import annotations

from pathlib import Path

from reportlab.pdfgen import canvas

from desktop_app.pdf.document_runtime import IsolatedDocumentRuntime


def _make_pdf(path: Path) -> None:
    pdf = canvas.Canvas(str(path))
    pdf.drawString(72, 720, "Signature")
    pdf.line(72, 680, 260, 680)
    pdf.showPage()
    pdf.save()


def test_isolated_runtime_detects_and_renders_in_child_process(tmp_path: Path) -> None:
    pdf_path = tmp_path / "worker.pdf"
    _make_pdf(pdf_path)
    runtime = IsolatedDocumentRuntime(timeout_seconds=30)

    candidates = runtime.detect_page(str(pdf_path), 0)
    png = runtime.render_page(str(pdf_path), 0, scale=0.5)

    assert isinstance(candidates, list)
    assert png.startswith(b"\x89PNG\r\n\x1a\n")


def test_isolated_runtime_turns_worker_timeout_into_structured_error(tmp_path: Path) -> None:
    runtime = IsolatedDocumentRuntime(timeout_seconds=0.001)

    try:
        runtime.render_page(str(tmp_path / "missing.pdf"), 0)
    except Exception as exc:
        assert type(exc).__name__ == "DocumentRuntimeError"
        assert str(exc) in {"document_worker_timeout", "document_worker_exit:1", "document_worker_exit:-9"}
    else:
        raise AssertionError("expected isolated worker failure")


def test_isolated_runtime_uses_a_disposable_process_for_each_operation(tmp_path: Path) -> None:
    pdf_path = tmp_path / "worker-repeated.pdf"
    _make_pdf(pdf_path)
    runtime = IsolatedDocumentRuntime(timeout_seconds=30)

    first = runtime.render_page(str(pdf_path), 0, scale=0.25)
    second = runtime.render_page(str(pdf_path), 0, scale=0.25)

    assert first.startswith(b"\x89PNG\r\n\x1a\n")
    assert second.startswith(b"\x89PNG\r\n\x1a\n")
