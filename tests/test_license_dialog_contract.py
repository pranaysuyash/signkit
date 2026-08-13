"""Source contract for the user-facing local activation boundary."""

from pathlib import Path


SOURCE = Path(__file__).parents[1] / "desktop_app" / "views" / "license_dialog.py"


def test_license_dialog_uses_signed_receipt_activation() -> None:
    source = SOURCE.read_text(encoding="utf-8")

    assert "EntitlementReceipt.from_dict" in source
    assert "activate_receipt(receipt)" in source
    assert "Activation not verified" in source
    assert "save_license" not in source
