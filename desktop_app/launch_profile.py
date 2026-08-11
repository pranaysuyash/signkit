from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LaunchProfile:
    """Metadata used by app launch/bootstrap paths."""

    profile_name: str
    organization_name: str
    organization_domain: str
    application_name: str
    application_display_name: str
    qt_mac_application_name: str
    desktop_file_name: str
    min_window_size: tuple[int, int]
    initial_window_size: tuple[int, int]
    icon_preference: tuple[str, ...]
    premium_ui: bool = False
    default_plan_id: str = "starter"
    window_title: str | None = None

    def resolve_title(self) -> str:
        """Return the resolved window title for this launch profile."""

        return self.window_title or self.application_display_name


STANDARD_PROFILE = LaunchProfile(
    profile_name="standard",
    organization_name="SignKit",
    organization_domain="signkit.work",
    application_name="SignKit",
    application_display_name="SignKit",
    qt_mac_application_name="SignKit",
    desktop_file_name="SignKit",
    min_window_size=(1000, 700),
    initial_window_size=(1200, 800),
    icon_preference=(
        "assets/files/signkit_icon_1024x1024.png",
        "assets/files/signkit_icon_512x512.png",
        "assets/files/signkit_icon_256x256.png",
        "assets/files/signkit_icon_128x128.png",
    ),
)

PREMIUM_MAC_PROFILE = LaunchProfile(
    profile_name="mac-premium",
    organization_name="SignKit",
    organization_domain="signkit.work",
    application_name="SignKit Premium",
    application_display_name="SignKit Premium",
    qt_mac_application_name="SignKit Premium",
    desktop_file_name="SignKitPremium",
    min_window_size=(1200, 800),
    initial_window_size=(1440, 920),
    icon_preference=(
        "assets/files/signkit_icon_1024x1024.png",
        "assets/files/signkit_icon_512x512.png",
        "assets/files/signkit_icon_256x256.png",
        "assets/files/signkit_icon_128x128.png",
    ),
    premium_ui=True,
    default_plan_id="team",
    window_title="SignKit Premium",
)

_PROFILES = {
    STANDARD_PROFILE.profile_name: STANDARD_PROFILE,
    PREMIUM_MAC_PROFILE.profile_name: PREMIUM_MAC_PROFILE,
}


def get_profile(profile_name: str | None = None) -> LaunchProfile:
    """Resolve a launch profile by name, defaulting to the standard profile."""

    name = profile_name or "standard"
    if name not in _PROFILES:
        raise ValueError(f"Unknown launch profile: {name}")

    return _PROFILES[name]
