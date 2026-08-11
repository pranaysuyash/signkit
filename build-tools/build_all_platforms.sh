#!/bin/bash
# Comprehensive multi-platform build script
# Builds for macOS (ARM64 + Intel), Windows, and Linux

set -e

echo "======================================================="
echo "  SignKit - Multi-Platform Distribution Builder"
echo "======================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Detect current platform
OS=$(uname -s)
ARCH=$(uname -m)

echo "Current Platform:"
echo "  OS: $OS"
echo "  Architecture: $ARCH"
echo ""

# Determine what can be built natively
CAN_BUILD_MACOS_ARM=false
CAN_BUILD_MACOS_INTEL=false
CAN_BUILD_WINDOWS=false
CAN_BUILD_LINUX=false
BUILD_MACOS_PREMIUM=${BUILD_MACOS_PREMIUM:-true}

case "$OS" in
    Darwin)
        echo -e "${GREEN}✓ Running on macOS${NC}"
        if [ "$ARCH" = "arm64" ]; then
            CAN_BUILD_MACOS_ARM=true
            echo -e "${GREEN}  ✓ Can build: macOS ARM64 (native)${NC}"
            echo -e "${YELLOW}  ⚠ Cannot build: macOS Intel (need Intel Mac or CI/CD)${NC}"
        elif [ "$ARCH" = "x86_64" ]; then
            CAN_BUILD_MACOS_ARM=true
            CAN_BUILD_MACOS_INTEL=true
            echo -e "${GREEN}  ✓ Can build: macOS Intel (native)${NC}"
            echo -e "${GREEN}  ✓ Can build: macOS ARM64 (via Rosetta)${NC}"
        fi
        echo -e "${YELLOW}  ⚠ Cannot build: Windows (need Windows machine or Wine)${NC}"
        echo -e "${YELLOW}  ⚠ Cannot build: Linux (need Linux machine or Docker)${NC}"
        ;;
    Linux)
        echo -e "${GREEN}✓ Running on Linux${NC}"
        CAN_BUILD_LINUX=true
        echo -e "${GREEN}  ✓ Can build: Linux (native)${NC}"
        echo -e "${YELLOW}  ⚠ Cannot build: macOS (need macOS machine)${NC}"
        echo -e "${YELLOW}  ⚠ Cannot build: Windows (need Windows machine or Wine)${NC}"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        echo -e "${GREEN}✓ Running on Windows${NC}"
        CAN_BUILD_WINDOWS=true
        echo -e "${GREEN}  ✓ Can build: Windows (native)${NC}"
        echo -e "${YELLOW}  ⚠ Cannot build: macOS (need macOS machine)${NC}"
        echo -e "${YELLOW}  ⚠ Cannot build: Linux (need Linux machine or WSL)${NC}"
        ;;
    *)
        echo -e "${RED}✗ Unknown operating system: $OS${NC}"
        exit 1
        ;;
esac

echo ""
echo "======================================================="
echo "  Build Options"
echo "======================================================="
echo ""

# Parse command line arguments
BUILD_TARGET=${1:-"native"}

case "$BUILD_TARGET" in
    "native")
        echo "Building for current platform only..."
        ;;
    "macos")
        if [ "$CAN_BUILD_MACOS_ARM" = false ] && [ "$CAN_BUILD_MACOS_INTEL" = false ]; then
            echo -e "${RED}✗ Cannot build macOS on this platform${NC}"
            exit 1
        fi
        echo "Building macOS versions..."
        ;;
    "windows")
        if [ "$CAN_BUILD_WINDOWS" = false ]; then
            echo -e "${RED}✗ Cannot build Windows on this platform${NC}"
            echo "Suggestion: Use a Windows machine or GitHub Actions"
            exit 1
        fi
        echo "Building Windows version..."
        ;;
    "linux")
        if [ "$CAN_BUILD_LINUX" = false ]; then
            echo -e "${RED}✗ Cannot build Linux on this platform${NC}"
            echo "Suggestion: Use a Linux machine, Docker, or GitHub Actions"
            exit 1
        fi
        echo "Building Linux version..."
        ;;
    "all")
        echo "Building all possible platforms..."
        ;;
    *)
        echo "Usage: $0 [native|macos|windows|linux|all]"
        echo ""
        echo "Options:"
        echo "  native  - Build for current platform only (default)"
        echo "  macos   - Build macOS versions (ARM64 + Intel if possible)"
        echo "  windows - Build Windows version"
        echo "  linux   - Build Linux version"
        echo "  all     - Build all possible platforms"
        exit 1
        ;;
