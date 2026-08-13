from pathlib import Path


ROOT = Path(__file__).parents[1]
TOOL = ROOT / "tools" / "run_local_product_browser_proof.mjs"
README = ROOT / "tools" / "README.md"


def test_local_product_browser_proof_is_reusable_and_scope_bound() -> None:
    source = TOOL.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")

    assert 'reducedMotion: "reduce"' in source
    assert 'width: 1440, height: 900' in source
    assert 'width: 390, height: 844' in source
    assert 'width: 320, height: 844' in source
    assert 'ArrowRight' in source
    assert 'skipLink' in source
    assert 'primaryCtaHref' in source
    assert 'stateRail' in source
    assert 'skip link cannot receive focus' in source
    assert 'workspace-app/' in source
    assert 'does not start' in source
    assert "run_local_product_browser_proof.mjs" in readme
