#!/usr/bin/env python3
"""
Quick manual screenshot guide for SignKit.
No backend, no complex initialization - just run the app and take screenshots.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Print manual screenshot guide."""
    
    signature_img = project_root / "desktop_app/resources/signature_template_synthetic_512.jpg"
    demo_pdf = project_root / "assets" / "demo_document.pdf"
    screenshots_dir = project_root / "screenshots"
    
    print("\n" + "="*70)
    print("📸 SIGNKIT SCREENSHOT GUIDE")
    print("="*70)
    print("\n🎯 GOAL: Capture 5-7 professional screenshots for Gumroad")
    
    print("\n" + "="*70)
    print("📁 ASSETS TO USE:")
    print("="*70)
    print(f"   Signature: {signature_img}")
    print(f"   PDF:       {demo_pdf}")
    print(f"   Save to:   {screenshots_dir}/")
    
    print("\n" + "="*70)
    print("🚀 STEP 1: LAUNCH APP")
    print("="*70)
    print("   • Open: dist/SignatureExtractor.app")
    print("   • Resize window to ~1400x900px")
    print("   • Make sure window looks clean")
    
    print("\n" + "="*70)
    print("📸 SCREENSHOTS TO TAKE:")
    print("="*70)
    
    screenshots = [
        {
            "num": 1,
            "name": "01_main_interface",
            "title": "Main Interface - Clean Start",
            "steps": [
                "Fresh app launch",
                "Show empty signature library panel",
                "Toolbar visible at top",
                "Clean, professional look",
            ],
            "cmd": "Cmd+Shift+4, Space, click window"
        },
        {
            "num": 2,
            "name": "02_image_loaded",
            "title": "Signature Image Loaded",
            "steps": [
                f"Open: {signature_img.name}",
                "Image fills viewer area",
                "Signature clearly visible",
                "Zoom/pan controls visible",
            ],
            "cmd": "Cmd+Shift+4, Space, click window"
        },
        {
            "num": 3,
            "name": "03_selection_drawn",
            "title": "Selection Rectangle",
            "steps": [
                "Draw rectangle around signature",
                "Red bounding box clearly visible",
                "Selection handles showing",
                "Coordinates visible if tooltip enabled",
            ],
            "cmd": "Cmd+Shift+4, Space, click window"
        },
        {
            "num": 4,
            "name": "04_extraction_settings",
            "title": "Extraction Panel",
            "steps": [
                "Extraction controls panel visible",
                "Threshold slider showing",
                "Color picker visible",
                "Preview if available",
            ],
            "cmd": "Cmd+Shift+4, Space, click window"
        },
        {
            "num": 5,
            "name": "05_extracted_signature",
            "title": "Extracted Result",
            "steps": [
                "Click 'Extract Signature'",
                "Clean extracted signature visible",
                "Transparent background (checkerboard)",
                "Sharp, professional result",
            ],
            "cmd": "Cmd+Shift+4, Space, click window"
        },
        {
            "num": 6,
            "name": "06_signature_library",
            "title": "Signature Library",
            "steps": [
                "Save extracted signature to library",
                "Library panel shows thumbnails",
                "Multiple signatures if available",
                "Organized, grid layout",
            ],
            "cmd": "Cmd+Shift+4, Space, click window"
        },
        {
            "num": 7,
            "name": "07_pdf_workflow",
            "title": "PDF Signing (Optional)",
            "steps": [
                "Switch to PDF tab",
                f"Load: {demo_pdf.name}",
                "Show PDF viewer",
                "Signature ready to place",
            ],
            "cmd": "Cmd+Shift+4, Space, click window"
        }
    ]
    
    for shot in screenshots:
        print(f"\n📷 {shot['num']}. {shot['title']}")
        print(f"   Save as: {shot['name']}.png")
        print("   Steps:")
        for step in shot['steps']:
            print(f"      • {step}")
        print(f"   Capture: {shot['cmd']}")
    
    print("\n" + "="*70)
    print("✨ SCREENSHOT TIPS:")
    print("="*70)
    print("   ✓ Clean desktop (hide other windows)")
    print("   ✓ Good lighting (no screen glare)")
    print("   ✓ Consistent window size (1400x900)")
    print("   ✓ Hide personal info (use demo data)")
    print("   ✓ PNG format (for transparency)")
    print("   ✓ High resolution (Retina/HiDPI)")
    print("   ✓ Professional appearance")
    
    print("\n" + "="*70)
    print("🎨 POST-PROCESSING (Optional):")
    print("="*70)
    print("   1. Crop to remove menu bar/desktop")
    print("   2. Add subtle drop shadow")
    print("   3. Resize if needed (max 2000px wide)")
    print("   4. Compress with ImageOptim/TinyPNG")
    print("   5. Review on different screens")
    
    print("\n" + "="*70)
    print("📤 UPLOAD TO GUMROAD:")
    print("="*70)
    print("   1. Go to: pranaysuyash.gumroad.com/l/signkit-v1")
    print("   2. Click 'Edit product'")
    print("   3. Scroll to 'Product images'")
    print("   4. Upload 5-7 screenshots")
    print("   5. Arrange in logical order")
    print("   6. Set first image as hero/cover")
    
    print("\n" + "="*70)
    print("⚡ QUICK START:")
    print("="*70)
    print("   1. open dist/SignatureExtractor.app")
    print(f"   2. Drag {signature_img.name} into app")
    print("   3. Follow screenshot guide above")
    print(f"   4. Save to: {screenshots_dir}/")
    print("   5. Upload to Gumroad")
    
    print("\n" + "="*70)
    print("✅ CHECKLIST:")
    print("="*70)
    print("   [ ] App launched and sized properly")
    print("   [ ] Screenshot 1: Main interface")
    print("   [ ] Screenshot 2: Image loaded")
    print("   [ ] Screenshot 3: Selection drawn")
    print("   [ ] Screenshot 4: Extraction panel")
    print("   [ ] Screenshot 5: Extracted result")
    print("   [ ] Screenshot 6: Signature library")
    print("   [ ] Screenshot 7: PDF workflow (optional)")
    print("   [ ] All saved to screenshots/ folder")
    print("   [ ] Reviewed for quality")
    print("   [ ] Uploaded to Gumroad")
    
    print("\n" + "="*70)
    print(f"📁 Screenshots will be saved to:")
    print(f"   {screenshots_dir}/")
    print("="*70 + "\n")
    
    # Create screenshots directory
    screenshots_dir.mkdir(exist_ok=True)
    print(f"✓ Created directory: {screenshots_dir}\n")


if __name__ == "__main__":
    main()
