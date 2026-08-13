"""Focused contract checks for the canonical root landing surface.

The completion rail is intentionally a bounded, keyboard-operable preview of
the documented current workflow. It does not process a visitor document or
replace the desktop application. A future interaction pass can bind the rail
to an authorized demonstration asset after the product and evidence contract
is approved.
"""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path


PAGE = Path(__file__).parents[1] / "index.html"


class _LandingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: list[tuple[str, dict[str, str]]] = []
        self.buttons: list[dict[str, str]] = []
        self.button_labels: list[str] = []
        self.images: list[dict[str, str]] = []
        self._current_button_text: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value or "" for name, value in attrs}
        self.elements.append((tag, attributes))
        if tag == "button":
            self.buttons.append(attributes)
            self._current_button_text = []
        if tag == "img":
            self.images.append(attributes)

    def handle_data(self, data: str) -> None:
        if self._current_button_text is not None:
            self._current_button_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "button" and self._current_button_text is not None:
            self.button_labels.append("".join(self._current_button_text).strip())
            self._current_button_text = None


def _page() -> str:
    return PAGE.read_text(encoding="utf-8")


def _parsed_page() -> tuple[str, _LandingParser]:
    page = _page()
    parser = _LandingParser()
    parser.feed(page)
    return page, parser


def test_canonical_landing_has_mobile_first_cta_and_semantic_landmarks() -> None:
    page, parser = _parsed_page()
    main_elements = [attrs for tag, attrs in parser.elements if tag == "main"]
    footer_elements = [attrs for tag, attrs in parser.elements if tag == "footer"]

    assert len(main_elements) == 1
    assert main_elements[0]["id"] == "main-content"
    assert main_elements[0]["tabindex"] == "-1"
    assert len(footer_elements) == 1
    assert 'class="skip-link" href="#main-content"' in page

    hero_start = page.index('<div class="hero-main">')
    lead_end = page.index('</p>', page.index('<p class="lead">', hero_start))
    cta_start = page.index('<div class="hero-actions">', lead_end)
    feature_detail_start = page.index('<ul>', cta_start)
    first_checkout = page.index('data-checkout-provider="dodo"', cta_start)

    assert lead_end < cta_start < feature_detail_start
    assert cta_start < first_checkout < feature_detail_start


def test_canonical_landing_exposes_non_vacuous_completion_rail_contract() -> None:
    page, parser = _parsed_page()
    rail_buttons = [
        button
        for button in parser.buttons
        if "data-completion-step" in button
    ]

    assert len(rail_buttons) == 5
    assert parser.button_labels == ["Source", "Mark", "Clean", "Place", "Ready"]
    assert {button["type"] for button in rail_buttons} == {"button"}
    assert {button["aria-controls"] for button in rail_buttons} == {
        "completion-step-description"
    }
    assert sum(button.get("aria-current") == "step" for button in rail_buttons) == 1
    assert 'role="status" aria-live="polite"' in page
    assert "not a live document processor" in page
    assert "document.querySelectorAll('[data-completion-step]')" in page


def test_canonical_landing_has_image_geometry_loading_and_accessibility_primitives() -> None:
    page, parser = _parsed_page()

    assert parser.images
    assert all(image.get("alt") is not None for image in parser.images)
    assert all(image.get("width") and image.get("height") for image in parser.images)
    assert all(image.get("loading") in {"eager", "lazy"} for image in parser.images)
    assert 'loading="eager"' in page
    assert page.count('loading="lazy"') >= 4

    assert "scroll-margin-top" in page
    assert ":focus-visible" in page
    assert "prefers-reduced-motion: reduce" in page
    assert "scroll-behavior: auto" in page


def test_canonical_landing_keeps_governed_claim_and_checkout_boundaries() -> None:
    page = _page()

    for required in (
        "locally by default",
        "Core extraction and PDF work run locally by default",
        'data-checkout-provider="dodo"',
        'data-checkout-provider="gumroad"',
        'src="web/live/js/checkout.js"',
    ):
        assert required in page

    for forbidden in (
        "100% offline",
        "never leave your computer",
        "free updates forever",
    ):
        assert forbidden not in page.lower()
