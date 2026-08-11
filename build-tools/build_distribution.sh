#!/bin/bash
# Comprehensive build script for macOS distribution

set -e

echo "================================================"
echo "  SignKit - Distribution Builder"
echo "================================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Detect current architecture
ARCH=$(uname -m)
echo "Current architecture: $ARCH"
echo ""

# Determine what we can build
if [ "$ARCH" = "arm64" ]; then
    echo -e "${GREEN}✓ Can build: Apple Silicon (arm64)${NC}"
    echo -e "${YELLOW}⚠ Cannot build: Intel (x86_64) on this machine${NC}"
    echo ""
    echo "For Intel build, you need to either:"
    echo "  1. Build on an Intel Mac"
    echo "  2. Use a CI/CD service (GitHub Actions with macos-13 runner)"
    echo "  3. Use cross-compilation (requires Intel Python environment)"
    echo ""
    CAN_BUILD_ARM=true
    CAN_BUILD_INTEL=false
elif [ "$ARCH" = "x86_64" ]; then
    echo -e "${GREEN}✓ Can build: Intel (x86_64)${NC}"
    echo -e "${GREEN}✓ Can build: Apple Silicon (arm64) with Rosetta${NC}"
    echo ""
    CAN_BUILD_ARM=true
    CAN_BUILD_INTEL=true
else
    echo -e "${RED}✗ Unknown architecture: $ARCH${NC}"
    exit 1
fi

# Parse arguments
BUILD_TARGET=${1:-"current"}
BUILD_PREMIUM=${BUILD_PREMIUM:-false}

case "$BUILD_TARGET" in
    "arm64"|"apple-silicon")
        if [ "$CAN_BUILD_ARM" = false ]; then
            echo -e "${RED}✗ Cannot build ARM64 on this machine${NC}"
            exit 1
        fi
        BUILD_ARM=true
        BUILD_INTEL=false
        ;;
    "intel"|"x86_64")
        if [ "$CAN_BUILD_INTEL" = false ]; then
            echo -e "${RED}✗ Cannot build Intel on this machine${NC}"
            echo "Suggestion: Use GitHub Actions or build on Intel Mac"
            exit 1
        fi
        BUILD_ARM=false
        BUILD_INTEL=true
        ;;
    "both"|"universal")
        BUILD_ARM=$CAN_BUILD_ARM
        BUILD_INTEL=$CAN_BUILD_INTEL
        ;;
    "current")
        if [ "$ARCH" = "arm64" ]; then
            BUILD_ARM=true
            BUILD_INTEL=false
        else
            BUILD_ARM=true  # Can build via Rosetta
            BUILD_INTEL=true
        fi
        ;;
    *)
        echo "Usage: $0 [arm64|intel|both|current]"
        echo ""
        echo "Options:"
        echo "  arm64     - Build for Apple Silicon only"
        echo "  intel     - Build for Intel only"
        echo "  both      - Build for both architectures"
        echo "  current   - Build for current architecture (default)"
        exit 1
        ;;
esac

echo "Build Plan:"
echo "-----------"
[ "$BUILD_ARM" = true ] && echo -e "${GREEN}✓ Apple Silicon (arm64)${NC}" || echo "  Skip: Apple Silicon"
[ "$BUILD_INTEL" = true ] && echo -e "${GREEN}✓ Intel (x86_64)${NC}" || echo "  Skip: Intel"
if [ "$BUILD_PREMIUM" = true ]; then
    if [ "$BUILD_ARM" = true ] && [ "$ARCH" = "arm64" ]; then
        echo -e "${GREEN}✓ Premium macOS (Apple Silicon)${NC}"
    else
        echo "  Skip Premium: set BUILD_PREMIUM=true and ARCH=arm64"
    fi
else
    echo "  Skip Premium: set BUILD_PREMIUM=true"
fi
echo ""

read -p "Continue with this build plan? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Build cancelled."
    exit 0
fi

# Activate virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    else
        echo -e "${RED}✗ Virtual environment not found${NC}"
        exit 1
    fi
fi

# Check PyInstaller
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo ""
echo "Cleaning previous builds..."
rm -rf build dist
echo -e "${GREEN}✓ Build directories cleaned${NC}"
echo ""

# Build ARM64 version
if [ "$BUILD_ARM" = true ]; then
    echo "================================================"
    echo "  Building Apple Silicon (ARM64) Version"
    echo "================================================"
    echo ""
    
    python build-tools/build.py \
        --build-platform darwin \
        --profile standard \
        --spec build-tools/SignatureExtractor_macOS.spec
    
    if [ -d "dist/SignKit.app" ]; then
        echo -e "${GREEN}✓ ARM64 build completed${NC}"
        APP_SIZE=$(du -sh dist/SignKit.app | cut -f1)
        echo "  Size: $APP_SIZE"
        
        # Rename to indicate architecture
        mv dist/SignKit.app dist/SignKit_ARM64.app
        echo "  Output: dist/SignKit_ARM64.app"
    else
        echo -e "${RED}✗ ARM64 build failed${NC}"
        exit 1
    fi
    echo ""
fi