esac

echo ""

# Activate virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Activating virtual environment..."
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    else
        echo -e "${RED}✗ Virtual environment not found${NC}"
        echo "Please run: python3 -m venv venv && source venv/bin/activate"
        exit 1
    fi
fi

# Check PyInstaller
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

echo ""
echo "======================================================="
echo "  Starting Builds"
echo "======================================================="
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist
mkdir -p dist
echo -e "${GREEN}✓ Build directories cleaned${NC}"
echo ""

BUILD_COUNT=0
SUCCESS_COUNT=0

# Build macOS ARM64
if [ "$CAN_BUILD_MACOS_ARM" = true ] && ([ "$BUILD_TARGET" = "native" ] || [ "$BUILD_TARGET" = "macos" ] || [ "$BUILD_TARGET" = "all" ]); then
    echo "-------------------------------------------------------"
    echo "  Building: macOS ARM64 (Apple Silicon)"
    echo "-------------------------------------------------------"
    BUILD_COUNT=$((BUILD_COUNT + 1))
    
    if python build-tools/build.py --build-platform darwin --profile standard --spec build-tools/SignatureExtractor_macOS.spec; then
        if [ -d "dist/SignKit.app" ]; then
            mv dist/SignKit.app dist/SignKit_ARM64.app
            APP_SIZE=$(du -sh dist/SignKit_ARM64.app | cut -f1)
            echo -e "${GREEN}✓ macOS ARM64 build completed ($APP_SIZE)${NC}"
            
            # Create DMG
            echo "Creating DMG..."
            hdiutil create \
                -volname "SignKit (Apple Silicon)" \
                -srcfolder dist/SignKit_ARM64.app \
                -ov \
                -format UDZO \
                dist/SignKit_macOS_ARM64.dmg 2>/dev/null
            
            DMG_SIZE=$(du -sh dist/SignKit_macOS_ARM64.dmg | cut -f1)
            echo -e "${GREEN}✓ DMG created: SignKit_macOS_ARM64.dmg ($DMG_SIZE)${NC}"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo -e "${RED}✗ macOS ARM64 build failed${NC}"
        fi
    else
        echo -e "${RED}✗ macOS ARM64 build failed${NC}"
    fi
    echo ""
fi

# Build macOS Intel
if [ "$CAN_BUILD_MACOS_INTEL" = true ] && ([ "$BUILD_TARGET" = "macos" ] || [ "$BUILD_TARGET" = "all" ]); then
    echo "-------------------------------------------------------"
    echo "  Building: macOS Intel (x86_64)"
    echo "-------------------------------------------------------"
    BUILD_COUNT=$((BUILD_COUNT + 1))
    
    if python build-tools/build.py --build-platform darwin --profile standard --spec build-tools/SignatureExtractor_Intel.spec; then
        if [ -d "dist/SignKit.app" ]; then
            mv dist/SignKit.app dist/SignKit_Intel.app
            APP_SIZE=$(du -sh dist/SignKit_Intel.app | cut -f1)
            echo -e "${GREEN}✓ macOS Intel build completed ($APP_SIZE)${NC}"
            
            # Create DMG
            echo "Creating DMG..."
            hdiutil create \
                -volname "SignKit (Intel)" \
                -srcfolder dist/SignKit_Intel.app \
                -ov \
                -format UDZO \
                dist/SignKit_macOS_Intel.dmg 2>/dev/null
            
            DMG_SIZE=$(du -sh dist/SignKit_macOS_Intel.dmg | cut -f1)
            echo -e "${GREEN}✓ DMG created: SignKit_macOS_Intel.dmg ($DMG_SIZE)${NC}"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo -e "${RED}✗ macOS Intel build failed${NC}"
        fi
    else
        echo -e "${RED}✗ macOS Intel build failed${NC}"
    fi
    echo ""
