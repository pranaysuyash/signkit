from pathlib import Path

from tools.validate_test_data_environment import _pytest_launcher_errors


def test_pytest_launcher_diagnostic_detects_mismatched_shebang(tmp_path: Path):
    repo_root = tmp_path / "repo"
    launcher = repo_root / "venv" / "bin" / "pytest"
    launcher.parent.mkdir(parents=True)
    launcher.write_text("#!/other/python\n", encoding="utf-8")

    errors = _pytest_launcher_errors(repo_root / "venv" / "bin" / "python", repo_root)

    assert len(errors) == 1
    assert "points to" in errors[0]
    assert "run" in errors[0]


def test_pytest_launcher_diagnostic_accepts_matching_shebang(tmp_path: Path):
    repo_root = tmp_path / "repo"
    selected = repo_root / "venv" / "bin" / "python"
    launcher = repo_root / "venv" / "bin" / "pytest"
    launcher.parent.mkdir(parents=True)
    launcher.write_text(f"#!{selected}\n", encoding="utf-8")

    assert _pytest_launcher_errors(selected, repo_root) == []
