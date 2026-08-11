"""Static launch-claim safeguards for the canonical SignKit landing page.

The root page is customer-facing and carries pricing, privacy, payment, and
refund language. These checks intentionally stay dependency-free so they can run
before a browser or checkout smoke workflow is available. They do not replace
runtime provider verification.
"""

from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = PROJECT_ROOT / "index.html"
REGISTRY_PATH = PROJECT_ROOT / "docs" / "launch_claims" / "registry.md"

CLAIM_IDS = {
    "job_local_pdf",
    "local_processing_boundary",
    "personal_price",
    "one_time_pricing",
    "checkout_provider_state",
    "platform_availability",
    "personal_included_workflow",
    "licence_updates",
    "refund_policy",
    "recurring_workflow_enquiry",
    "operator_context",
    "product_evidence",
}


def _index() -> str:
    return INDEX_PATH.read_text(encoding="utf-8")


def _normalised(value: str) -> str:
    return " ".join(value.split())


def _registry_rows() -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in REGISTRY_PATH.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\| `([a-z_]+)` \|", line)
        if match:
            rows[match.group(1)] = line
    return rows


def test_registry_bindings_are_complete() -> None:
    """Every public claim marker has one registry row and an enforcing test."""

    index = _index()
    registry = REGISTRY_PATH.read_text(encoding="utf-8")
    marker_ids = set(re.findall(r"<!--\s*launch-claim:\s*([a-z_]+)\s*-->", index))
    assert marker_ids == CLAIM_IDS

    rows = _registry_rows()
    assert set(rows) == CLAIM_IDS
    for claim_id, row in rows.items():
        assert "index.html" in row, claim_id
        assert "tests/test_launch_claim_registry.py" in row, claim_id
        assert "Tier" in row, claim_id
        assert claim_id in registry, claim_id


def test_required_job_language_is_present() -> None:
    page = _normalised(_index()).lower()
    for phrase in (
        "extract, clean, save, and place signatures on pdfs",
        "locally by default",
        "$29",
        "$39",
        "gumroad",
        "recurring document operations",
        "what you choose to type",
        "intent=document-workflow",
    ):
        assert phrase in page, phrase


def test_price_decision_is_explicit() -> None:
    page = _normalised(_index())
    assert re.search(r"\$29[^.]{0,80}one[- ]time", page, re.IGNORECASE)
    assert re.search(r"\$39[^.]{0,100}(regular Personal price|regular Personal licence)", page)
    assert "no recurring charges" in page.lower()


def test_privacy_boundary_is_qualified() -> None:
    page = _normalised(_index()).lower()
    assert "core extraction and pdf work run locally by default" in page
    assert "checkout receives purchase and delivery information" in page
    assert "the enquiry receives only what you choose to type" in page
    assert "do not attach documents" in page


def test_provider_copy_is_state_neutral() -> None:
    page = _normalised(_index())
    assert re.search(
        r"Secure checkout is available through the configured provider\. Gumroad is the current fallback while Dodo is not configured\.",
        page,
    )
    assert "Dodo Payments delivers" not in page
    assert "Dodo Payments provides" not in page
    assert 'data-checkout-primary-label="Buy SignKit through Gumroad' in page


def test_platform_copy_names_release_bundle_source_of_truth() -> None:
    page = _normalised(_index()).lower()
    for platform in ("macos", "windows", "linux"):
        assert platform in page
    assert "release bundle is the source of truth" in page


def test_personal_workflow_terms_are_present() -> None:
    page = _normalised(_index()).lower()
    for phrase in (
        "signature extraction and cleanup",
        "reusable local vault",
        "pdf placement and export",
        "one-time personal licence",
    ):
        assert phrase in page, phrase


def test_update_boundary_is_qualified() -> None:
    page = _normalised(_index()).lower()
    assert "minor updates are included within the purchased major version" in page
    assert "every future major release" not in page


def test_refund_copy_matches_legal_policy() -> None:
    page = _normalised(_index()).lower()
    assert "30-day money-back guarantee" in page
    assert "provider used for purchase" in page
    assert "support@signkit.work" in page
    assert "purchase email and order reference" in page
    for legal_name in ("legal/TERMS_OF_SERVICE.md", "legal/EULA.md"):
        legal_text = (PROJECT_ROOT / legal_name).read_text(encoding="utf-8").lower()
        assert "30-day money-back guarantee" in legal_text, legal_name


def test_workflow_enquiry_is_unpriced_and_data_bounded() -> None:
    page = _index()
    start = page.index('<section class="workflow-section"')
    end = page.index("<!-- FAQ section -->", start)
    workflow = _normalised(page[start:end])
    assert "$" not in workflow
    assert "what you choose to type" in workflow.lower()
    assert "do not attach documents" in workflow.lower()
    assert "intent=document-workflow" in workflow


def test_no_social_proof_or_benchmarks_are_published() -> None:
    page = _index().lower()
    forbidden = (
        "1,200+",
        "12,847",
        "4.8/5",
        "30s",
        "happy customers",
        "testimonial",
        "review rating",
        "customer rating",
        "dodo payments delivers",
        "100% offline",
        "100 percent offline",
        "no cloud storage",
        "no cloud upload",
        "your data never touches our servers",
    )
    for phrase in forbidden:
        assert phrase not in page, phrase
    assert not re.search(r"\bin\s+\d+\s*seconds?\b", page)
    assert not re.search(r"\bwithin\s+\d+\s*seconds?\b", page)


def test_product_preview_is_not_marketed_as_benchmark() -> None:
    page = _index().lower()
    assert "product preview" in page
    assert "live preview" not in page
    assert "benchmark" not in page


def test_root_has_no_public_variant_redirect_logic() -> None:
    page = _index()
    assert "AUTO_SPLIT" not in page
    assert "ab_variant" not in page
    assert not re.search(r"window\.location\.href\s*=\s*['\"]/(?:root|buy|purchase|gum)", page)
