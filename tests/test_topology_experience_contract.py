from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_desktop_status_copy_names_the_local_companion_boundary() -> None:
    main_window = (ROOT / "desktop_app" / "views" / "main_window.py").read_text(encoding="utf-8")
    status = (ROOT / "desktop_app" / "views" / "main_window_parts" / "status.py").read_text(encoding="utf-8")
    extraction = (ROOT / "desktop_app" / "views" / "main_window_parts" / "extraction.py").read_text(encoding="utf-8")

    assert "Local service: Online" in main_window
    assert "Local service: checking" in status
    assert "Cloud-sync active" not in extraction
    assert "cloud features enabled" not in extraction


def test_browser_workspace_explains_current_and_planned_topologies() -> None:
    page = (ROOT / "web" / "cloud_workspace" / "index.html").read_text(encoding="utf-8").lower()
    app = (ROOT / "web" / "cloud_workspace" / "app.js").read_text(encoding="utf-8").lower()

    assert page.count("<main") == 1
    for phrase in ("local", "cloud", "hybrid", "planned", "metadata-only"):
        assert phrase in page or phrase in app, phrase
    assert "new cloud execution" not in page
    assert "document bytes" in page


def test_new_page_makes_topology_a_product_choice_not_a_hidden_implementation_detail() -> None:
    page = (ROOT / "web" / "new_landing_page" / "index.html").read_text(encoding="utf-8").lower()
    for phrase in ("choose how signkit runs", "local", "cloud", "hybrid", "planned direction"):
        assert phrase in page, phrase
