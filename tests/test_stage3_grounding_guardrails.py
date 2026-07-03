"""Stage 3 grounding guardrails (OPCS follow-up, MAI Sahel + false-precision reviews).

Two prompt-level guardrails added in response to MAI feedback:
  - Issue C: fabricated paragraph-level policy citations (Nepal "para 13/17",
    ASCENT "ESS4 24-27", Morocco "para 9(f)"). Guardrail forbids inventing
    paragraph/sub-paragraph handles not present in the provided guidance.
  - Issue G (Sahel P173830): the note recommended *creating* a SEA/SH Action
    Plan and Third-Party Monitoring that already existed on the record.
    Guardrail requires reconciling against evidenced controls before flagging
    them absent.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_stage3_has_policy_citation_guardrail():
    import app

    prompt = app.DEFAULT_PROMPTS["3"]
    assert "POLICY CITATION GUARDRAIL" in prompt
    # Names the failure mode explicitly.
    assert "para 9(f)" in prompt
    assert "does real reputational damage" in prompt


def test_stage3_has_existing_control_reconciliation_guardrail():
    import app

    prompt = app.DEFAULT_PROMPTS["3"]
    assert "EXISTING-CONTROL RECONCILIATION" in prompt
    # Must steer create -> strengthen/verify when the control already exists.
    assert "strengthen / extend / verify-coverage" in prompt
    assert "Third-Party Monitoring already deployed" in prompt
