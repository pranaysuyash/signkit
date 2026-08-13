# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Intel macOS.
For building on Intel Macs or cross-compiling.
"""

import sys
import os
from pathlib import Path

# Get the project root directory
PROJ_DIR = Path(SPECPATH).parent
SRC_DIR = PROJ_DIR

# Main application entry point
MAIN_SCRIPT = SRC_DIR / "desktop_app" / "main.py"

# Prepare datas list (filter out None entries)
datas_list = [
    (str(SRC_DIR / "backend" / ".env"), "backend") if (SRC_DIR / "backend" / ".env").exists() else None,
    (str(SRC_DIR / "legal"), "legal") if (SRC_DIR / "legal").exists() else None,
    (str(SRC_DIR / "desktop_app" / "resources"), "desktop_app/resources") if (SRC_DIR / "desktop_app" / "resources").exists() else None,
    (str(SRC_DIR / "desktop_app/resources/signature_template_synthetic_512.jpg"), "desktop_app/resources") if (SRC_DIR / "desktop_app/resources/signature_template_synthetic_512.jpg").exists() else None,
    
    # Include app assets (icons)
    (str(SRC_DIR / "assets" / "files"), "assets/files") if (SRC_DIR / "assets" / "files").exists() else None,
    
    (str(SRC_DIR / "backend" / "app"), "backend/app"),
    (str(SRC_DIR / "backend" / "alembic.ini"), "backend") if (SRC_DIR / "backend" / "alembic.ini").exists() else None,
]
# Filter out None entries
datas_list = [d for d in datas_list if d is not None]

# Analysis configuration (same as ARM64 version)
a = Analysis(
    [str(MAIN_SCRIPT)],
    pathex=[str(SRC_DIR)],
    binaries=[],
    datas=datas_list,
    hiddenimports=[
        "PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets", "PySide6.QtPrintSupport",
        "shiboken6", "cv2", "numpy", "PIL", "PIL.Image", "PIL.ImageQt", "PIL.ImageDraw",
        "PIL.ImageFont", "PIL.ExifTags", "uvicorn", "uvicorn.logging", "uvicorn.loops",
        "uvicorn.loops.auto", "uvicorn.protocols", "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto", "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto", "uvicorn.lifespan", "uvicorn.lifespan.on",
        "fastapi", "fastapi.responses", "starlette", "starlette.middleware",
        "starlette.middleware.cors", "sqlalchemy", "sqlalchemy.ext.declarative",
        "pydantic", "pydantic_settings", "passlib", "passlib.context",
        # Uvicorn HTTP dependencies
        "h11", "anyio", "sniffio", "click",
        "python_multipart", "jose", "psycopg2", "pypdfium2", "pikepdf",
        "queue", "threading", "asyncio", "json", "base64", "hashlib", "datetime",
        "pathlib", "subprocess", "socket", "tempfile", "shutil", "gc", "uuid",
        "secrets", "hmac", "time", "logging", "urllib.parse", "email.utils", "io", "atexit",
        "desktop_app", "desktop_app.config", "desktop_app.state", "desktop_app.state.session",
        "desktop_app.api", "desktop_app.api.client", "desktop_app.backend_manager",
        "desktop_app.views", "desktop_app.views.main_window",
        "desktop_app.views.main_window_parts", "desktop_app.views.main_window_parts.extraction",
        "desktop_app.views.main_window_parts.pdf", "desktop_app.views.login_dialog",
        "desktop_app.views.license_dialog", "desktop_app.views.license_restriction_dialog",
        "desktop_app.widgets", "desktop_app.widgets.image_view",
        "desktop_app.widgets.modern_mac_button", "desktop_app.processing",
        "desktop_app.processing.extractor", "desktop_app.license",
        "desktop_app.license.storage", "desktop_app.license.validator",
        "desktop_app.license.restrictions", "desktop_app.pdf", "desktop_app.pdf.signer",
        "backend.app.main", "backend.app.config", "backend.app.database",
        "backend.app.routers", "backend.app.routers.auth", "backend.app.routers.extraction",
        "backend.app.models", "backend.app.models.user", "backend.app.crud", "backend.app.utils",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "pandas", "notebook", "jupyter", "IPython", "test", "tests", "pytest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SignKit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch='x86_64',  # Intel architecture
    codesign_identity=None,
    entitlements_file=None,
)

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

app = BUNDLE(
    coll,
    name='SignKit.app',
    icon=str(SRC_DIR / "assets" / "files" / "SignKit.icns") if (SRC_DIR / "assets" / "files" / "SignKit.icns").exists() else None,
    bundle_identifier='work.signkit.app',
    version='1.0.0',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleName': 'SignKit',
        'CFBundleDisplayName': 'SignKit',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025. All rights reserved.',
        'LSMinimumSystemVersion': '10.13.0',
        'NSRequiresAquaSystemAppearance': False,
        'LSApplicationCategoryType': 'public.app-category.productivity',
        'CFBundleDocumentTypes': [
            {'CFBundleTypeName': 'Image', 'CFBundleTypeRole': 'Viewer', 'LSItemContentTypes': ['public.image']},
            {'CFBundleTypeName': 'PDF', 'CFBundleTypeRole': 'Editor', 'LSItemContentTypes': ['com.adobe.pdf']}
        ],
    },
)
