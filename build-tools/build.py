#!/usr/bin/env python3
"""
Build script for packaging SignKit using PyInstaller.

This script provides a convenient interface for building the application
for different platforms and configurations.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

STANDARD_PROFILE_SPEC_BY_PLATFORM = {
    "darwin": "build-tools/SignatureExtractor_macOS.spec",
    "linux": "build-tools/SignatureExtractor_Linux.spec",
    "win32": "build-tools/SignatureExtractor_Windows.spec",
    "win64": "build-tools/SignatureExtractor_Windows.spec",
}

PLATFORM_DARWIN = "darwin"
PLATFORM_WINDOWS = "win32"
PLATFORM_LINUX = "linux"

PREMIUM_PROFILE_SPEC_BY_PLATFORM = {
    "darwin": "build-tools/SignatureExtractor_macOS_Premium.spec",
}

_DEFAULT_MAIN_ENTRYPOINTS = {
    "standard": "desktop_app/main.py",
    "mac-premium": "desktop_app/main_macos_premium.py",
}


def detect_platform_for_build() -> str:
    """Normalize the target platform key used for build routing."""

    if sys.platform.startswith("linux"):
        return PLATFORM_LINUX
    if sys.platform == "darwin":
        return PLATFORM_DARWIN
    if sys.platform.startswith("win"):
        return PLATFORM_WINDOWS
    return sys.platform


def run_command(cmd: List[str], cwd: str = None) -> int:
    """Run a command and return the exit code."""
    print(f"Running: {' '.join(cmd)}")
    if cwd:
        print(f"Working directory: {cwd}")

    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


def resolve_spec_file(profile_name: str, platform_hint: Optional[str] = None) -> Path:
    """Resolve the preferred spec file for a profile + platform combination."""

    target_platform = platform_hint or detect_platform_for_build()
    if profile_name == "mac-premium" and target_platform != PLATFORM_DARWIN:
        raise ValueError("Profile 'mac-premium' is only supported on darwin targets.")
    if profile_name == "mac-premium":
        return Path(PREMIUM_PROFILE_SPEC_BY_PLATFORM[target_platform])
    if target_platform == PLATFORM_DARWIN:
        return Path(STANDARD_PROFILE_SPEC_BY_PLATFORM[PLATFORM_DARWIN])
    if target_platform in STANDARD_PROFILE_SPEC_BY_PLATFORM:
        return Path(STANDARD_PROFILE_SPEC_BY_PLATFORM[target_platform])
    return Path("signature_extractor.spec")


def resolve_entrypoint(profile_name: str) -> Path:
    """Resolve the expected launch entrypoint for a profile."""

    if profile_name not in _DEFAULT_MAIN_ENTRYPOINTS:
        raise ValueError(f"Unknown launch profile for entrypoint resolution: {profile_name}")
    return Path(_DEFAULT_MAIN_ENTRYPOINTS[profile_name])


def check_dependencies(profile_name: str = "standard", platform: Optional[str] = None) -> bool:
    """Check if required build dependencies are available."""
    print("Checking dependencies...")

    try:
        import PyInstaller

        print(f"✓ PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        return False

    # Check if launch script exists
    main_script = resolve_entrypoint(profile_name=profile_name)
    if not main_script.exists():
        print(f"❌ Main script not found: {main_script}")
        return False
    print(f"✓ Main script found: {main_script}")

    # Check selected/default spec exists
    default_spec = resolve_spec_file(profile_name, platform)
    if default_spec.exists():
        print(f"✓ Spec found: {default_spec}")
    else:
        print(f"⚠️  Recommended spec not found: {default_spec} (using fallback mode)")

    return True


def clean_build_dirs() -> None:
    """Clean previous build directories."""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)

    # Clean Python cache files
    protected_env_dirs = {".venv", "venv", ".git", "node_modules"}
    for cache_dir in Path(".").rglob("__pycache__"):
        if protected_env_dirs.intersection(cache_dir.parts):
            continue
        print(f"Cleaning cache: {cache_dir}")
        shutil.rmtree(cache_dir)


def build_application(
    one_file: bool = False,
    debug: bool = False,
    windowed: bool = True,
    clean: bool = True,
    spec_file: Optional[str] = None,
    profile: str = "standard",
    platform: Optional[str] = None,
) -> int:
    """Build the application using PyInstaller."""

    if clean:
        clean_build_dirs()

    # Prepare PyInstaller command
    # Build with the interpreter running this script. Calling a bare
    # `python` can silently switch to a stale system or legacy virtualenv.
    cmd = [sys.executable, "-m", "PyInstaller"]

    # Use spec file if provided, otherwise select standard spec by platform and profile
    if spec_file and Path(spec_file).exists():
        cmd.append(spec_file)
    else:
        selected_spec = resolve_spec_file(profile, platform)
        if selected_spec.exists():
            cmd.append(str(selected_spec))
        else:
            # Build without spec file
            default_entry = resolve_entrypoint(profile)
            cmd.extend(
                [
                    str(default_entry),
                    "--name",
                    "SignKit",
                    "--add-data",
                    ".env.example:.",
                    "--add-data",
                    "docs:docs",
                    "--add-data",
                    "backend:backend",
                ]
            )

            if one_file:
                cmd.append("--onefile")
            else:
                cmd.append("--onedir")

            if debug:
                cmd.append("--debug")
                cmd.append("--log-level")
                cmd.append("DEBUG")

            if windowed:
                cmd.append("--windowed")  # --noconsole
            else:
                cmd.append("--console")

    # Additional options
    if not debug:
        cmd.append("--clean")

    print(f"Building application with command: {' '.join(cmd)}")

    # Run PyInstaller
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("✓ Build completed successfully!")

        # Show output directory
        dist_dir = Path("dist")
        if dist_dir.exists():
            print(f"Output directory: {dist_dir.absolute()}")

            # List built files
            for item in dist_dir.iterdir():
                if item.is_file():
                    size_mb = item.stat().st_size / (1024 * 1024)
                    print(f"  - {item.name} ({size_mb:.1f} MB)")
                elif item.is_dir():
                    print(f"  - {item.name}/ (directory)")
    else:
        print("❌ Build failed!")

    return result.returncode


def create_installer_scripts() -> None:
    """Create platform-specific installer scripts."""
    print("Creating installer scripts...")

    # macOS script
    macos_script = """#!/bin/bash
