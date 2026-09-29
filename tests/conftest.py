"""Shared pytest fixtures. Owner: Engineering."""
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
FIXTURE_DIR = REPO / "tests" / "fixtures" / "mini_scifact"


@pytest.fixture(scope="session")
def fixture_dir() -> Path:
    """A tiny, SYNTHETIC SciFact-format dataset used only for unit tests (never for reported metrics)."""
    return FIXTURE_DIR
