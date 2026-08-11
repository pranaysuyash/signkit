"""Profile-aware entrypoint and command-line helpers for SignKit launches."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from desktop_app.app_bootstrap import run as run_with_profile
from desktop_app.launch_profile import LaunchProfile, get_profile


KNOWN_PROFILES = ("standard", "mac-premium")
PLATFORM_MACOS = "darwin"
_PLATFORM_NAME = sys.platform


def _default_profile(platform_name: str) -> str:
    """Return the default launch profile for a given platform."""

    return "mac-premium" if platform_name == PLATFORM_MACOS else "standard"


def _resolve_profile_name(
    requested_profile: Optional[str],
    *,
    platform_name: Optional[str] = None,
) -> str:
    """Resolve the final profile name from CLI/env/OS defaults.

    Resolution precedence:
    1) explicit CLI profile
    2) SIGNKIT_PROFILE env var
    3) default profile based on platform
    """

    target_platform = platform_name or _PLATFORM_NAME
    requested = (requested_profile or "").strip().lower() if requested_profile else ""
    if requested == "auto" or not requested:
        requested = os.getenv("SIGNKIT_PROFILE", "").strip().lower()

    if not requested:
        requested = _default_profile(target_platform)

    if requested not in KNOWN_PROFILES:
        raise ValueError(f"Unknown launch profile: {requested}")

    if requested == "mac-premium" and target_platform != PLATFORM_MACOS:
        raise ValueError("Profile 'mac-premium' is only supported on macOS")

    return requested


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse CLI arguments for the launcher."""

    parser = argparse.ArgumentParser(description="Launch SignKit with profile-aware entrypoints.")
    parser.add_argument(
        "--profile",
        choices=("auto", "standard", "mac-premium"),
        default="auto",
        help="Launch profile override. auto = env/default platform behavior.",
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="Show supported profiles and exit.",
    )
    parser.add_argument(
        "--premium",
        action="store_true",
        help="Shortcut for --profile mac-premium (macOS only).",
    )

    return parser.parse_args(argv)


def resolve_profile(
    requested_profile: Optional[str],
    *,
    platform_name: Optional[str] = None,
) -> LaunchProfile:
    """Resolve and load a launch profile."""

    resolved_name = _resolve_profile_name(requested_profile, platform_name=platform_name)
    return get_profile(resolved_name)


def run(argv: Optional[list[str]] = None) -> int:
    """Run SignKit with CLI-compatible profile resolution."""

    args = parse_args(argv)

    if args.list_profiles:
        for profile in KNOWN_PROFILES:
            default_note = "(default on non-mac)"
            if profile == "mac-premium":
                default_note = "(default on macOS)"
            print(f"{profile:14} {default_note}")
        return 0

    requested_profile = args.profile
    if args.premium:
        requested_profile = "mac-premium"

    try:
        profile = resolve_profile(requested_profile)
    except ValueError as error:
        print(f"❌ {error}")
        return 1

    return run_with_profile(profile)


def _run_profile(profile_name: str) -> int:
    """Compatibility helper for explicit legacy entrypoints."""

    profile = get_profile(profile_name)
    return run_with_profile(profile)


def main() -> None:
    """CLI entrypoint."""

    sys.exit(run())


if __name__ == "__main__":
    main()
