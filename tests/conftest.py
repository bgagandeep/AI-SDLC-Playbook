import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    """Run each test in an isolated cwd so scripts never touch the real repo."""
    monkeypatch.chdir(tmp_path)
    return tmp_path
