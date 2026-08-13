#!/usr/bin/env python3
"""
Automated screenshot capture for SignKit marketing materials.
Takes screenshots of key app screens for Gumroad product page.
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer, QSize
    from PySide6.QtGui import QScreen
except ImportError:
    print("Error: PySide6 not installed")
    print("Run: pip install PySide6")
    sys.exit(1)

# Import app components
from desktop_app.views.main_window import MainWindow
from desktop_app.api.client import ApiClient
from desktop_app.state.session import SessionState


class ScreenshotCapture:
    """Automates screenshot capture for marketing materials."""
    
    def __init__(self, output_dir: str = "screenshots"):
        self.output_dir = Path(project_root) / output_dir
        self.output_dir.mkdir(exist_ok=True)
        self.screenshot_count = 0
        
        # Test assets
        self.signature_image = project_root / "desktop_app/resources/signature_template_synthetic_512.jpg"
        self.demo_pdf = project_root / "assets" / "demo_document.pdf"
        
        # Initialize Qt Application
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        # Initialize app components (offline mode for screenshots)
        self.session_state = SessionState()
        self.api_client = ApiClient(
            base_url="http://127.0.0.1:8001",
            session=self.session_state
        )
        self.main_window = None
        
    def capture_window(self, name: str, delay_ms: int = 500):
        """
        Capture screenshot of current window state.
        
        Args:
            name: Base name for screenshot file
            delay_ms: Delay before capture (allows UI to settle)
        """
        def do_capture():
            if not self.main_window:
                print("Error: No window to capture")
                return
                
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
        
        # Schedule capture after delay
        QTimer.singleShot(delay_ms, do_capture)
    
    def setup_window_size(self, width: int = 1200, height: int = 800):
        """Set window to optimal size for screenshots."""
        if self.main_window:
            self.main_window.resize(width, height)
            
    def load_image(self, image_path: Path):
        """Load an image into the app."""
        if self.main_window and image_path.exists():
            # Use the main window's load_image method
            self.main_window.load_image(str(image_path))
            print(f"   📄 Loaded: {image_path.name}")
    
    def simulate_selection(self):
        """Simulate drawing a selection rectangle."""
        if self.main_window and hasattr(self.main_window, 'image_view'):
            # Get image view widget
            image_view = self.main_window.image_view
            # Simulate selection (this would need actual UI automation)
            print(f"   🖱️  Selection simulated (manual step required)")
    
    def run_capture_sequence(self):
        """Run automated screenshot capture sequence."""
        print("\n🎬 Starting automated screenshot capture...")
        print(f"📁 Saving to: {self.output_dir}")
        print(f"📸 Using assets:")
        print(f"   • Signature: {self.signature_image.name}")
        print(f"   • PDF: {self.demo_pdf.name}\n")
        
        # Verify assets exist
        if not self.signature_image.exists():
            print(f"❌ Signature image not found: {self.signature_image}")
            return
        if not self.demo_pdf.exists():
            print(f"❌ Demo PDF not found: {self.demo_pdf}")
            return
        
        # Create main window
        self.main_window = MainWindow(
            self.api_client,
            self.session_state,
            backend_manager=None
        )
        
        # Set optimal window size for screenshots
        self.setup_window_size(1400, 900)
        self.main_window.show()
        
        # Capture sequence with delays and actions
        sequence = [
            (1000, lambda: self.capture_window("01_main_interface"), 
             "Main interface - empty state"),
            
            (2500, lambda: self.load_image(self.signature_image),
             "Loading signature image"),
            
            (3500, lambda: self.capture_window("02_image_loaded"),
             "Image loaded in viewer"),
            
            (5000, lambda: self.capture_window("03_zoom_view"),
             "Zoomed view of signature"),
            
            (6500, lambda: self.load_image(self.demo_pdf),
             "Loading PDF document"),
            
            (7500, lambda: self.capture_window("04_pdf_loaded"),
             "PDF document loaded"),
        ]
        
        for delay, action, description in sequence:
            print(f"⏱️  {delay/1000:.1f}s: {description}")
            QTimer.singleShot(delay, action)
        
        # Close app after all captures
        QTimer.singleShot(9000, self.finalize)
        
    def finalize(self):
        """Finalize and cleanup."""
        print(f"\n✅ Captured {self.screenshot_count} screenshots")
        print(f"📁 Location: {self.output_dir}")
        print("\n💡 Next steps:")
        print("   1. Review screenshots in screenshots/ folder")
        print("   2. Edit/crop as needed")
        print("   3. Upload to Gumroad product page")
        
        if self.main_window:
            self.main_window.close()
        
        # Exit after brief delay
        QTimer.singleShot(500, self.app.quit)


class ManualScreenshotGuide:
    """Provides instructions for manual screenshot capture."""
    
    @staticmethod
    def print_guide():
        """Print step-by-step guide for manual screenshots."""
        print("\n" + "="*70)
        print("📸 MANUAL SCREENSHOT GUIDE")
        print("="*70)
        
        screenshots = [
            {
                "num": 1,
                "name": "Main Interface",
                "what": "Clean main window with signature library panel",
                "how": [
                    "Launch app: open dist/SignatureExtractor.app",
                    "Make window ~1400x900px",
                    "Show empty signature library",
                    "Take screenshot (Cmd+Shift+4, then Space, click window)"
                ]
            },
            {
                "num": 2,
                "name": "Image Loaded",
                "what": "Image viewer with a signature document loaded",
                "how": [
                    "Click 'Open Image' or drag a document",
                    "Use a sample contract/form with signature",
                    "Zoom to show signature clearly",
                    "Take screenshot"
                ]
            },
            {
                "num": 3,
                "name": "Selection Tool",
                "what": "Rectangle selection around a signature",
                "how": [
                    "Draw selection rectangle around signature",
                    "Show the red bounding box clearly",
                    "Position selection tool panel visible",
                    "Take screenshot"
                ]
            },
            {
                "num": 4,
                "name": "Extraction Settings",
                "what": "Threshold and color adjustment panel",
                "how": [
                    "Open extraction settings",
                    "Show threshold slider",
                    "Display color picker",
                    "Show preview if possible",
                    "Take screenshot"
                ]
            },
            {
                "num": 5,
                "name": "Extracted Signature",
                "what": "Clean extracted signature with transparency",
                "how": [
                    "Complete extraction process",
                    "Show extracted signature preview",
                    "Display transparent background (checkerboard)",
                    "Take screenshot"
                ]
            },
            {
                "num": 6,
                "name": "Export Options",
                "what": "Export dialog with format options",
                "how": [
                    "Click 'Export Signature'",
                    "Show format dropdown (PNG/JPG/PDF)",
                    "Display background options",
                    "Show file name field",
                    "Take screenshot"
                ]
            },
            {
                "num": 7,
                "name": "License Dialog",
                "what": "License activation screen",
                "how": [
                    "Open Settings → License",
                    "Show license activation form",
                    "Display 'Activate License' button",
                    "Take screenshot"
                ]
            }
        ]
        
        for shot in screenshots:
            print(f"\n📷 Screenshot {shot['num']}: {shot['name']}")
            print(f"   What: {shot['what']}")
            print("   How:")
            for step in shot['how']:
                print(f"      • {step}")
        
        print("\n" + "="*70)
        print("💾 SAVE SCREENSHOTS AS:")
        print("="*70)
        print("   Format: 01_main_interface.png, 02_image_loaded.png, etc.")
        print(f"   Location: {Path(project_root) / 'screenshots'}/")
        print("   Size: At least 1200x800px (original window size)")
        print("   Format: PNG (for transparency where needed)")
        
        print("\n" + "="*70)
        print("✨ TIPS FOR GREAT SCREENSHOTS:")
        print("="*70)
        print("   • Use a clean, simple signature sample")
        print("   • Avoid personal information in documents")
        print("   • Keep UI clean (close unnecessary panels)")
        print("   • Use consistent window size across shots")
        print("   • Natural lighting if taking screen photos")
        print("   • Crop to remove desktop/menu bar if needed")
        
        print("\n" + "="*70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Capture screenshots for SignKit marketing"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run automated screenshot capture (limited)"
    )
    parser.add_argument(
        "--guide",
        action="store_true",
        help="Show manual screenshot guide"
    )
    parser.add_argument(
        "--output",
        default="screenshots",
        help="Output directory for screenshots (default: screenshots/)"
    )
    
    args = parser.parse_args()
    
    if args.guide or not args.auto:
        # Show manual guide by default
        ManualScreenshotGuide.print_guide()
        
        if not args.auto:
            print("\n💡 Run with --auto flag for automated capture (basic screenshots only)")
            return 0
    
    if args.auto:
        print("\n⚠️  Automated mode captures basic window states only.")
        print("    For best results, follow manual guide for feature screenshots.\n")
        
        try:
            capturer = ScreenshotCapture(output_dir=args.output)
            capturer.run_capture_sequence()
            return capturer.app.exec()
        except Exception as e:
            print(f"\n❌ Error during automated capture: {e}")
            print("\n💡 Try manual screenshot capture instead (run without --auto)")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
