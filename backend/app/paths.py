"""Shared filesystem paths for backend runtime.

Keep all path decisions (user-writable dirs, uploads, logs) centralized so
routers and the FastAPI app mount use the same locations.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def get_user_data_dir(app_name: str = "SignKit") -> Path:
    """Return a user-writable base directory for app data/logs/uploads."""
    configured_base = os.environ.get("SIGNKIT_DATA_DIR")
    if configured_base:
        base = Path(configured_base).expanduser().resolve()
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / app_name
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", str(Path.home()))) / app_name
    else:
        base = Path.home() / ".local" / "share" / app_name
    base.mkdir(parents=True, exist_ok=True)
    # Restrict the per-user data directory to the owner. Signature images and
    # selection sidecars are local PII; prevent other accounts on a shared
    # machine from reading them.
    if os.name == "posix":
        try:
            os.chmod(base, 0o700)
        except OSError:
            pass
    return base


USER_DATA_DIR: Path = get_user_data_dir()
LOG_DIR: Path = USER_DATA_DIR / "logs"
UPLOADS_DIR: Path = USER_DATA_DIR / "uploads" / "images"
