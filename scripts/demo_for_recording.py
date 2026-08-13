#!/usr/bin/env python3
"""
Demo script for video recording - goes through ALL features slowly.
Run this and record the screen to capture everything.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from desktop_app.views.main_window import MainWindow
from desktop_app.api.client import ApiClient
from desktop_app.state.session import SessionState


def main():
    """Run app for video recording."""
    
    print("\n" + "=" * 70)
    print("🎥 DEMO MODE FOR VIDEO RECORDING")
    print("=" * 70)
    print("\n📹 START RECORDING NOW!")
    print("\nThis will:")
    print("  1. Launch the app")
    print("  2. Keep it open for you to demonstrate")
    print("  3. You manually show all features")
    print("\n🎬 Features to demonstrate:")
    print("  ✓ Main interface")
    print("  ✓ Open image (desktop_app/resources/signature_template_synthetic_512.jpg)")
    print("  ✓ Draw selection rectangle")
    print("  ✓ Adjust threshold slider")
    print("  ✓ Click Preview/Extract")
    print("  ✓ Save to library")
    print("  ✓ Click Export (show dialog)")
    print("  ✓ Open License menu")
    print("  ✓ Open Help menu")
    print("  ✓ Switch to PDF tab")
    print("  ✓ Load PDF (assets/demo_document.pdf)")
    print("  ✓ Select signature from library")
    print("  ✓ Place on PDF")
    print("  ✓ Show all menus and dialogs")
    print("\n⏱️  Take your time - show each feature clearly!")
    print("=" * 70)
    print()
    
    app = QApplication(sys.argv)
    
    # Initialize app components
    session_state = SessionState()
    api_client = ApiClient(
        base_url="http://127.0.0.1:8001",
        session=session_state
    )
    
    # Create main window
    main_window = MainWindow(
        api_client,
        session_state,
        backend_manager=None
    )
    
    # Set good size for recording
    main_window.resize(1400, 900)
    main_window.show()
    
    print("✅ App launched! Recording now...")
    print("💡 Close the app window when done recording.\n")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
