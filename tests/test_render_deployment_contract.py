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


def test_httpx_is_an_explicit_runtime_dependency() -> None:
    requirements = (
        REPO_ROOT / "requirements.txt"
    ).read_text(encoding="utf-8").splitlines()
    declared = {
        line.partition("#")[0].strip().lower()
        for line in requirements
        if line.partition("#")[0].strip()
    }

    assert any(
        re.fullmatch(r"httpx(?:\[.*\])?(?:[<>=!~].*)?", requirement)
        for requirement in declared
    ), (
        "requirements.txt must declare httpx because app.py imports it directly"
    )


def test_anthropic_sdk_excludes_incompatible_one_major() -> None:
    requirements = (
        REPO_ROOT / "requirements.txt"
    ).read_text(encoding="utf-8").splitlines()
    declared = {
        line.partition("#")[0].strip().lower()
        for line in requirements
        if line.partition("#")[0].strip()
    }

    assert "anthropic>=0.40.0,<1.0.0" in declared, (
        "requirements.txt must retain the Render-verified Anthropic 0.x client"
    )
