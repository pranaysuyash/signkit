import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).parents[1]
TOOL = ROOT / "tools" / "run_local_product_stack.py"
SERVE = ROOT / "serve.py"
README = ROOT / "tools" / "README.md"


def test_local_product_stack_reuses_canonical_services_and_isolates_default_data() -> None:
    source = TOOL.read_text(encoding="utf-8")
    serve = SERVE.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")

    assert '"backend.app.main:app"' in source
    assert '"serve.py"' in source
    assert "local-product-stack.db" in source
    assert "local-product-stack-data" in source
    assert 'environment["DATABASE_URL"] = _database_url(args)' in source
    assert 'environment["SIGNKIT_DATA_DIR"] = str(_data_dir(args))' in source
    assert "--data-dir" in source
    assert "/health" in source
    assert '"/workspace-app/"' in source or "/workspace-app/" in source
    assert "SIGNKIT_LANDING_PORT" in serve
    assert "run_local_product_stack.py" in readme


def test_backend_data_root_is_configurable_without_changing_the_default() -> None:
    source = (ROOT / "backend" / "app" / "paths.py").read_text(encoding="utf-8")

    assert 'os.environ.get("SIGNKIT_DATA_DIR")' in source
    assert 'Path(configured_base).expanduser().resolve()' in source
    assert 'Path.home() / "Library" / "Application Support" / app_name' in source


def test_backend_uses_explicit_data_root_in_a_fresh_process(tmp_path: Path) -> None:
    data_root = (tmp_path / "signkit-data").resolve()
    environment = os.environ.copy()
    environment["SIGNKIT_DATA_DIR"] = str(data_root)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from backend.app.paths import USER_DATA_DIR; print(USER_DATA_DIR)",
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(data_root)
