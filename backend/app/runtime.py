"""Runtime capabilities that define which server-side product boundary is active."""

from __future__ import annotations

import os


LOCAL_COMPANION_PROFILE = "local_companion"
HOSTED_PROFILE = "hosted"


def runtime_profile() -> str:
    """Return the explicit server capability profile."""

    profile = os.getenv("SIGNKIT_RUNTIME_PROFILE", LOCAL_COMPANION_PROFILE).strip().lower()
    if profile not in {LOCAL_COMPANION_PROFILE, HOSTED_PROFILE}:
        raise RuntimeError(
            "SIGNKIT_RUNTIME_PROFILE must be 'local_companion' or 'hosted'."
        )
    return profile


def is_local_companion() -> bool:
    return runtime_profile() == LOCAL_COMPANION_PROFILE
