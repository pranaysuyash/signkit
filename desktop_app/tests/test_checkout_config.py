from desktop_app.config import GUMROAD_FALLBACK_URL, get_purchase_url


def test_purchase_url_prefers_valid_dodo_product(monkeypatch):
    monkeypatch.setenv("DODO_PRODUCT_ID", "pdt_SignKit123")
    monkeypatch.setenv("GUMROAD_PRODUCT_URL", "https://example.com/gumroad-fallback")

    assert get_purchase_url() == (
        "https://checkout.dodopayments.com/buy/pdt_SignKit123"
    )


def test_purchase_url_rejects_malformed_dodo_product(monkeypatch):
    monkeypatch.setenv("DODO_PRODUCT_ID", "replace-me")
    monkeypatch.delenv("GUMROAD_PRODUCT_URL", raising=False)

    assert get_purchase_url() == GUMROAD_FALLBACK_URL


def test_purchase_url_respects_explicit_gumroad_fallback(monkeypatch):
    monkeypatch.delenv("DODO_PRODUCT_ID", raising=False)
    monkeypatch.setenv("GUMROAD_PRODUCT_URL", "https://example.com/alternate")

    assert get_purchase_url() == "https://example.com/alternate"


def test_purchase_url_supports_plan_specific_product(monkeypatch):
    monkeypatch.setenv("DODO_PRODUCT_ID_TEAM", "pdt_TeamPlan")
    monkeypatch.delenv("DODO_PRODUCT_ID", raising=False)
    monkeypatch.delenv("GUMROAD_PRODUCT_URL", raising=False)

    assert get_purchase_url("team") == "https://checkout.dodopayments.com/buy/pdt_TeamPlan"


def test_purchase_url_supports_plan_specific_fallback(monkeypatch):
    monkeypatch.delenv("DODO_PRODUCT_ID", raising=False)
    monkeypatch.delenv("DODO_PRODUCT_ID_TEAM", raising=False)
    monkeypatch.setenv("GUMROAD_PRODUCT_URL_TEAM", "https://example.com/team")

    assert get_purchase_url("team") == "https://example.com/team"


def test_purchase_url_resolves_default_plan_env_variable(monkeypatch):
    monkeypatch.setenv("SIGNKIT_DEFAULT_PLAN", "team")
    monkeypatch.setenv("DODO_PRODUCT_ID_TEAM", "pdt_TeamDefault")
    monkeypatch.delenv("DODO_PRODUCT_ID", raising=False)
    monkeypatch.delenv("GUMROAD_PRODUCT_URL", raising=False)

    assert get_purchase_url() == "https://checkout.dodopayments.com/buy/pdt_TeamDefault"
