"""Unit tests for Zone 2 character-limit constants."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import STAGE1_MAX_DOC_CHARS, STAGE1_PACKAGE_DOC_CHARS, STAGE1_CONTEXT_DOC_CHARS

def test_char_limit_constants():
    assert STAGE1_MAX_DOC_CHARS == 60_000
    assert STAGE1_PACKAGE_DOC_CHARS == 25_000
    assert STAGE1_CONTEXT_DOC_CHARS == 30_000
    # Package limit must be strictly less than primary limit
    assert STAGE1_PACKAGE_DOC_CHARS < STAGE1_MAX_DOC_CHARS
