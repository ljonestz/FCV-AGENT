"""Route-level tests for mechanism cards: off by default (no prompt change), end-to-end in Express when on."""
from __future__ import annotations

import json

import pytest

import app
from tests.test_concise_stage3_contract import _decode_sse, _payload, _wrapped

DOC = ("Water Global Practice\n" + "Context. " * 30 +
       "Practice Area (Lead) Contributing Practice Areas Water Climate Change and Disaster Screening Yes. "
       + "Component 2 finances water points in host communities. " * 10)
STAGE1 = """Stage 1 project extraction.
%%%SECTOR_FACTS_START%%%
practice_area_lead: Water
sector_label: water
sector_confidence: high
pdo_names_sector: true
fcv_setting: displacement_hosting
sector_shares: water=0.9
features:
- water_points_wash | share=0.40 | named=true | evidence=true | country=n/a | page=22
%%%SECTOR_FACTS_END%%%"""


def _run_express(monkeypatch, stage2_text: str, priorities_cards=None):
    prompts: dict[int, str] = {}
    payload = _payload()
    if priorities_cards is not None:
        payload["priorities"][0]["sector_cards"] = priorities_cards

    def fake_stream(messages, _max_tokens, stage, **_kwargs):
        prompts[stage] = "\n".join(str(m.get("content")) for m in messages if isinstance(m, dict))
        fake_stream._last_result = STAGE1 if stage == 1 else stage2_text if stage == 2 else _wrapped(payload)
        fake_stream._last_stop_reason = "end_turn"
        yield 'data: {"chunk": "stage"}\n\n'

    def fake_research(*_args, **_kwargs):
        yield {"result": {"core_brief": "Brief.", "climate_research": {}, "lens_context_sources": [],
                          "climate_grounding": {}}}

    monkeypatch.setattr(app, "_stream_stage", fake_stream)
    monkeypatch.setattr(app, "_iter_stage1_research", fake_research)
    monkeypatch.setattr(app, "extract_country_name", lambda *_a: "Exampleland")
    monkeypatch.setattr(app, "extract_sector_name", lambda *_a: "Water")
    monkeypatch.setattr(app, "get_fast_client", lambda: object())
    monkeypatch.setattr(app, "extract_instrument_type", lambda _t: "IPF")
    monkeypatch.setattr(app, "extract_temporal_context", lambda _t: {})
    monkeypatch.setattr(app, "extract_regime_context", lambda _t, _i: {})
    monkeypatch.setattr(app, "extract_country_classification", lambda _t: {"category": "Conflict-Affected"})
    monkeypatch.setattr(app, "extract_lens_evidence", lambda *_a: {})
    response = app.app.test_client().post("/api/run-express", json={
        "active_lenses": [], "review_mode": "design", "document_type": "PAD", "instrument_type": "IPF",
        "documents": [{"name": "PAD.txt", "type": "text", "docRole": "primary", "content": DOC}],
    })
    events = _decode_sse(response)
    return prompts, events


def _stage(events, n):
    return next(e for e in events if e.get("stage_done") == n)


def test_flag_off_leaves_prompts_and_payloads_unchanged(monkeypatch):
    monkeypatch.delenv("SECTOR_CARDS_ENABLED", raising=False)
    prompts, events = _run_express(monkeypatch, "Stage 2 assessment.")
    assert "SECTOR_FACTS" not in prompts[1] and "SECTOR MECHANISM CARDS" not in prompts[2]
    assert "SECTOR CARD FINDINGS" not in prompts[3]
    assert _stage(events, 1)["sector_facts"] is None and _stage(events, 1)["sector_routing"] is None
    assert "sector_provenance" not in _stage(events, 3)


