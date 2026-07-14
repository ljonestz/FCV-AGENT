"""Tests for Stage 1 preprocessing diagnostics."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app


def test_stage1_payload_summary_counts_roles_and_content_size():
    documents = [
        {"docRole": "primary", "content": "abc"},
        {"docRole": "package", "content": "12345"},
        {"docRole": "context", "content": "zz"},
        {"isContext": True, "content": "long"},
        {"content": "fallback-primary"},
    ]

    summary = app._stage1_payload_summary(documents)

    assert summary == {
        "docs": 5,
        "primary": 2,
        "package": 1,
        "context": 2,
        "content_chars": 30,
    }