# Build Intel version
if [ "$BUILD_INTEL" = true ]; then
    echo "================================================"
    echo "  Building Intel (x86_64) Version"
    echo "================================================"
    echo ""
    
    python build-tools/build.py \
        --build-platform darwin \
        --profile standard \
        --spec build-tools/SignatureExtractor_Intel.spec
    
    if [ -d "dist/SignKit.app" ]; then
        echo -e "${GREEN}✓ Intel build completed${NC}"
        APP_SIZE=$(du -sh dist/SignKit.app | cut -f1)
        echo "  Size: $APP_SIZE"
        mv dist/SignKit.app dist/SignKit_Intel.app
        echo "  Output: dist/SignKit_Intel.app"
    else
        echo -e "${RED}✗ Intel build failed${NC}"
        exit 1
    fi
    echo ""
fi

# Create distribution packages
echo "================================================"
echo "  Creating Distribution Packages"
echo "================================================"
echo ""

if [ -d "dist/SignKit_ARM64.app" ]; then
    echo "Creating DMG for Apple Silicon..."
    hdiutil create \
        -volname "SignKit (Apple Silicon)" \
        -srcfolder dist/SignKit_ARM64.app \
        -ov \
        -format UDZO \
        dist/SignKit_macOS_ARM64.dmg
    
    DMG_SIZE=$(du -sh dist/SignKit_macOS_ARM64.dmg | cut -f1)
    echo -e "${GREEN}✓ ARM64 DMG created: $DMG_SIZE${NC}"
fi

if [ -f "dist/SignKit_Premium_macOS_ARM64.dmg" ]; then
    echo -e "${GREEN}✓ Premium macOS (ARM64)${NC}"
    echo "  DMG:  dist/SignKit_Premium_macOS_ARM64.dmg"
    echo "  For:  premium tier on Apple Silicon Macs"
    echo ""
fi


if [ "$BUILD_PREMIUM" = true ] && [ "$BUILD_ARM" = true ] && [ "$ARCH" = "arm64" ]; then
    echo "Creating Premium DMG for Apple Silicon..."
    python build-tools/build.py \
        --build-platform darwin \
        --profile mac-premium \
        --spec build-tools/SignatureExtractor_macOS_Premium.spec
    mv dist/SignKitPremium.app dist/SignKitPremium_ARM64.app
    hdiutil create \
        -volname "SignKit Premium (Apple Silicon)" \
        -srcfolder dist/SignKitPremium_ARM64.app \
        -ov \
        -format UDZO \
        dist/SignKit_Premium_macOS_ARM64.dmg
    if [ -f "dist/SignKit_Premium_macOS_ARM64.dmg" ]; then
        DMG_SIZE=$(du -sh dist/SignKit_Premium_macOS_ARM64.dmg | cut -f1)
        echo -e "${GREEN}✓ Premium ARM64 DMG created: $DMG_SIZE${NC}"
    fi
    if [ -d "dist/SignKitPremium_ARM64.app" ]; then
        rm -rf dist/SignKitPremium_ARM64.app
    fi
fi


if [ -d "dist/SignKit_Intel.app" ]; then
    echo "Creating DMG for Intel..."
    hdiutil create \
        -volname "SignKit (Intel)" \
        -srcfolder dist/SignKit_Intel.app \
        -ov \
        -format UDZO \
        dist/SignKit_macOS_Intel.dmg
    
    DMG_SIZE=$(du -sh dist/SignKit_macOS_Intel.dmg | cut -f1)
    echo -e "${GREEN}✓ Intel DMG created: $DMG_SIZE${NC}"
fi

echo ""
echo "================================================"
echo "  Build Summary"
echo "================================================"
echo ""

if [ -d "dist/SignKit_ARM64.app" ]; then
    echo -e "${GREEN}✓ Apple Silicon (ARM64)${NC}"
    echo "  App:  dist/SignKit_ARM64.app"
    echo "  DMG:  dist/SignKit_macOS_ARM64.dmg"
    echo "  Arch: arm64"
    echo "  For:  macOS 11.0+ on Apple Silicon Macs"
    echo ""
fi

if [ -d "dist/SignKit_Intel.app" ]; then
    echo -e "${GREEN}✓ Intel (x86_64)${NC}"
    echo "  App:  dist/SignKit_Intel.app"
    echo "  DMG:  dist/SignKit_macOS_Intel.dmg"
    echo "  Arch: x86_64"
    echo "  For:  macOS 10.13+ on Intel Macs"
    echo ""
fi

echo "Distribution Strategy:"
echo "----------------------"
echo "1. Upload BOTH DMG files to Gumroad"
echo "2. Let customers choose based on their Mac:"
echo "   - M1/M2/M3 Mac → ARM64 version"
echo "   - Intel Mac → Intel version"
echo ""
echo "3. Or create a README that detects automatically:"
echo "   - Check System Info → About This Mac → Chip"
echo "   - Download appropriate version"
echo ""

echo -e "${GREEN}Build complete!${NC}"
echo ""
echo "Testing:"
echo "--------"
echo "Test ARM64: open dist/SignKit_ARM64.app"
[ -d "dist/SignKit_Intel.app" ] && echo "Test Intel: open dist/SignKit_Intel.app"
echo ""
