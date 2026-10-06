"""Shared pytest fixtures. Owner: Engineering."""
import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
FIXTURE_DIR = REPO / "tests" / "fixtures" / "mini_scifact"


@pytest.fixture(scope="session")
def fixture_dir() -> Path:
    """A tiny, SYNTHETIC SciFact-format dataset used only for unit tests (never for reported metrics)."""
    return FIXTURE_DIR


@pytest.fixture(autouse=True)
def _no_citecheck_env(monkeypatch):
    """Tests must not depend on the developer's shell.  A CITECHECK_* variable left set (e.g. CITECHECK_LOG_ENABLED=0
    from a user-test session, or CITECHECK_TAU) made five app/workflow tests fail (Oct 4 full test).  Tests that need
    one set it themselves with monkeypatch.setenv."""
    for k in [k for k in os.environ if k.startswith("CITECHECK_")]:
        monkeypatch.delenv(k, raising=False)
