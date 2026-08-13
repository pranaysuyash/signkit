# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Get the project root directory
PROJ_DIR = Path(SPECPATH).parent
SRC_DIR = PROJ_DIR

# Main application entry point
MAIN_SCRIPT = SRC_DIR / "desktop_app" / "main.py"

# Analysis configuration
a = Analysis(
    [str(MAIN_SCRIPT)],
    pathex=[str(SRC_DIR)],
    binaries=[],
    datas=[
        # Include configuration files
        (str(SRC_DIR / ".env.example"), "."),

        # Include documentation
        (str(SRC_DIR / "docs"), "docs"),

        # Include license dialog assets if they exist
        (str(SRC_DIR / "desktop_app" / "assets"), "desktop_app/assets") if (SRC_DIR / "desktop_app" / "assets").exists() else None,

        # Include backend files (optional component)
        (str(SRC_DIR / "backend"), "backend"),
    ],
    hiddenimports=[
        # PySide6 modules
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtPrintSupport",

        # Image processing libraries
        "cv2",
        "numpy",
        "PIL",
        "PIL.Image",

        # Backend dependencies
        "uvicorn",
        "fastapi",
        "sqlalchemy",
        "pydantic",

        # PDF processing libraries
        "pypdfium2",
        "pikepdf",

        # Standard library modules that might be missed
        "queue",
        "threading",
        "asyncio",
        "json",
        "base64",
        "hashlib",
        "datetime",
        "pathlib",
        "subprocess",
        "socket",
        "tempfile",
        "shutil",
        "gc",
        "uuid",
        "secrets",
        "hmac",
        "time",
        "logging",
        "urllib.parse",
        "email.utils",

        # Desktop app modules
        "desktop_app",
        "desktop_app.config",
        "desktop_app.state.session",
        "desktop_app.api.client",
        "desktop_app.backend_manager",
        "desktop_app.views.main_window",
        "desktop_app.views.login_dialog",
        "desktop_app.views.license_dialog",
        "desktop_app.views.license_restriction_dialog",
        "desktop_app.widgets.modern_mac_button",
        "desktop_app.processing.extractor",
        "desktop_app.license.storage",
        "desktop_app.license.validator",
        "desktop_app.license.entitlements",
        "desktop_app.license.verification",
        "desktop_app.license.activation",

        # Backend modules
        "backend.app.main",
        "backend.app.routers.auth",
        "backend.app.routers.extraction",
        "backend.app.database",
        "backend.app.models",
        "backend.app.crud",
        "backend.app.utils",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        "tkinter",
        "matplotlib",
        "scipy",
        "pandas",
        "notebook",
        "jupyter",
        "IPython",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove None entries from datas
a.datas = [entry for entry in a.datas if entry is not None]

# PYZ configuration
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# EXE configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SignKit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Application metadata
    version="1.0.0",
    description="SignKit - Extract signatures from documents with precision",
    icon=str(SRC_DIR / "assets" / "files" / "signkit_icon.ico") if (SRC_DIR / "assets" / "files" / "signkit_icon.ico").exists() else None,
)

# Optional: Create directory-based distribution for development
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SignKit',
)
