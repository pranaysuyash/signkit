"""Template persistence tests for reusable signature placement templates."""

from __future__ import annotations

import json
import time
from pathlib import Path

from desktop_app.pdf.template_store import (
    SignaturePlacementTemplate,
    create_template,
    delete_template,
    get_template,
    list_templates,
    save_template,
    _safe_templates_payload,
)
from desktop_app.workflows.models import SignatureFieldBinding


def _configure_store_path(monkeypatch, path: Path) -> None:
    """Point template store to an isolated temporary file."""
    monkeypatch.setattr("desktop_app.pdf.template_store.APP_DIR", str(path))
    monkeypatch.setattr(
        "desktop_app.pdf.template_store.TEMPLATES_FILE",
        str(path / "pdf_templates.json"),
    )


def test_template_store_round_trip(monkeypatch, tmp_path: Path) -> None:
    """Persist and retrieve templates in descending updated_at order."""
    _configure_store_path(monkeypatch, tmp_path)

    first = create_template(
        signature_path="/tmp/signature-a.png",
        page_index=0,
        x_ratio=0.1,
        y_ratio=0.2,
        width_ratio=0.3,
        height_ratio=0.04,
        name="First Template",
    )
    time.sleep(0.01)
    second = create_template(
        signature_path="/tmp/signature-b.png",
        page_index=1,
        x_ratio=0.12,
        y_ratio=0.22,
        width_ratio=0.26,
        height_ratio=0.05,
        name="Second Template",
    )

    templates = list_templates()
    assert [tpl.template_id for tpl in templates[:2]] == [second.template_id, first.template_id]
    assert get_template(first.template_id) == first
    assert get_template(second.template_id) == second


def test_template_store_update_and_delete(monkeypatch, tmp_path: Path) -> None:
    """Save existing template with the same id and delete by id."""
    _configure_store_path(monkeypatch, tmp_path)

    template = create_template(
        signature_path="/tmp/signature-a.png",
        page_index=0,
        x_ratio=0.05,
        y_ratio=0.1,
        width_ratio=0.2,
        height_ratio=0.03,
        name="To Update",
    )

    template.name = "Renamed Template"
    template.x_ratio = 0.15
    saved = save_template(template)

    loaded = get_template(template.template_id)
    assert loaded is not None
    assert loaded.name == "Renamed Template"
    assert loaded.template_id == saved.template_id

    deleted = delete_template(template.template_id)
    assert deleted is True
    assert list_templates() == []
    assert get_template(template.template_id) is None


def test_template_store_tolerates_invalid_payload(monkeypatch, tmp_path: Path) -> None:
    """Load an invalid payload by creating the file manually."""
    _configure_store_path(monkeypatch, tmp_path)

    templates_file = tmp_path / "pdf_templates.json"
    templates_file.write_text("{not-valid-json}")
    payload = _safe_templates_payload()
    assert payload["templates"] == []
    assert list_templates() == []


def test_template_field_anchor_metadata(monkeypatch, tmp_path: Path) -> None:
    """Keep anchor metadata for field-aware template replay."""
    _configure_store_path(monkeypatch, tmp_path)
    template = SignaturePlacementTemplate(
        template_id="fixed-id",
        name="Anchored",
        signature_path="/tmp/signature.png",
        page_index=2,
        x_ratio=0.25,
        y_ratio=0.35,
        width_ratio=0.2,
        height_ratio=0.04,
        use_field_anchor=True,
        field_type="signature",
        field_label="Sign here",
        field_confidence=0.92,
        anchor_x_ratio=0.51,
        anchor_y_ratio=0.62,
        source_pdf_name="contract.pdf",
        source_pdf_path="/tmp/contract.pdf",
    )

    saved = save_template(template)
    loaded = get_template("fixed-id")
    assert loaded is not None
    assert loaded.use_field_anchor is True
    assert loaded.anchor_x_ratio == 0.51
    assert loaded.anchor_y_ratio == 0.62
    assert loaded.field_type == "signature"
    assert loaded.field_label == "Sign here"
    assert loaded.source_pdf_name == "contract.pdf"


def test_template_store_migrates_v1_legacy_payload(monkeypatch, tmp_path: Path) -> None:
    """Read legacy scalar payload as version-1 style and expose canonical bindings."""
    _configure_store_path(monkeypatch, tmp_path)
    legacy_payload = {
        "version": 1,
        "templates": [
            {
                "template_id": "legacy-1",
                "name": "Legacy",
                "signature_path": "/tmp/sig.png",
                "page_index": 2,
                "x_ratio": 0.1,
                "y_ratio": 0.2,
                "width_ratio": 0.3,
                "height_ratio": 0.04,
                "use_field_anchor": True,
                "field_type": "signature",
                "field_label": "Sig",
                "field_confidence": 0.88,
                "anchor_x_ratio": 0.5,
                "anchor_y_ratio": 0.6,
                "source_pdf_name": "contract.pdf",
                "source_pdf_path": "/tmp/contract.pdf",
            }
        ],
    }
    payload_file = tmp_path / "pdf_templates.json"
    payload_file.write_text(json.dumps(legacy_payload))

    templates = list_templates()
    assert len(templates) == 1
    template = templates[0]
    assert template.template_id == "legacy-1"
    assert template.version == 2
    assert template.field_bindings
    assert len(template.field_bindings) == 1
    assert template.field_bindings[0].signature_asset_ref == "/tmp/sig.png"
    assert template.field_bindings[0].anchor_x_ratio == 0.5


def test_template_store_save_supports_multi_binding(monkeypatch, tmp_path: Path) -> None:
    """Persist and reload a template with multiple placement bindings."""
    _configure_store_path(monkeypatch, tmp_path)

    binding_a = SignatureFieldBinding.from_legacy_values(
        signature_path="/tmp/signature-a.png",
        page_index=0,
        x_ratio=0.11,
        y_ratio=0.12,
        width_ratio=0.2,
        height_ratio=0.04,
        field_label="Signer A",
    )
    binding_b = SignatureFieldBinding.from_legacy_values(
        signature_path="/tmp/signature-b.png",
        page_index=1,
        x_ratio=0.21,
        y_ratio=0.22,
        width_ratio=0.2,
        height_ratio=0.04,
        field_label="Signer B",
    )

    template = SignaturePlacementTemplate(
        template_id="multi-1",
        name="Multi",
        signature_path=binding_a.signature_asset_ref,
        page_index=binding_a.page_index,
        x_ratio=binding_a.x_ratio,
        y_ratio=binding_a.y_ratio,
        width_ratio=binding_a.width_ratio,
        height_ratio=binding_a.height_ratio,
        field_bindings=[binding_a, binding_b],
    )
    saved = save_template(template)

    payload = _safe_templates_payload()
    raw_item = payload["templates"][0]
    assert raw_item["version"] == 2
    assert len(raw_item["field_bindings"]) == 2
    assert raw_item["field_bindings"][0]["signature_asset_ref"] == "/tmp/signature-a.png"

    loaded = get_template("multi-1")
    assert loaded is not None
    assert loaded.field_bindings is not None
    assert len(loaded.field_bindings) == 2
    assert loaded.field_bindings[1].signature_asset_ref == "/tmp/signature-b.png"
