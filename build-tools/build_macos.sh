#!/bin/bash
# Build script for macOS app bundle

set -e  # Exit on error

echo "=================================="
echo "SignKit macOS Build"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
ARCH=$(uname -m)

echo "Project root: $PROJECT_ROOT"
echo ""
TARGET_MODE=${1:-standard}
case "$TARGET_MODE" in
    standard|premium|both)
        ;;
    *)
        echo "Usage: $0 [standard|premium|both]"
        exit 1
        ;;
esac

# Resolve one interpreter for dependency checks and the build. Prefer the
# current environment, then the maintained project .venv, and only then the
# legacy venv. Do not source a stale environment into this shell.
if [[ -n "${SIGNKIT_PYTHON_BIN:-}" && -x "$SIGNKIT_PYTHON_BIN" ]]; then
    PYTHON_BIN="$SIGNKIT_PYTHON_BIN"
elif [[ -n "${VIRTUAL_ENV:-}" && -x "$VIRTUAL_ENV/bin/python" ]]; then
    PYTHON_BIN="$VIRTUAL_ENV/bin/python"
elif [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
    PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
elif [[ -x "$PROJECT_ROOT/venv/bin/python" ]]; then
    PYTHON_BIN="$PROJECT_ROOT/venv/bin/python"
else
    echo -e "${RED}✗ No usable project Python environment found${NC}"
    echo "Create .venv or set SIGNKIT_PYTHON_BIN to a Python executable."
    exit 1
fi

echo "Using Python: $PYTHON_BIN"

# Check Python version
PYTHON_VERSION=$("$PYTHON_BIN" --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Check if PyInstaller is installed
if ! "$PYTHON_BIN" -c "import PyInstaller" 2>/dev/null; then
    echo -e "${YELLOW}PyInstaller not found. Installing...${NC}"
    "$PYTHON_BIN" -m pip install pyinstaller
fi

# Check other required packages
echo "Checking required packages..."
REQUIRED_PACKAGES=("PySide6:PySide6" "Pillow:PIL" "opencv-python:cv2" "numpy:numpy" "requests:requests")
MISSING_PACKAGES=()

for package_spec in "${REQUIRED_PACKAGES[@]}"; do
    package_name="${package_spec%%:*}"
    module_name="${package_spec##*:}"
    if ! "$PYTHON_BIN" -c "import $module_name" 2>/dev/null; then
        MISSING_PACKAGES+=("$package_name")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}Missing packages: ${MISSING_PACKAGES[*]}${NC}"
    echo "Installing missing packages..."
    "$PYTHON_BIN" -m pip install "${MISSING_PACKAGES[@]}"
fi

echo -e "${GREEN}✓ All required packages available${NC}"
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist
echo -e "${GREEN}✓ Cleaned build directories${NC}"
echo ""

# Build the application(s)
echo "Building macOS application..."
echo "This may take 3-5 minutes..."
echo ""

# Build Standard
build_standard() {
    local spec_file="build-tools/SignatureExtractor_macOS.spec"
    if [ ! -f "$spec_file" ]; then
        echo -e "${RED}✗ Spec file not found: $spec_file${NC}"
        return 1
    fi

    "$PYTHON_BIN" build-tools/build.py \
        --build-platform darwin \
        --profile standard \
        --spec "$spec_file"

    if [ ! -d "dist/SignKit.app" ]; then
        echo -e "${RED}✗ Standard build failed - .app bundle not found${NC}"
        return 1
    fi

    local app_path="dist/SignKit.app"
    APP_SIZE=$(du -sh "$app_path" | cut -f1)
    echo -e "${GREEN}✓ Standard build completed (${APP_SIZE})${NC}"
    echo "App Bundle: $app_path"
    echo "Executable: $(file "$app_path/Contents/MacOS/SignKit" | cut -d: -f2)"
}

# Build Premium
build_premium() {
    local spec_file="build-tools/SignatureExtractor_macOS_Premium.spec"
    if [ ! -f "$spec_file" ]; then
        echo -e "${RED}✗ Spec file not found: $spec_file${NC}"
        return 1
    fi

    "$PYTHON_BIN" build-tools/build.py \
        --build-platform darwin \
        --profile mac-premium \
        --spec "$spec_file"

    if [ ! -d "dist/SignKitPremium.app" ]; then
        echo -e "${RED}✗ Premium build failed - .app bundle not found${NC}"
        return 1
    fi

    local app_path="dist/SignKitPremium.app"
    APP_SIZE=$(du -sh "$app_path" | cut -f1)
    echo -e "${GREEN}✓ Premium build completed (${APP_SIZE})${NC}"
    echo "App Bundle: $app_path"
    echo "Executable: $(file "$app_path/Contents/MacOS/SignKitPremium" | cut -d: -f2)"
}

if [ "$TARGET_MODE" = "standard" ] || [ "$TARGET_MODE" = "both" ]; then
    build_standard
fi

if [ "$TARGET_MODE" = "premium" ] || [ "$TARGET_MODE" = "both" ]; then
    if [ "$ARCH" != "arm64" ]; then
        echo -e "${YELLOW}⚠ Premium macOS build is configured for Apple Silicon only.${NC}"
        echo "   Switch to an arm64 mac host to build SignKit Premium."
    else
        build_premium
    fi
fi

echo ""
echo -e "${GREEN}Build complete!${NC}"

if [ "$TARGET_MODE" != "premium" ]; then
    APP_PATH="dist/SignKit.app"
    if [ -d "$APP_PATH" ] && [ -f "$APP_PATH/Contents/Info.plist" ]; then
        echo ""
        echo "Next Steps:"
        echo "==========="
        echo "1. Test the app:"
        echo "   open $APP_PATH"
        echo ""
        echo "2. Create DMG for distribution (optional):"
        echo "   hdiutil create -volname 'SignKit' -srcfolder $APP_PATH -ov -format UDZO dist/SignKit_macOS.dmg"
        echo ""
    fi
fi