# macOS Installation Script for SignKit

set -e

APP_NAME="SignKit"
APP_DIR="/Applications/$APP_NAME.app"

echo "Installing SignKit..."

# Check if app is running
if pgrep -f "$APP_NAME" > /dev/null; then
    echo "Please quit SignKit before installing."
    exit 1
fi

# Remove existing installation
if [ -d "$APP_DIR" ]; then
    echo "Removing existing installation..."
    sudo rm -rf "$APP_DIR"
fi

# Create Applications directory if needed
if [ ! -d "/Applications" ]; then
    echo "Creating Applications directory..."
    sudo mkdir -p "/Applications"
fi

# Copy application
echo "Copying application to /Applications..."
sudo cp -R "dist/$APP_NAME.app" "/Applications/"

# Set permissions
sudo chown -R root:admin "$APP_DIR"
sudo chmod -R 755 "$APP_DIR"

echo "Installation complete!"
echo "You can now launch SignKit from your Applications folder."
"""

    with open("install_macos.sh", "w") as f:
        f.write(macos_script)
    os.chmod("install_macos.sh", 0o755)
    print("✓ Created install_macos.sh")

    # Windows script
    windows_script = """@echo off
REM Windows Installation Script for SignKit

set APP_NAME=SignKit
set INSTALL_DIR=%ProgramFiles%\\%APP_NAME%

echo Installing SignKit...

REM Check if app is running
tasklist /FI "IMAGENAME eq %APP_NAME%.exe" 2>NUL | find /I "%APP_NAME%.exe" >NUL
if %ERRORLEVEL% == 0 (
    echo Please quit SignKit before installing.
    pause
    exit /b 1
)

REM Create installation directory
if not exist "%INSTALL_DIR%" (
    echo Creating installation directory...
    mkdir "%INSTALL_DIR%"
)

