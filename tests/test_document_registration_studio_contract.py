from pathlib import Path
import re


ROOT = Path(__file__).parents[1]
LANDING = ROOT / "web/concepts/2026-08-13-document-registration-studio"
WORKSPACE = LANDING / "workspace"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_candidate_is_isolated_and_truth_bound() -> None:
    html = read(LANDING / "index.html")
    assert "Illustrative concept" in html
    assert "not a production route" in html
    assert "does not show" in html
    assert "browser signing" in html
    assert len(re.findall(r"<main\b", html, flags=re.I)) == 1
    assert len(re.findall(r"<footer\b", html, flags=re.I)) == 1
    assert 'href="#main-content"' in html


def test_landing_binds_all_registration_states_to_native_controls() -> None:
    html = read(LANDING / "index.html")
    js = read(LANDING / "app.js")
    css = read(LANDING / "styles.css")
    assert len(re.findall(r'data-stage="(?:source|mark|clean|place|ready)"', html)) == 5
    assert html.count('role="tab"') == 5
    assert "ArrowRight" in js and "ArrowLeft" in js and "Home" in js and "End" in js
    assert "addEventListener('focus'" in js
    assert "aria-live=\"polite\"" in html
    assert "prefers-reduced-motion:reduce" in css
    assert "transition: all" not in css


def test_workspace_keeps_metadata_boundary_and_accessible_controls() -> None:
    html = read(WORKSPACE / "index.html")
    js = read(WORKSPACE / "app.js")
    assert "metadata workbench, not a signing session" in html
    assert "No account, PDF, or backend record is changed" in html
    assert len(re.findall(r'data-record="(?:acknowledgement|placement|receipt)"', html)) == 3
    assert html.count('type="button"') >= 7
    assert 'role="status"' in html and 'aria-live="polite"' in html
    assert "No backend state changed" in js


def test_candidate_styles_cover_focus_motion_and_mobile_geometry() -> None:
    for path in (LANDING / "styles.css", WORKSPACE / "styles.css"):
        css = read(path)
        assert ":focus-visible" in css
        assert "prefers-reduced-motion:reduce" in css
        assert "max-width:560px" in css
        assert "transition: all" not in css
        assert "outline:none" not in css