fi

# Build macOS Premium ARM64 (SignKitPremium)
if [ "$CAN_BUILD_MACOS_ARM" = true ] && [ "$BUILD_MACOS_PREMIUM" = true ] && ([ "$BUILD_TARGET" = "native" ] || [ "$BUILD_TARGET" = "macos" ] || [ "$BUILD_TARGET" = "all" ]); then
    if [ "$ARCH" = "arm64" ]; then
        echo "-------------------------------------------------------"
        echo "  Building: macOS Premium (Apple Silicon)"
        echo "-------------------------------------------------------"
        BUILD_COUNT=$((BUILD_COUNT + 1))
        
        if python build-tools/build.py --build-platform darwin --profile mac-premium --spec build-tools/SignatureExtractor_macOS_Premium.spec; then
            if [ -d "dist/SignKitPremium.app" ]; then
                mv dist/SignKitPremium.app dist/SignKitPremium_ARM64.app
                APP_SIZE=$(du -sh dist/SignKitPremium_ARM64.app | cut -f1)
                echo -e "${GREEN}✓ macOS Premium ARM64 build completed ($APP_SIZE)${NC}"
                
                # Create Premium DMG
                echo "Creating Premium DMG..."
                hdiutil create \
                    -volname "SignKit Premium (Apple Silicon)" \
                    -srcfolder dist/SignKitPremium_ARM64.app \
                    -ov \
                    -format UDZO \
                    dist/SignKit_Premium_macOS_ARM64.dmg 2>/dev/null
                
                DMG_SIZE=$(du -sh dist/SignKit_Premium_macOS_ARM64.dmg | cut -f1)
                echo -e "${GREEN}✓ Premium DMG created: SignKit_Premium_macOS_ARM64.dmg ($DMG_SIZE)${NC}"
                SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            else
                echo -e "${RED}✗ macOS Premium ARM64 build failed${NC}"
            fi
        else
            echo -e "${RED}✗ macOS Premium ARM64 build failed${NC}"
        fi
        echo ""
    else
        echo -e "${YELLOW}⚠ Premium ARM64 build skipped (requires native arm64 host)${NC}"
    fi
fi

# Build Windows
if [ "$CAN_BUILD_WINDOWS" = true ] && ([ "$BUILD_TARGET" = "native" ] || [ "$BUILD_TARGET" = "windows" ] || [ "$BUILD_TARGET" = "all" ]); then
    echo "-------------------------------------------------------"
    echo "  Building: Windows (x64)"
    echo "-------------------------------------------------------"
    BUILD_COUNT=$((BUILD_COUNT + 1))
    
    if python build-tools/build.py --build-platform win64 --profile standard --spec build-tools/SignatureExtractor_Windows.spec; then
        if [ -f "dist/SignKit.exe" ]; then
            mv dist/SignKit.exe dist/SignKit_Windows.exe
            EXE_SIZE=$(du -sh dist/SignKit_Windows.exe | cut -f1)
            echo -e "${GREEN}✓ Windows build completed ($EXE_SIZE)${NC}"
            
            # Create ZIP
            echo "Creating ZIP..."
            cd dist
            zip -q SignKit_Windows.zip SignKit_Windows.exe
            cd ..
            ZIP_SIZE=$(du -sh dist/SignKit_Windows.zip | cut -f1)
            echo -e "${GREEN}✓ ZIP created: SignKit_Windows.zip ($ZIP_SIZE)${NC}"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo -e "${RED}✗ Windows build failed${NC}"
        fi
    else
        echo -e "${RED}✗ Windows build failed${NC}"
    fi
    echo ""