def test_flag_on_express_end_to_end(monkeypatch):
    monkeypatch.setenv("SECTOR_CARDS_ENABLED", "1")
    prompts, events = _run_express(monkeypatch, "placeholder")  # first pass learns the eligible ids
    routing = _stage(events, 1)["sector_routing"]
    assert routing["sectors"] == ["water"] and routing["eligible"]
    assert "%%%SECTOR_FACTS_START%%%" in prompts[1]
    assert "SECTOR MECHANISM CARDS" in prompts[2]
    ids = [e["card_id"] for e in routing["eligible"]]

    stage2 = ("Stage 2 assessment.\n%%%SECTOR_CARDS_START%%%\n" + json.dumps({"cards": [
        {"card_id": ids[0], "finding": "Siting of water points across host and displaced areas could be clarified.",
         "page_ref": "22"},
        {"card_id": ids[1], "finding": "Committee membership rules could be set out.", "page_ref": "23"},
    ]}) + "\n%%%SECTOR_CARDS_END%%%")
    prompts, events = _run_express(monkeypatch, stage2, priorities_cards=[ids[0], "mc-99"])
    assert "SECTOR CARD FINDINGS" in prompts[3] and f"[{ids[0]}]" in prompts[3]
    s2 = _stage(events, 2)
    assert "SECTOR_CARDS" not in (s2.get("display_text") or "") and "SECTOR_CARDS" not in (s2.get("result") or "")
    s3 = _stage(events, 3)
    assert s3["priorities"][0]["sector_cards"] == [ids[0]]
    assert s3["sector_provenance"].startswith("Sector checks: Water (lead Practice Area)")
    assert "Reflected in priority 1." in s3["sector_provenance"]
    assert [a["card_id"] for a in s3["sector_additional"]] == [ids[1]]


def test_flag_on_missing_card_block_is_not_an_error(monkeypatch):
    monkeypatch.setenv("SECTOR_CARDS_ENABLED", "1")
    _prompts, events = _run_express(monkeypatch, "Stage 2 assessment without a card block.")
    s3 = _stage(events, 3)
    assert s3["sector_additional"] == []
    assert "No additional sector considerations" in s3["sector_provenance"]
    assert not s3.get("parse_error")


@pytest.mark.parametrize("value", ["", "0", "false", "off"])
def test_flag_values_that_mean_off(monkeypatch, value):
    monkeypatch.setenv("SECTOR_CARDS_ENABLED", value)
    assert app.sector_cards_enabled(app.AnalysisState(), False) is False


def test_flag_never_applies_to_implementation_reviews_or_climate(monkeypatch):
    monkeypatch.setenv("SECTOR_CARDS_ENABLED", "1")
    assert app.sector_cards_enabled(app.AnalysisState(), True) is False
    assert app.sector_cards_enabled(app.AnalysisState(active_lenses=["climate"]), False) is False
    assert app.sector_cards_enabled(app.AnalysisState(), False) is True


def test_step_by_step_routing_recomputes_from_echoed_facts(monkeypatch):
    from sector_cards.integration import extract_sector_facts
    facts = extract_sector_facts(STAGE1, DOC)
    full = app.sector_routing_for_request({"sector_facts": facts}, "IPF")
    assert full["eligible"]
    off_one = app.sector_routing_for_request(
        {"sector_facts": facts, "sector_cards_off": [full["eligible"][0]["card_id"]]}, "IPF")
    assert len(off_one["eligible"]) == len(full["eligible"]) - 1
    assert app.sector_routing_for_request({"sector_facts": facts, "sector_off": True}, "IPF")["eligible"] == []
    # The browser cannot add cards: an injected eligible list is ignored because routing is recomputed.
    tampered = {**facts, "eligible": [{"card_id": "mc-24"}]}
    assert "mc-24" not in [e["card_id"] for e in app.sector_routing_for_request({"sector_facts": tampered}, "IPF")["eligible"]]


def test_step_by_step_stage2_prompt_gets_card_slice_and_respects_switch_off(monkeypatch):
    from sector_cards.integration import extract_sector_facts
    calls = []

    def fake(messages, _max_tokens, stage, **_kwargs):
        calls.append((stage, "\n".join(str(m.get("content")) for m in messages if isinstance(m, dict))))
        fake._last_result = "Independent Stage 2 findings."
        fake._last_stop_reason = "end_turn"
        yield 'data: {"chunk":"offline"}\n\n'

    monkeypatch.setattr(app, "_stream_stage", fake)
    monkeypatch.setattr(app, "get_fast_client", lambda: object())
    facts = extract_sector_facts(STAGE1, DOC)
    hist = [{"role": "user", "content": "[Stage 1 - project documents analysed]"},
            {"role": "assistant", "content": STAGE1}]

    def run_stage2(**extra):
        calls.clear()
        response = app.app.test_client().post("/api/run-stage", json={
            "stage": 2, "history": hist, "active_lenses": [], "instrument_type": "IPF",
            "document_type": "PAD", "doc_type": "PAD", "sector_facts": facts, **extra})
        assert response.status_code == 200
        response.get_data(as_text=True)
        return next(p for s, p in calls if s == 2)

    monkeypatch.setenv("SECTOR_CARDS_ENABLED", "1")
    assert "SECTOR MECHANISM CARDS" in run_stage2()
    assert "SECTOR MECHANISM CARDS" not in run_stage2(sector_off=True)
    monkeypatch.delenv("SECTOR_CARDS_ENABLED")
    assert "SECTOR MECHANISM CARDS" not in run_stage2()


