#!/usr/bin/env python3
"""Capture dated, profile-aware SignKit product surfaces from the current code."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication

from desktop_app.api.client import ApiClient
from desktop_app.launch_profile import get_profile
from desktop_app.state.session import SessionState
from desktop_app.views.main_window import MainWindow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture current SignKit tab surfaces from a selected launch profile."
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Repository-relative directory for dated PNG evidence.",
    )
    parser.add_argument(
        "--profile",
        choices=("standard", "mac-premium"),
        default="mac-premium",
        help="Current launch profile to render.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile = get_profile(args.profile)
    output_dir = PROJECT_ROOT / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    app = QApplication.instance() or QApplication(sys.argv)
    session = SessionState()
    window = MainWindow(
        ApiClient(base_url="http://127.0.0.1:8001", session=session),
        session,
        backend_manager=None,
        window_title=profile.resolve_title(),
        workflow_premium_enabled=profile.premium_ui,
        onboarding_default_plan_id=profile.default_plan_id,
        show_onboarding_upgrade_card=not profile.premium_ui,
    )
    window.resize(*profile.initial_window_size)
    window.show()
    app.processEvents()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    captured = 0
    for index in range(window.tab_widget.count()):
        window.tab_widget.setCurrentIndex(index)
        app.processEvents()
        tab_name = window.tab_widget.tabText(index)
        slug = "".join(character.lower() if character.isalnum() else "_" for character in tab_name).strip("_")
        path = output_dir / f"{index + 1:02d}_{slug}_{timestamp}.png"
        if not window.grab().save(str(path), "PNG"):
            raise RuntimeError(f"Failed to save {path}")
        captured += 1
        print(f"Captured {path.relative_to(PROJECT_ROOT)}")

    window.close()
    app.processEvents()
    print(f"Captured {captured} current {profile.profile_name} surfaces.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