fi

# Build Linux
if [ "$CAN_BUILD_LINUX" = true ] && ([ "$BUILD_TARGET" = "native" ] || [ "$BUILD_TARGET" = "linux" ] || [ "$BUILD_TARGET" = "all" ]); then
    echo "-------------------------------------------------------"
    echo "  Building: Linux (x64)"
    echo "-------------------------------------------------------"
    BUILD_COUNT=$((BUILD_COUNT + 1))
    
    if python build-tools/build.py --build-platform linux --profile standard --spec build-tools/SignatureExtractor_Linux.spec; then
        if [ -f "dist/SignatureExtractor" ]; then
            mv dist/SignatureExtractor dist/SignKit_Linux
            chmod +x dist/SignKit_Linux
            BIN_SIZE=$(du -sh dist/SignKit_Linux | cut -f1)
            echo -e "${GREEN}✓ Linux build completed ($BIN_SIZE)${NC}"
            
            # Create tar.gz
            echo "Creating tar.gz..."
            cd dist
            tar -czf SignKit_Linux.tar.gz SignKit_Linux
            cd ..
            TAR_SIZE=$(du -sh dist/SignKit_Linux.tar.gz | cut -f1)
            echo -e "${GREEN}✓ Archive created: SignKit_Linux.tar.gz ($TAR_SIZE)${NC}"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo -e "${RED}✗ Linux build failed${NC}"
        fi
    else
        echo -e "${RED}✗ Linux build failed${NC}"
    fi
    echo ""
fi

# Build summary
echo "======================================================="
echo "  Build Summary"
echo "======================================================="
echo ""
echo "Builds attempted: $BUILD_COUNT"
echo "Builds successful: $SUCCESS_COUNT"
echo ""

if [ $SUCCESS_COUNT -gt 0 ]; then
    echo -e "${GREEN}Distribution files created:${NC}"
    echo ""
    ls -lh dist/*.dmg dist/*.zip dist/*.tar.gz 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
    echo ""
    
    echo "Upload these files to Gumroad:"
    echo "------------------------------"
    [ -f "dist/SignKit_macOS_ARM64.dmg" ] && echo "  ✓ SignKit_macOS_ARM64.dmg (for M1/M2/M3 Macs)"
    [ -f "dist/SignKit_macOS_Intel.dmg" ] && echo "  ✓ SignKit_macOS_Intel.dmg (for Intel Macs)"
    [ -f "dist/SignKit_Windows.zip" ] && echo "  ✓ SignKit_Windows.zip (for Windows 10+)"
    [ -f "dist/SignKit_Linux.tar.gz" ] && echo "  ✓ SignKit_Linux.tar.gz (for Ubuntu 20.04+)"
    echo ""
fi

if [ $BUILD_COUNT -eq 0 ]; then
    echo -e "${YELLOW}No builds were attempted.${NC}"
    echo "Run with 'all' to build all possible platforms:"
    echo "  ./build_all_platforms.sh all"
elif [ $SUCCESS_COUNT -eq 0 ]; then
    echo -e "${RED}All builds failed. Check the errors above.${NC}"
    exit 1
elif [ $SUCCESS_COUNT -lt $BUILD_COUNT ]; then
    echo -e "${YELLOW}Some builds failed. Check the errors above.${NC}"
else
    echo -e "${GREEN}All builds completed successfully!${NC}"
fi

echo ""
echo "Next steps:"
echo "-----------"
echo "1. Test the builds on their respective platforms"
echo "2. Upload to Gumroad product page"
echo "3. Create LICENSE_INSTRUCTIONS.txt"
echo "4. Test purchase and download flow"
echo ""