# --- readout option C: browser/Share HTML renderer and Word export ------------------------------------------

def _normal_html(extra):
    from tests.test_fcv_readout import normal
    return normal(extra)


def test_renderer_shows_line_tag_and_closed_panel_only_when_fields_present():
    plain = _normal_html({})
    assert "fr-sector-line" not in plain and "Sector check" not in plain
    extra = {"sectorProvenance": "Sector checks: Water (lead Practice Area). Reflected in priority 1.",
             "sectorAdditional": [{"card_id": "mc-12", "text": "Downstream allocation rules could be set out.",
                                   "page_ref": "25", "sources": ["Turbulent Waters (2017, p.35)"]}],
             "priorities": [dict(__import__("tests.test_fcv_readout", fromlist=["NORMAL_PRIORITY"]).NORMAL_PRIORITY,
                                 sector_cards=["mc-03"])]}
    html = _normal_html(extra)
    assert 'class="fr-note fr-sector-line"' in html and "Reflected in priority 1." in html
    assert '<span class="fr-sector-tag">Sector check</span>' in html
    panel = html[html.index("Additional sector considerations") - 200:]
    assert '<details class="fr-disc">' in panel and "<details class=\"fr-disc\" open" not in panel
    assert "Downstream allocation rules could be set out." in html and "(p.25)" in html
    assert "Guidance: Turbulent Waters (2017, p.35)" in html
    # The sector line sits inside the priorities section, after the cards.
    assert html.index("fr-sector-line") > html.index('id="fr-priority-1"')


def test_word_export_adds_line_and_grey_box_only_when_fields_present():
    from io import BytesIO

    from docx import Document

    from tests.test_fcv_priority_advisory_exports import _docx_text
    priority = {"title": "Priority 1 · Clarify siting", "the_gap": "Gap.", "why_it_matters": "Why.",
                "actions": [{"document_element": "PAD", "guidance": "Do it.", "suggested_language": "Text."}]}
    client = app.app.test_client()
    base = client.post("/api/download-report", json={"summary": "", "priorities": [priority], "metadata": {}})
    assert base.status_code == 200
    assert "Sector checks" not in _docx_text(Document(BytesIO(base.data)))
    with_sector = client.post("/api/download-report", json={
        "summary": "", "priorities": [priority], "metadata": {},
        "sector_provenance": "Sector checks: Water (lead Practice Area). Reflected in priority 1.",
        "sector_additional": [{"card_id": "mc-12", "text": "Downstream allocation rules could be set out.",
                               "page_ref": "25", "sources": ["Turbulent Waters (2017, p.35)"]}]})
    assert with_sector.status_code == 200
    text = _docx_text(Document(BytesIO(with_sector.data)))
    assert "Sector checks: Water (lead Practice Area). Reflected in priority 1." in text
    assert "ADDITIONAL SECTOR CONSIDERATIONS" in text
    assert "Downstream allocation rules could be set out. (p.25) Guidance: Turbulent Waters (2017, p.35)" in text


def test_word_priority_header_marks_sector_shaped_priorities():
    from io import BytesIO

    from docx import Document

    from tests.test_fcv_priority_advisory_exports import _docx_text
    base = {"the_gap": "Gap.", "why_it_matters": "Why.", "risk_level": "High", "actions": []}
    shaped = dict(base, title="Priority 1 · Sequence tariffs", sector_cards=["mc-13"])
    plain = dict(base, title="Priority 2 · Monitor context", sector_cards=[])
    resp = app.app.test_client().post("/api/download-report",
                                      json={"summary": "", "priorities": [shaped, plain], "metadata": {}})
    assert resp.status_code == 200
    text = _docx_text(Document(BytesIO(resp.data)))
    assert text.count("SECTOR CHECK") == 1
