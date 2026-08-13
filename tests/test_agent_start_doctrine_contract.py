"""Static guard for the shared agent-start doctrine source-selection contract."""

from pathlib import Path

import pytest


AGENT_START = Path("/Users/pranay/Projects/agent-start")


def test_agent_start_preserves_project_local_motto_and_separates_workspace_doctrine() -> None:
    if not AGENT_START.exists():
        pytest.skip("shared agent-start wrapper is not available in this environment")

    source = AGENT_START.read_text(encoding="utf-8")

    assert 'if [[ -f "$PROJECT_DIR/motto_v5.md" ]]' in source
    assert 'DOCTRINE_SOURCE="$DOCTRINE_FILE"' in source
    assert 'DOCTRINE_VERSION="5"' in source
    assert 'ensure_motto_v5_alias()' in source
    assert 'Refusing to overwrite it. Expected a symlink to $motto_source.' in source
    assert 'retained project-local motto_v5.md; workspace Doctrine 6.0 remains separate' in source

    # The project-specific motto must not be in the destructive legacy list.
    legacy_block = source.split("LEGACY_DOCTRINE_FILES=(", 1)[1].split(")", 1)[0]
    assert '"$PROJECT_DIR/motto_v5.md"' not in legacy_block
