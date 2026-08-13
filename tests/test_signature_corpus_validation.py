"""Tests for corpus provenance, geometry, and split-leakage validation."""

import json
from pathlib import Path

from PIL import Image

from tools.validate_signature_corpus import validate_corpus


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "desktop_app/tests/fixtures/signature_edge_cases/metadata.json"


def test_generated_corpus_passes_readiness_validation():
    assert validate_corpus(CORPUS, ROOT) == []


def test_readiness_gate_rejects_held_out_claim_without_split(tmp_path):
    payload = json.loads(CORPUS.read_text(encoding="utf-8"))
    payload["cases"] = [dict(payload["cases"][0])]
    image_path = tmp_path / "blank.png"
    Image.new("L", (512, 512), color=255).save(image_path)
    payload["cases"][0]["file"] = "blank.png"
    payload["cases"][0]["sha256"] = "not-the-real-hash"
    corpus_path = tmp_path / "corpus.json"
    corpus_path.write_text(json.dumps(payload), encoding="utf-8")

    errors = validate_corpus(corpus_path, tmp_path, require_held_out=True, required_tags=set())
    assert "held-out validation requires a test or held_out split" in errors


def test_readiness_gate_rejects_duplicate_fixture_across_splits(tmp_path):
    payload = json.loads(CORPUS.read_text(encoding="utf-8"))
    payload["cases"] = [dict(payload["cases"][0]), dict(payload["cases"][0])]
    payload["cases"][1]["name"] = "duplicate_blank"
    payload["cases"][1]["split"] = "test"
    corpus_path = tmp_path / "corpus.json"
    corpus_path.write_text(json.dumps(payload), encoding="utf-8")

    errors = validate_corpus(corpus_path, ROOT, required_tags=set())
    assert any("duplicate fixture file across splits" in error for error in errors)


def test_readiness_gate_rejects_subject_leakage_between_splits(tmp_path):
    payload = json.loads(CORPUS.read_text(encoding="utf-8"))
    first = dict(payload["cases"][0])
    second = dict(payload["cases"][1])
    first["subject_id"] = "subject-001"
    second["subject_id"] = "subject-001"
    first["split"] = "train"
    second["split"] = "test"
    payload["cases"] = [first, second]
    corpus_path = tmp_path / "corpus.json"
    corpus_path.write_text(json.dumps(payload), encoding="utf-8")

    errors = validate_corpus(
        corpus_path,
        ROOT,
        require_held_out=True,
        require_subject_disjoint=True,
        required_tags=set(),
    )

    assert any("subject leakage between test and train" in error for error in errors)
