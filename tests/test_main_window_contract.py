"""Smoke test for MainWindow mixin contract compliance."""

import pytest
from unittest.mock import Mock


PySide6 = pytest.importorskip("PySide6")


def test_main_window_mixin_contract(qapp):
    """Verify all mixin methods exist on MainWindow before instantiation."""
    # Import here to catch import errors
    from desktop_app.api.client import ApiClient
    from desktop_app.state.session import SessionState
    from desktop_app.views.main_window import MainWindow

    # Create minimal mocks
    mock_client = Mock(spec=ApiClient)
    mock_client.base_url = "http://127.0.0.1:8001"
    mock_session = Mock(spec=SessionState)

    # Instantiate window
    try:
        window = MainWindow(mock_client, mock_session)

        # Verify mixin methods exist
        required_methods = [
            # From ExtractionTabMixin
            '_setup_extraction_ui',
            '_on_tab_changed',
            'on_open',
            'on_export',
            'on_save_to_library',

            # From PdfTabMixin
            '_setup_pdf_ui',

            # From ThemeMixin
            '_apply_theme',
            '_setup_dark_mode_support',

            # From ToolbarMixin
            '_setup_main_toolbar',

            # From PaneStatusMixin
            '_init_status_bar',
            'defer_coordinate_update',

            # From NativeDialogsMixin
            '_native_open_file',
            '_open_document',
            '_open_url',

            # Health check
            '_check_backend_health',
        ]

        missing_methods = []
        for method in required_methods:
            if not hasattr(window, method):
                missing_methods.append(method)

        # Cleanup
        window.close()

        # Assert no missing methods
        assert not missing_methods, f"Missing mixin methods: {missing_methods}"

    except Exception as e:
        pytest.fail(f"MainWindow instantiation failed: {e}")


def test_main_window_responsive_breakpoints(qapp):
    """Verify responsive breakpoint handler exists."""
    from desktop_app.api.client import ApiClient
    from desktop_app.state.session import SessionState
    from desktop_app.views.main_window import MainWindow

    mock_client = Mock(spec=ApiClient)
    mock_client.base_url = "http://127.0.0.1:8001"
    mock_session = Mock(spec=SessionState)

    window = MainWindow(mock_client, mock_session)

    # Verify responsive attributes
    assert hasattr(window, '_is_compact')
    assert hasattr(window, '_is_narrow')
    assert hasattr(window, '_apply_responsive_breakpoints')
    assert window._onboarding_default_plan_id == "starter"
    assert window.get_default_purchase_plan_id() == "starter"
    assert window._show_onboarding_upgrade_card is True

    window.close()


def test_workflow_tabs_locked_for_standard_profile(qapp):
    """Standard profile should expose workflow features as discoverable but premium-locked."""

    from desktop_app.api.client import ApiClient
    from desktop_app.state.session import SessionState
    from PySide6.QtWidgets import QPushButton
    from desktop_app.views.main_window import MainWindow

    mock_client = Mock(spec=ApiClient)
    mock_client.base_url = "http://127.0.0.1:8001"
    mock_session = Mock(spec=SessionState)

    window = MainWindow(mock_client, mock_session)
    assert window.workflow_premium_enabled is False
    assert window.workflow_console_tab.property("feature_locked") is True
    assert window.workflow_grants_tab.property("feature_locked") is True
    assert window.recipe_builder_tab.property("feature_locked") is True
    assert any(
        isinstance(btn, QPushButton) and btn.text() == "Upgrade to Workflow Premium"
        for btn in window.workflow_console_tab.findChildren(QPushButton)
    )
    assert "Workflow Dashboard (Premium)" in window.tab_widget.tabText(window._workflow_console_tab_index)
    assert "Workflow Grants (Premium)" in window.tab_widget.tabText(window._workflow_grants_tab_index)
    assert "Recipe Builder (Premium)" in window.tab_widget.tabText(window._recipe_builder_tab_index)

    window.close()


def test_workflow_lock_copy_mentions_folder_triplet(qapp):
    """Standard profile should explain folder-triple execution model in locked states."""

    from desktop_app.api.client import ApiClient
    from desktop_app.state.session import SessionState
    from desktop_app.views.main_window import MainWindow
    from PySide6.QtWidgets import QLabel

    mock_client = Mock(spec=ApiClient)
    mock_client.base_url = "http://127.0.0.1:8001"
    mock_session = Mock(spec=SessionState)

    window = MainWindow(mock_client, mock_session)
    labels = window.workflow_console_tab.findChildren(QLabel)
    combined_text = " ".join(label.text() for label in labels)
    assert "Unsigned Docs → Signed Docs" in combined_text or "unsigned docs" in combined_text.lower()

    window.close()


def test_workflow_tabs_enabled_for_premium_profile(qapp):
    """mac-premium profile should get interactive workflow tabs."""

    from desktop_app.api.client import ApiClient
    from desktop_app.state.session import SessionState
    from desktop_app.views.main_window import MainWindow
    from desktop_app.views.main_window_parts.workflow_console import WorkflowConsole
    from desktop_app.views.main_window_parts.grant_manager import GrantManager
    from desktop_app.views.main_window_parts.recipe_builder import RecipeBuilder

    mock_client = Mock(spec=ApiClient)
    mock_client.base_url = "http://127.0.0.1:8001"
    mock_session = Mock(spec=SessionState)

    window = MainWindow(mock_client, mock_session, workflow_premium_enabled=True)
    assert window.workflow_premium_enabled is True
    assert isinstance(window.workflow_console_tab, WorkflowConsole)
    assert isinstance(window.workflow_grants_tab, GrantManager)
    assert isinstance(window.recipe_builder_tab, RecipeBuilder)
    assert window.workflow_console_tab.property("feature_locked") is None

    assert hasattr(window.workflow_console_tab, "refresh")
    assert hasattr(window.workflow_grants_tab, "refresh")
    assert hasattr(window.recipe_builder_tab, "refresh")
    assert window._onboarding_default_plan_id == "starter"
    assert window.get_default_purchase_plan_id() == "starter"
    assert window._show_onboarding_upgrade_card is True

    window.close()


def test_main_window_title_can_be_set_by_launch_profile(qapp):
    """Window title should use the provided launch title so premium builds can brand distinctly."""

    from desktop_app.api.client import ApiClient
    from desktop_app.state.session import SessionState
    from desktop_app.views.main_window import MainWindow

    mock_client = Mock(spec=ApiClient)
    mock_client.base_url = "http://127.0.0.1:8001"
    mock_session = Mock(spec=SessionState)

    window = MainWindow(mock_client, mock_session, window_title="SignKit Premium")
    assert window.windowTitle() == "SignKit Premium"

    default_window = MainWindow(mock_client, mock_session)
    assert default_window.windowTitle() == "SignKit"

    window.close()
    default_window.close()


if __name__ == "__main__":
    # Run smoke test standalone
    print("Running MainWindow mixin contract smoke test...")
    test_main_window_mixin_contract()
    print("✓ All mixin methods exist")

    test_main_window_responsive_breakpoints()
    print("✓ Responsive breakpoints configured")

    print("\n✅ All smoke tests passed!")
