"""2026-11-27 (owner): the Word report no longer shows the S/R focus tag, the FCV Strategy shift or the
authority basis. The fields stay in the Stage 3 JSON (ITS parity surface)."""
from io import BytesIO

from docx import Document

import app
from tests.test_fcv_priority_advisory_exports import _docx_text


def test_word_report_hides_legacy_priority_labels():
    priority = {"title": "Priority 1 · Clarify siting", "tag": "[S+R]", "risk_level": "High",
                "fcv_dimension": "Inclusion", "refresh_shift": "Shift A: Anticipate",
                "authority_basis": "reviewer_judgment", "implementation_note": "Phase the works.",
                "the_gap": "Gap.", "why_it_matters": "Why.",
                "actions": [{"document_element": "PAD", "guidance": "Do it.", "suggested_language": "Text."}]}
    resp = app.app.test_client().post("/api/download-report",
                                      json={"summary": "", "priorities": [priority], "metadata": {}})
    assert resp.status_code == 200
    text = _docx_text(Document(BytesIO(resp.data)))
    assert "Inclusion" in text and "Phase the works." in text
    for gone in ("Sensitivity + Responsiveness", "FCV Focus", "FCV Strategy 2026-2030", "Shift A: Anticipate",
                 "Authority basis", "reviewer judgment"):
        assert gone not in text, gone