REM Copy application files
echo Copying application files...
xcopy "dist\\%APP_NAME%\\*" "%INSTALL_DIR%\\" /E /Y

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\\Desktop\\SignKit.lnk');$s.TargetPath='%INSTALL_DIR%\\%APP_NAME%.exe';$s.Save()"

REM Create Start Menu shortcut
echo Creating Start Menu shortcut...
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\SignKit.lnk');$s.TargetPath='%INSTALL_DIR%\\%APP_NAME%.exe';$s.Save()"

echo Installation complete!
echo You can now launch SignKit from your desktop or Start Menu.
pause
"""

    with open("install_windows.bat", "w") as f:
        f.write(windows_script)
    print("✓ Created install_windows.bat")


def describe_build_targets() -> str:
    """Return a compact profile/platform description."""

    return ", ".join(
        sorted(
            f"{profile}:{platform}->{spec}"
            for profile, spec_by_platform in {
                "standard": STANDARD_PROFILE_SPEC_BY_PLATFORM,
                "mac-premium": PREMIUM_PROFILE_SPEC_BY_PLATFORM,
            }.items()
            for platform, spec in spec_by_platform.items()
        )
    )


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build SignKit application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                    # Build with default settings (one-dir, windowed)
  python build.py --one-file         # Build as single executable
  python build.py --debug            # Build with debug information
  python build.py --console          # Build with console window
  python build.py --clean-only       # Only clean build directories
  python build.py --create-scripts   # Create installer scripts
        """,
    )

    parser.add_argument("--one-file", action="store_true", help="Build as single executable file")
    parser.add_argument("--debug", action="store_true", help="Build with debug information")
    parser.add_argument("--console", action="store_true", help="Build with console window (no GUI)")
    parser.add_argument(
        "--clean",
        action="store_true",
        default=True,
        help="Clean build directories before building",
    )
    parser.add_argument("--no-clean", dest="clean", action="store_false", help="Don't clean build directories before building")
    parser.add_argument("--clean-only", action="store_true", help="Only clean build directories, don't build")
    parser.add_argument(
        "--spec",
        type=str,
        default="",
        help="Use a specific spec file (overrides profile/platform defaults)",
    )
    parser.add_argument(
        "--profile",
        choices=["standard", "mac-premium"],
        default="standard",
        help="Select launch profile: standard (all platforms) or mac-premium (mac only)",
    )
    parser.add_argument("--build-platform", choices=["darwin", "linux", "win32", "win64"], default=None, help="Override platform for defaults")
    parser.add_argument("--create-scripts", action="store_true", help="Create installer scripts")
    parser.add_argument("--no-deps-check", action="store_true", help="Skip dependency checking")
    parser.add_argument("--show-targets", action="store_true", help="Show supported profile/platform mapping and exit")

    args = parser.parse_args()

    print("SignKit Build Script")
    print("=" * 40)

    if args.show_targets:
        print("Target map:", describe_build_targets())
        print("Known profiles: standard, mac-premium")
        return

    resolved_platform = args.build_platform or detect_platform_for_build()
    if args.profile == "mac-premium" and resolved_platform != "darwin":
        print("❌ --profile mac-premium is only supported on Darwin targets.")
        sys.exit(1)

    # Check dependencies
    if not args.no_deps_check:
        if not check_dependencies(profile_name=args.profile, platform=resolved_platform):
            sys.exit(1)

    # Handle clean-only
    if args.clean_only:
        clean_build_dirs()
        print("✓ Build directories cleaned.")
        return

    # Create installer scripts if requested
    if args.create_scripts:
        create_installer_scripts()

    # Build application
    if not args.create_scripts or args.clean_only:
        return_code = build_application(
            one_file=args.one_file,
            debug=args.debug,
            windowed=not args.console,
            clean=args.clean,
            spec_file=args.spec,
            profile=args.profile,
            platform=resolved_platform,
        )

        if return_code != 0:
            print("Build failed with exit code:", return_code)
            sys.exit(return_code)


if __name__ == "__main__":
    main()
