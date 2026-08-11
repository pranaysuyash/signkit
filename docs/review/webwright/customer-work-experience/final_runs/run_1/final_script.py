"""Create a repeatable visual evidence run for the customer-facing SignKit concept.

Args:
    None. The local review URL is intentionally fixed to the current parallel concept.
"""

import os
import subprocess
from pathlib import Path

RUN_DIR = Path(__file__).parent
NODE = "/Users/pranay/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
NODE_MODULES = "/Users/pranay/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"

environment = os.environ.copy()
environment["NODE_PATH"] = NODE_MODULES
subprocess.run([NODE, str(RUN_DIR / "final_script.mjs")], check=True, env=environment)
