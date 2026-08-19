"""Deployment dependency contracts for the Render web service."""

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_packaging_is_an_explicit_runtime_dependency() -> None:
    requirements = (
        REPO_ROOT / "requirements.txt"
    ).read_text(encoding="utf-8").splitlines()
    declared = {
        line.partition("#")[0].strip().lower()
        for line in requirements
        if line.partition("#")[0].strip()
    }

    assert any(
        re.fullmatch(r"packaging(?:\[.*\])?(?:[<>=!~].*)?", requirement)
        for requirement in declared
    ), "requirements.txt must declare packaging for Gunicorn's gevent worker"
