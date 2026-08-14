"""Prevent the condensed TODO from contradicting canonical local evidence."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).parents[1]
TODO = ROOT / "docs" / "TODO.md"
BACKLOG = ROOT / "docs" / "PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md"


def test_condensed_todo_points_to_canonical_backlog_and_current_local_closures() -> None:
    todo = TODO.read_text(encoding="utf-8")
    backlog = BACKLOG.read_text(encoding="utf-8")
    normalized_todo = " ".join(todo.split())

    assert "Canonical backlog governance is now in:" in todo
    assert "docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md" in todo
    assert "| L2-12 | implicit | docs/status |" in backlog

    expected_current_rows = (
        "[x] Local smoke tests: /health, authenticated upload, process/export/deletion round-trip (`QA-53`)",
        "[x] PyInstaller spec for the current macOS arm64 bundle (`QA-55`)",
        "[x] Export gating uses the signed local entitlement boundary and Upgrade path (`L1-01`, `QA-23`)",
        "[x] Status bar note when unlicensed is bound to the evaluation-mode export lock (`L1-01`, `QA-23`)",
    )
    for row in expected_current_rows:
        assert row in todo, row

    assert "[ ] Smoke tests: /health, upload, process round-trip" not in todo
    assert "[ ] PyInstaller spec for macOS bundle" not in todo
    assert "[ ] Export gating: show Upgrade dialog if unlicensed" not in todo
    assert "[ ] Status bar note when unlicensed" not in todo

    assert "untracked root `TODO.md` is preserved separately" in normalized_todo
    assert "hosted, provider, signing, notarization, cross-platform, and rollback" in normalized_todo
