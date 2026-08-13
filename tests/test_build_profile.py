"""Tests for build script profile defaults."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType


def load_build_script() -> ModuleType:
    """Load build-tools/build.py as a module without requiring package import."""

    script_path = Path(__file__).resolve().parents[1] / "build-tools" / "build.py"
    module_spec = spec_from_file_location("build_script", script_path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError("Could not load build-tools/build.py")

    module = module_from_spec(module_spec)
    module_spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def test_resolve_entrypoint_for_profiles():
    build_script = load_build_script()
    standard = build_script.resolve_entrypoint("standard")
    premium = build_script.resolve_entrypoint("mac-premium")

    assert standard == Path("desktop_app/main.py")
    assert premium == Path("desktop_app/main_macos_premium.py")


def test_resolve_spec_prefers_profile_by_platform():
    build_script = load_build_script()
    assert build_script.resolve_spec_file("standard", "darwin") == Path("build-tools/SignatureExtractor_macOS.spec")
    assert build_script.resolve_spec_file("mac-premium", "darwin") == Path(
        "build-tools/SignatureExtractor_macOS_Premium.spec"
    )


def test_resolve_spec_rejects_macos_premium_on_non_mac_platform():
    build_script = load_build_script()

    try:
        build_script.resolve_spec_file("mac-premium", "linux")
    except ValueError as exc:
        assert "only supported on darwin" in str(exc)
    else:
        raise AssertionError("Expected mac-premium on non-darwin to be rejected")


def test_resolve_entrypoint_unknown_profile_is_rejected():
    build_script = load_build_script()

    try:
        build_script.resolve_entrypoint("enterprise")
    except ValueError as exc:
        assert "Unknown launch profile" in str(exc)
    else:
        raise AssertionError("Expected unknown profile to fail for entrypoint resolution")


def test_release_specs_never_bundle_developer_environment_files():
    """Release specs must not copy local credentials into packaged apps."""

    root = Path(__file__).resolve().parents[1]
    specs = sorted((root / "build-tools").glob("SignatureExtractor_*.spec"))

    assert specs
    for spec in specs:
        source = spec.read_text(encoding="utf-8")
        assert '"backend" / ".env"' not in source
        assert "backend/.env" not in source
        assert '"web" / "cloud_workspace"' in source
