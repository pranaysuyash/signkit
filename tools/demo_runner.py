"""Qt-based demo runner that executes flows from YAML and records the screen.

Example:
    python tools/demo_runner.py --flow flows/sample_place_sign_export.yaml --output demos/sample.mp4

Notes:
  - Ensure PySide6 and PyYAML are installed.
  - Assign objectName to widgets you intend to target via 'click'.
  - You can call methods on MainWindow using 'invoke'.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Dict

import yaml

try:
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QWidget
except Exception as exc:  # pragma: no cover
    print("PySide6 is required to run the demo runner:", exc, file=sys.stderr)
    sys.exit(2)

# App imports
try:
    from desktop_app.views.main_window import MainWindow
    from desktop_app.state.session import SessionState
except Exception as exc:  # pragma: no cover
    print("Failed to import MainWindow:", exc, file=sys.stderr)
    sys.exit(2)

from tools.record import start_recording, stop_recording


def _click(window: MainWindow, target: str, button: str = "left") -> None:
    widget: QWidget | None = window.findChild(QWidget, target)
    if widget is None:
        raise RuntimeError(f"click target not found: {target}")
    button_map = {
        "left": Qt.LeftButton,
        "right": Qt.RightButton,
        "middle": Qt.MiddleButton,
    }
    btn = button_map.get(button.lower(), Qt.LeftButton)
    QTest.mouseClick(widget, btn)


def _type(text: str) -> None:
    QTest.keyClicks(QApplication.focusWidget(), text)


def _wait(ms: int) -> None:
    QTest.qWait(ms)


def _invoke(window: MainWindow, method: str, args: list[Any] | None = None) -> None:
    fn = getattr(window, method, None)
    if not callable(fn):
        raise RuntimeError(f"invoke target not callable: {method}")
    (fn)(*(args or []))


class _DummyApiClient:
    def upload_image(self, path: str) -> dict:
        return {"id": "demo-session"}

    def process_image(self, **kwargs):  # pragma: no cover
        return {}


def run_flow(flow_path: Path, output_video: Path) -> None:
    with flow_path.open("r", encoding="utf-8") as f:
        flow: Dict[str, Any] = yaml.safe_load(f)

    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow(_DummyApiClient(), SessionState())
    window.show()
    QTest.qWaitForWindowExposed(window)

    proc = start_recording(str(output_video))
    try:
        for step in flow.get("steps", []):
            if isinstance(step, int):
                _wait(step)
                continue
            if "wait" in step:
                _wait(int(step["wait"]))
            elif "click" in step:
                if isinstance(step["click"], str):
                    _click(window, step["click"])  # default left click
                else:
                    _click(window, step["click"]["target"], step["click"].get("button", "left"))
            elif "type" in step:
                _type(str(step["type"]))
            elif "invoke" in step:
                inv = step["invoke"]
                _invoke(window, inv["method"], inv.get("args"))
            else:
                raise RuntimeError(f"Unknown step: {step}")
    finally:
        stop_recording(proc)
        window.close()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run a UI flow and record a demo video.")
    p.add_argument("--flow", required=True, help="Path to YAML flow file")
    p.add_argument("--output", required=True, help="Path to output MP4 video")
    args = p.parse_args(argv)

    flow_path = Path(args.flow)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    run_flow(flow_path, out)
    print(f"Saved demo video to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
