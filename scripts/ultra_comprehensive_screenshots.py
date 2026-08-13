#!/usr/bin/env python3
"""
Ultra-comprehensive automated screenshot capture for SignKit.
Captures ALL features, menus, workflows, popups, sliders, cropping areas, etc.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer, QRect, QPoint, Qt
    from PySide6.QtGui import QPixmap
except ImportError:
    print("Error: PySide6 not installed")
    print("Run: pip install PySide6")
    sys.exit(1)

# Import app components
from desktop_app.views.main_window import MainWindow
from desktop_app.api.client import ApiClient
from desktop_app.launch_profile import get_profile
from desktop_app.state.session import SessionState


class UltraComprehensiveScreenshotCapture:
    """Ultra-comprehensive automated screenshot capture for ALL features."""
    
    def __init__(self, output_dir: str = "screenshots", profile_name: str = "mac-premium"):
        self.output_dir = Path(project_root) / output_dir
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.screenshot_count = 0
        self.profile = get_profile(profile_name)
        
        # Test assets
        self.signature_image = project_root / "desktop_app/resources/signature_template_synthetic_512.jpg"
        self.demo_pdf = project_root / "assets" / "demo_document.pdf"
        
        # Initialize Qt Application
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        # Initialize app components
        self.session_state = SessionState()
        self.api_client = ApiClient(
            base_url="http://127.0.0.1:8001",
            session=self.session_state
        )
        self.main_window = None
        
    def capture_window(self, name: str, delay_ms: int = 500):
        """Capture screenshot of current window state."""
        def do_capture():
            if not self.main_window:
                print("Error: No window to capture")
                return
                
            # Process events to ensure UI is updated
            QApplication.processEvents()
            
            # Grab the window
            pixmap = self.main_window.grab()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.screenshot_count:02d}_{name}_{timestamp}.png"
            filepath = self.output_dir / filename
            
            # Save screenshot
            if pixmap.save(str(filepath)):
                self.screenshot_count += 1
                print(f"✓ Captured: {filename} ({pixmap.width()}x{pixmap.height()})")
            else:
                print(f"✗ Failed to save: {filename}")
        
        QTimer.singleShot(delay_ms, do_capture)
    
    def setup_window_size(self, width: int = 1400, height: int = 900):
        """Set window to optimal size for screenshots."""
        if self.main_window:
            self.main_window.resize(width, height)
            QApplication.processEvents()
            
    def load_image_directly(self, image_path: Path):
        """Load an image directly into the app."""
        if self.main_window and image_path.exists():
            try:
                self.main_window._load_image_from_path(str(image_path))
                print(f"   📄 Loaded: {image_path.name}")
                QApplication.processEvents()
            except Exception as e:
                print(f"   ⚠️  Load image error: {e}")
    
    def simulate_selection(self):
        """Simulate drawing a selection rectangle."""
        if self.main_window and hasattr(self.main_window, 'src_view'):
            src_view = self.main_window.src_view
            if src_view.has_image():
                pixmap_item = src_view.pixmap_item
                if pixmap_item:
                    pixmap = pixmap_item.pixmap()
                    # Create selection (centered, 60% of image size)
                    img_width = pixmap.width()
                    img_height = pixmap.height()
                    sel_width = int(img_width * 0.6)
                    sel_height = int(img_height * 0.6)
                    sel_x = (img_width - sel_width) // 2
                    sel_y = (img_height - sel_height) // 2
                    
                    src_view.set_selection_from_coords(
                        sel_x,
                        sel_y,
                        sel_x + sel_width,
                        sel_y + sel_height,
                    )
                    QApplication.processEvents()
                    print(f"   🖱️  Selection: {sel_width}x{sel_height} at ({sel_x}, {sel_y})")
    
    def adjust_threshold(self, value: int):
        """Adjust threshold slider."""
        if self.main_window and hasattr(self.main_window, 'threshold'):
            self.main_window.threshold.setValue(value)
            QApplication.processEvents()
            print(f"   🎚️  Threshold: {value}")
    
    def trigger_extraction(self):
        """Trigger extraction process."""
        if self.main_window and hasattr(self.main_window, 'on_preview'):
            try:
                self.main_window.on_preview()
                QApplication.processEvents()
                print(f"   ⚡ Extraction triggered")
            except Exception as e:
                print(f"   ⚠️  Extraction error: {e}")
    
    def save_to_library(self):
        """Save extracted signature to library."""
        if self.main_window and hasattr(self.main_window, 'on_save_to_library'):
            try:
                self.main_window.on_save_to_library()
                QApplication.processEvents()
                print(f"   💾 Saved to library")
            except Exception as e:
                print(f"   ⚠️  Save error: {e}")
    
    def refresh_library(self):
        """Refresh signature library."""
        if self.main_window and hasattr(self.main_window, '_refresh_library'):
            try:
                self.main_window._refresh_library()
                QApplication.processEvents()
                print(f"   📚 Library refreshed")
            except Exception as e:
                print(f"   ⚠️  Refresh error: {e}")
    
    def zoom_in(self):
        """Zoom in on image."""
        if self.main_window and hasattr(self.main_window, 'src_view'):
            src_view = self.main_window.src_view
            if hasattr(src_view, 'zoom_in'):
                src_view.zoom_in()
                QApplication.processEvents()
                print(f"   🔍+ Zoomed in")
    
    def fit_to_view(self):
        """Fit image to view."""
        if self.main_window and hasattr(self.main_window, '_on_fit'):
            self.main_window._on_fit()
            QApplication.processEvents()
            print(f"   ⛶ Fit to view")
    
    def switch_to_pdf_tab(self):
        """Switch to PDF tab."""
        if self.main_window and hasattr(self.main_window, 'tab_widget'):
            for i in range(self.main_window.tab_widget.count()):
                if "PDF" in self.main_window.tab_widget.tabText(i):
                    self.main_window.tab_widget.setCurrentIndex(i)
                    QApplication.processEvents()
                    print(f"   📄 Switched to PDF tab")
                    return

    def switch_to_tab(self, tab_text: str):
        """Switch to a named current-product tab for capture evidence."""
        if not self.main_window or not hasattr(self.main_window, "tab_widget"):
            return
        for index in range(self.main_window.tab_widget.count()):
            if self.main_window.tab_widget.tabText(index) == tab_text:
                self.main_window.tab_widget.setCurrentIndex(index)
                QApplication.processEvents()
                print(f"   ↪ Switched to {tab_text}")
                return
    
    def load_pdf_directly(self, pdf_path: Path):
        """Load PDF directly."""
        if self.main_window and hasattr(self.main_window, 'pdf_viewer') and pdf_path.exists():
            try:
                self.main_window._current_pdf_path = str(pdf_path)
                self.main_window.pdf_viewer.open_pdf(str(pdf_path))
                QApplication.processEvents()
                print(f"   📄 Loaded PDF: {pdf_path.name}")
            except Exception as e:
                print(f"   ⚠️  PDF load error: {e}")
    
    def refresh_pdf_library(self):
        """Refresh PDF signature library."""
        if self.main_window and hasattr(self.main_window, '_refresh_pdf_signature_library'):
            try:
                self.main_window._refresh_pdf_signature_library()
                QApplication.processEvents()
                print(f"   🔄 PDF library refreshed")
            except Exception as e:
                print(f"   ⚠️  PDF refresh error: {e}")
    
    def select_pdf_signature(self):
        """Select first signature in PDF library."""
        if self.main_window and hasattr(self.main_window, 'pdf_sig_list'):
            sig_list = self.main_window.pdf_sig_list
            if sig_list.count() > 0:
                sig_list.setCurrentRow(0)
                QApplication.processEvents()
                print(f"   ✍️  Signature selected")
    
    def open_license_menu(self):
        """Open license menu."""
        if self.main_window:
            menu_bar = self.main_window.menuBar()
            if menu_bar:
                for action in menu_bar.actions():
                    if "License" in action.text():
                        menu = action.menu()
                        if menu:
                            menu.popup(menu_bar.mapToGlobal(QPoint(10, 30)))
                            QApplication.processEvents()
                            print(f"   🔑 License menu opened")
                        return
    
    def close_menus(self):
        """Close all open menus."""
        if self.main_window:
            menu_bar = self.main_window.menuBar()
            if menu_bar:
                for action in menu_bar.actions():
                    menu = action.menu()
                    if menu and menu.isVisible():
                        menu.close()
                QApplication.processEvents()
    
    def open_help_menu(self):
        """Open help menu."""
        if self.main_window:
            menu_bar = self.main_window.menuBar()
            if menu_bar:
                for action in menu_bar.actions():
                    if "Help" in action.text():
                        menu = action.menu()
                        if menu:
                            menu.popup(menu_bar.mapToGlobal(QPoint(100, 30)))
                            QApplication.processEvents()
                            print(f"   ❓ Help menu opened")
                        return
    
    def run_ultra_comprehensive_sequence(self):
        """Run ultra-comprehensive screenshot capture sequence."""
        print("\n🎬 Starting ULTRA-COMPREHENSIVE screenshot capture...")
        print(f"📁 Saving to: {self.output_dir}")
        print(f"📸 Using assets:")
        print(f"   • Signature: {self.signature_image.name}")
        print(f"   • PDF: {self.demo_pdf.name}\n")
        
        # Verify assets
        if not self.signature_image.exists():
            print(f"❌ Signature image not found: {self.signature_image}")
            return
        if not self.demo_pdf.exists():
            print(f"⚠️  Demo PDF not found (PDF screenshots will be skipped)")
        
        # Create main window
        self.main_window = MainWindow(
            self.api_client,
            self.session_state,
            backend_manager=None,
            window_title=self.profile.resolve_title(),
            workflow_premium_enabled=self.profile.premium_ui,
            onboarding_default_plan_id=self.profile.default_plan_id,
            show_onboarding_upgrade_card=not self.profile.premium_ui,
        )
        
        # Set window size
        self.setup_window_size(1400, 900)
        self.main_window.show()
        QApplication.processEvents()
        
        # ULTRA-COMPREHENSIVE capture sequence
        sequence = [
            # PART 1: INITIAL STATE
            (1000, lambda: self.capture_window("01_main_interface_empty"), 
             "1. Main interface - empty"),
            
            (2000, lambda: self.capture_window("02_menu_bar"),
             "2. Menu bar and toolbar"),
            
            # PART 2: IMAGE LOADING
            (3000, lambda: self.load_image_directly(self.signature_image),
             "Loading signature image"),
            
            (4500, lambda: self.capture_window("03_image_loaded"),
             "3. Image loaded"),
            
            (5500, lambda: self.capture_window("04_extraction_controls"),
             "4. Extraction controls"),
            
            # PART 3: ZOOM & NAVIGATION
            (6500, lambda: self.zoom_in(),
             "Zooming in"),
            
            (7500, lambda: self.capture_window("05_zoomed_in"),
             "5. Zoomed in view"),
            
            (8500, lambda: self.fit_to_view(),
             "Fitting to view"),
            
            (9500, lambda: self.capture_window("06_fit_to_view"),
             "6. Fit to view"),
            
            # PART 4: SELECTION & CROPPING
            (10500, lambda: self.simulate_selection(),
             "Drawing selection/crop area"),
            
            (11500, lambda: self.capture_window("07_selection_drawn"),
             "7. Selection/crop area drawn"),
            
            # PART 5: THRESHOLD SLIDER
            (12500, lambda: self.adjust_threshold(150),
             "Adjusting threshold slider"),
            
            (13500, lambda: self.capture_window("08_threshold_low"),
             "8. Threshold slider - low"),
            
            (14500, lambda: self.adjust_threshold(200),
             "Adjusting threshold slider"),
            
            (15500, lambda: self.capture_window("09_threshold_medium"),
             "9. Threshold slider - medium"),
            
            (16500, lambda: self.adjust_threshold(230),
             "Adjusting threshold slider"),
            
            (17500, lambda: self.capture_window("10_threshold_high"),
             "10. Threshold slider - high"),
            
            # PART 6: EXTRACTION WORKFLOW
            (18500, lambda: self.adjust_threshold(200),
             "Resetting threshold"),
            
            (19500, lambda: self.trigger_extraction(),
             "Processing extraction"),
            
            (21000, lambda: self.capture_window("11_extraction_result"),
             "11. Extraction result"),
            
            (22000, lambda: self.capture_window("12_preview_pane"),
             "12. Preview pane detail"),
            
            (23000, lambda: self.capture_window("13_result_pane"),
             "13. Result pane detail"),
            
            # PART 7: LIBRARY MANAGEMENT
            (24000, lambda: self.save_to_library(),
             "Saving to library"),
            
            (25500, lambda: self.refresh_library(),
             "Refreshing library"),
            
            (26500, lambda: self.capture_window("14_signature_library"),
             "14. Signature library"),
            
            # PART 8: MENUS & POPUPS
            (27500, lambda: self.open_license_menu(),
             "Opening license menu"),
            
            (28500, lambda: self.capture_window("15_license_menu"),
             "15. License menu popup"),
            
            (29000, lambda: self.close_menus(),
             "Closing menus"),
            
            (30000, lambda: self.open_help_menu(),
             "Opening help menu"),
            
            (31000, lambda: self.capture_window("16_help_menu"),
             "16. Help menu popup"),
            
            (31500, lambda: self.close_menus(),
             "Closing menus"),
            
            # PART 9: PDF TAB
            (32500, lambda: self.switch_to_pdf_tab(),
             "Switching to PDF tab"),
            
            (33500, lambda: self.capture_window("17_pdf_tab_empty"),
             "17. PDF tab - empty"),
            
            (34500, lambda: self.capture_window("18_pdf_controls"),
             "18. PDF controls panel"),
        ]
        
        # Add PDF workflow if available
        if self.demo_pdf.exists():
            sequence.extend([
                (35500, lambda: self.load_pdf_directly(self.demo_pdf),
                 "Loading PDF"),
                
                (37000, lambda: self.capture_window("19_pdf_loaded"),
                 "19. PDF loaded"),
                
                (38000, lambda: self.refresh_pdf_library(),
                 "Refreshing PDF library"),
                
                (39000, lambda: self.capture_window("20_pdf_library"),
                 "20. PDF signature library"),
                
                (40000, lambda: self.select_pdf_signature(),
                 "Selecting signature"),
                
                (41000, lambda: self.capture_window("21_pdf_signature_selected"),
                 "21. Signature selected"),
                
                (42000, lambda: self.capture_window("22_pdf_workflow_complete"),
                 "22. PDF workflow complete"),
            ])
        
        # PART 10: FINAL STATES
        final_delay = 43000 if self.demo_pdf.exists() else 35500
        sequence.extend([
            (final_delay, lambda: self.switch_to_tab("Workflow Dashboard"),
             "Switching to Workflow Dashboard"),
            (final_delay + 1000, lambda: self.capture_window("23_workflow_dashboard"),
             "23. Workflow Dashboard"),
            (final_delay + 2000, lambda: self.switch_to_tab("Workflow Grants"),
             "Switching to Workflow Grants"),
            (final_delay + 3000, lambda: self.capture_window("24_workflow_grants"),
             "24. Workflow Grants"),
            (final_delay + 4000, lambda: self.switch_to_tab("Recipe Builder"),
             "Switching to Recipe Builder"),
            (final_delay + 5000, lambda: self.capture_window("25_recipe_builder"),
             "25. Recipe Builder"),
            (final_delay + 6000, lambda: self.switch_to_tab("Vault"),
             "Switching to Vault"),
            (final_delay + 7000, lambda: self.capture_window("26_vault"),
             "26. Vault"),
            (final_delay + 8000, lambda: self.main_window.tab_widget.setCurrentIndex(0),
             "Switching back to extraction tab"),
            (final_delay + 9000, lambda: self.capture_window("27_extraction_final"),
             "27. Extraction tab final"),
            (final_delay + 10000, lambda: self.capture_window("28_full_interface"),
             "28. Full interface overview"),
        ])
        
        # Execute sequence
        print("\n📋 CAPTURE SEQUENCE:")
        print("=" * 70)
        for delay, action, description in sequence:
            print(f"⏱️  {delay/1000:>5.1f}s: {description}")
            QTimer.singleShot(delay, action)
        
        # Finalize
        final_delay = sequence[-1][0] + 3000
        print(f"⏱️  {final_delay/1000:>5.1f}s: Finalizing")
        print("=" * 70)
        QTimer.singleShot(final_delay, self.finalize)
        
    def finalize(self):
        """Finalize and cleanup."""
        print(f"\n" + "=" * 70)
        print(f"✅ CAPTURE COMPLETE!")
        print("=" * 70)
        print(f"📸 Total screenshots: {self.screenshot_count}")
        print(f"📁 Location: {self.output_dir}")
        print(f"\n💡 Review screenshots: open {self.output_dir}")
        print("=" * 70)
        
        if self.main_window:
            self.main_window.close()
        
        QTimer.singleShot(500, self.app.quit)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ultra-comprehensive screenshot capture for SignKit"
    )
    parser.add_argument(
        "--output",
        default="screenshots",
        help="Output directory (default: screenshots/)"
    )
    parser.add_argument(
        "--profile",
        choices=("standard", "mac-premium"),
        default="mac-premium",
        help="Current launch profile to capture (default: mac-premium)",
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🎯 ULTRA-COMPREHENSIVE SCREENSHOT CAPTURE")
    print("=" * 70)
    print("\nCaptures ALL features, menus, popups, sliders, cropping areas:")
    print("  ✓ Interface & menus")
    print("  ✓ Image loading & viewing")
    print("  ✓ Zoom & navigation")
    print("  ✓ Selection/cropping areas")
    print("  ✓ Threshold slider (multiple positions)")
    print("  ✓ Extraction workflow")
    print("  ✓ Library management")
    print("  ✓ Menu popups (License, Help)")
    print("  ✓ PDF features & workflow")
    print("\n🎬 Total: 24+ screenshots")
    print("⏱️  Time: ~45-50 seconds")
    print("=" * 70)
    print()
    
    try:
        capturer = UltraComprehensiveScreenshotCapture(
            output_dir=args.output,
            profile_name=args.profile,
        )
        capturer.run_ultra_comprehensive_sequence()
        return capturer.app.exec()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
