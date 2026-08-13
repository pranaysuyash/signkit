"""Run the isolated Webwright visual evidence suite for the customer-facing concept."""

import subprocess
from pathlib import Path

RUN_DIR = Path(__file__).parent
NODE = "/Users/pranay/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
subprocess.run([NODE, str(RUN_DIR / "final_script.mjs")], check=True)
