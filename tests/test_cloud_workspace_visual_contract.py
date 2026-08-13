from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).parents[1]
PAGE = ROOT / "web" / "cloud_workspace" / "index.html"
STYLES = ROOT / "web" / "cloud_workspace" / "styles.css"


class WorkspaceMarkupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.elements.append((tag, {name: value or "" for name, value in attrs}))


def parsed_workspace() -> tuple[str, WorkspaceMarkupParser]:
    markup = PAGE.read_text(encoding="utf-8")
    parser = WorkspaceMarkupParser()
    parser.feed(markup)
    return markup, parser


def test_workspace_preserves_metadata_first_truth_and_semantic_state_roles() -> None:
    markup, parser = parsed_workspace()
    lower_markup = markup.lower()
    elements = parser.elements

    assert "metadata-only" in lower_markup
    assert "not a signing claim" in lower_markup
    assert "does not host document signing" in lower_markup
    assert "browser-native signing" not in lower_markup
    assert "100% offline" not in lower_markup

    tablist = [attrs for tag, attrs in elements if attrs.get("role") == "tablist"]
    tabs = [attrs for tag, attrs in elements if attrs.get("role") == "tab"]
    panels = [attrs for tag, attrs in elements if attrs.get("role") == "tabpanel"]
    assert len(tablist) == 1
    assert len(tabs) == 2
    assert {attrs.get("aria-selected") for attrs in tabs} == {"true", "false"}
    assert {attrs.get("aria-controls") for attrs in tabs} == {"login-form", "register-form"}
    assert {attrs.get("tabindex") for attrs in tabs} == {"0", "-1"}
    assert {attrs.get("id") for attrs in panels} == {"login-form", "register-form"}
    assert {attrs.get("aria-hidden") for attrs in panels} == {"false", "true"}
    assert "MutationObserver" in markup
    assert "ArrowRight" in markup and "ArrowLeft" in markup

    trust_boundary = next(attrs for tag, attrs in elements if attrs.get("id") == "trust-boundary")
    passport = next(attrs for tag, attrs in elements if attrs.get("id") == "passport-panel-label")
    assert trust_boundary.get("role") == "note"
    assert passport.get("class") == "visually-hidden"


def test_workspace_form_controls_have_explicit_labels_names_and_autocomplete() -> None:
    _, parser = parsed_workspace()
    elements = parser.elements
    ids = {attrs["id"] for tag, attrs in elements if attrs.get("id")}
    labels = [attrs for tag, attrs in elements if tag == "label"]
    controls = [
        attrs
        for tag, attrs in elements
        if tag in {"input", "select", "textarea"} and attrs.get("type") != "hidden"
    ]

    assert labels
    assert all(attrs.get("for") in ids for attrs in labels)
    assert all(attrs.get("id") in ids and attrs.get("name") for attrs in controls)

    controls_by_id = {attrs["id"]: attrs for attrs in controls}
    assert controls_by_id["login-email"]["autocomplete"] == "email"
    assert controls_by_id["login-password"]["autocomplete"] == "current-password"
    assert controls_by_id["register-password"]["autocomplete"] == "new-password"
    assert controls_by_id["participant-name"]["autocomplete"] == "name"
    assert controls_by_id["participant-email"]["autocomplete"] == "email"
    assert controls_by_id["reviewer-name"]["autocomplete"] == "name"
    assert controls_by_id["reviewer-email"]["autocomplete"] == "email"


def test_workspace_styles_cover_focus_motion_and_mobile_contract() -> None:
    styles = STYLES.read_text(encoding="utf-8")

    assert ":focus-visible" in styles
    assert "outline: 3px solid var(--clay)" in styles
    assert "@media (prefers-reduced-motion: reduce)" in styles
    assert "@media (max-width: 880px)" in styles
    assert "@media (max-width: 560px)" in styles
    assert ".topology-options { grid-template-columns: 1fr; }" in styles
    assert ".execution-row { grid-template-columns: 1fr; }" in styles
