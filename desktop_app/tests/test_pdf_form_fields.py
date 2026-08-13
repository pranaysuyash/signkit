"""Tests for native PDF form field inspection and editing."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

pytest.importorskip("reportlab")
pytest.importorskip("PySide6")
pytest.importorskip("fitz")

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from desktop_app.pdf.form_fields import PdfFormFieldEditor


@pytest.fixture(autouse=True)
def enable_fitz_for_forms(monkeypatch) -> None:
    """Ensure form editing tests run with the policy flag enabled."""
    monkeypatch.setenv("SIGNKIT_ALLOW_PYMUPDF_SIGNING", "1")


@pytest.fixture
def sample_form_pdf() -> str:
    """Create a PDF with native text, checkbox, combo, and radio widgets."""
    temp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    temp.close()

    cnv = canvas.Canvas(temp.name, pagesize=letter)
    cnv.setFont("Helvetica", 12)
    cnv.drawString(72, 720, "Full Name:")
    cnv.acroForm.textfield(name="full_name", tooltip="Full Name", x=150, y=710, width=220, height=20)
    cnv.drawString(72, 680, "Agree:")
    cnv.acroForm.checkbox(name="agree_terms", tooltip="Agree Terms", x=150, y=675, buttonStyle="check", checked=False)
    cnv.drawString(72, 640, "Country:")
    cnv.acroForm.choice(
        name="country",
        tooltip="Country",
        value="US",
        options=["US", "CA", "UK"],
        x=150,
        y=630,
        width=120,
        height=20,
    )
    cnv.drawString(72, 600, "Plan:")
    cnv.acroForm.radio(name="plan", value="basic", selected=True, x=150, y=595, tooltip="Plan")
    cnv.acroForm.radio(name="plan", value="pro", selected=False, x=180, y=595, tooltip="Plan")
    cnv.showPage()
    cnv.save()

    yield temp.name
    Path(temp.name).unlink(missing_ok=True)


def test_detect_native_form_fields(sample_form_pdf: str) -> None:
    """Detect native widgets from a generated AcroForm PDF."""
    editor = PdfFormFieldEditor()
    fields = editor.detect_pdf(sample_form_pdf)

    names = {field.field_name for field in fields}
    types = {field.field_type.lower() for field in fields}

    assert "full_name" in names
    assert "agree_terms" in names
    assert "country" in names
    assert "plan" in names
    assert any("text" in field_type for field_type in types)
    assert any("check" in field_type for field_type in types)
    assert any("choice" in field_type or "combo" in field_type for field_type in types)
    assert any("radio" in field_type for field_type in types)


def test_fill_native_form_field(sample_form_pdf: str) -> None:
    """Fill a text field and verify the updated PDF saves correctly."""
    editor = PdfFormFieldEditor()
    output_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name

    try:
        changed = editor.fill_field(sample_form_pdf, output_path, "full_name", value="Pranay")
        assert changed is True

        reopened = editor.detect_pdf(output_path)
        text_field = next(field for field in reopened if field.field_name == "full_name")
        assert text_field.value == "Pranay"
    finally:
        Path(output_path).unlink(missing_ok=True)


def test_fill_choice_and_radio_fields(sample_form_pdf: str) -> None:
    """Fill combo and radio widgets using their native form values."""
    editor = PdfFormFieldEditor()
    combo_output = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
    radio_output = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name

    try:
        assert editor.fill_field(sample_form_pdf, combo_output, "country", value="CA") is True
        assert editor.fill_field(combo_output, radio_output, "plan", value="pro") is True

        reopened = editor.detect_pdf(radio_output)
        country = next(field for field in reopened if field.field_name == "country")
        assert country.value == "CA"

        plans = [field.value for field in reopened if field.field_name == "plan"]
        assert "pro" in plans
        assert "Off" in plans
    finally:
        Path(combo_output).unlink(missing_ok=True)
        Path(radio_output).unlink(missing_ok=True)
