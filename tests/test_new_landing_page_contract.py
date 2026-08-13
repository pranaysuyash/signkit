from pathlib import Path
import re


PAGE = Path(__file__).parents[1] / "web" / "new_landing_page" / "index.html"


def _page() -> str:
    return PAGE.read_text(encoding="utf-8").lower()


def test_new_page_uses_the_governed_product_and_checkout_contract() -> None:
    page = _page()

    for required in (
        "locally by default",
        "no recurring charges",
        "minor updates within the purchased major version",
        "choose how signkit runs",
        "local",
        "cloud",
        "hybrid",
        "planned direction",
        'data-checkout-provider="dodo"',
        'data-checkout-provider="gumroad"',
        "../../web/live/js/checkout-config.js",
        "../../web/live/js/checkout.js",
    ):
        assert required in page


def test_new_page_does_not_reintroduce_unsupported_or_placeholder_copy() -> None:
    page = _page()
    forbidden = (
        "100% offline",
        "100 percent offline",
        "never leave your computer",
        "never uploading",
        "free updates forever",
        "/ lifetime",
        "secured by gumroad",
        "version 2.0 available",
        'href="#"',
    )

    for phrase in forbidden:
        assert phrase not in page


def test_new_page_images_have_alt_text_and_one_main_landmark() -> None:
    page = _page()
    assert page.count("<main") == 1
    assert not re.search(r"<img(?![^>]*\balt=)[^>]*>", page)
