"""AF financed-component scope (OPCS follow-up, MAI Mali AF P173830 review).

MAI finding: the AF note drew recommendations from the full parent-project
narrative (crisis-response / displacement themes) when the $50M AF actually
financed only a subset of components. The tool should extract and state which
parent-project components the AF finances vs which remain unchanged, and scope
recommendations accordingly.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_af_guide_has_financed_scope_check():
    import background_docs as bd

    assert "Financed-scope check (AF)" in bd.AF_GUIDE
    # Must steer against pulling recommendations from unfinanced components.
    assert "do not draw recommendations indiscriminately" in bd.AF_GUIDE
    # Must flag cross-document scope/geography inconsistency rather than guessing.
    assert "flag the inconsistency" in bd.AF_GUIDE


def test_stage1_prompt_requires_af_financed_component_statement():
    import app

    prompt = app.DEFAULT_PROMPTS["1"]
    assert "which of the parent project's components the additional financing finances" in prompt
    assert "does not specify which components the additional financing finances" in prompt
