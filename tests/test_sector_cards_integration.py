"""Stage wiring for mechanism cards: Stage 1 facts, routing, Stage 2 slice/parse, Stage 3 readout fields."""
from __future__ import annotations

import json

from sector_cards.integration import (
    SECTOR_FACTS_PROMPT,
    apply_sector_cards,
    build_readout_fields,
    build_stage2_card_slice,
    build_stage3_card_slice,
    extract_sector_cards,
    extract_sector_facts,
    route_from_facts,
    strip_sector_blocks,
)

DATASHEET = ("Water Global Practice\n" + "x " * 40 + "Practice Area (Lead) Contributing Practice Areas Water "
             "Environment, Natural Resources & the Blue Economy Climate Change and Disaster Screening")
STAGE1 = """Analysis text.
%%%SECTOR_FACTS_START%%%
practice_area_lead: Water
sector_label: water
sector_confidence: high
pdo_names_sector: true
ews_is_primary: false
cerc_only: false
fcv_setting: displacement_hosting
sector_shares: water=0.85; enrm=0.05
features:
- water_points_wash | share=0.40 | named=true | evidence=true | country=n/a | page=22
- nrm_landscape_forest | share=2.3% | named=true | evidence=true | country=n/a | page=24
- not_a_feature | share=0.5 | named=true | evidence=true | country=n/a | page=1
%%%SECTOR_FACTS_END%%%
More text."""


def test_prompt_block_is_parseable_template():
    assert "%%%SECTOR_FACTS_START%%%" in SECTOR_FACTS_PROMPT and "%%%SECTOR_FACTS_END%%%" in SECTOR_FACTS_PROMPT


def test_extract_sector_facts_parses_block_and_datasheet():
    f = extract_sector_facts(STAGE1, DATASHEET)
    assert f["error"] is False
    assert f["pa_lead_parsed"] == "Water" and f["pa_lead_model"] == "Water"
    assert f["sector_label"] == "water" and f["sector_confidence"] == "high"
    assert f["fcv_setting"] == "displacement_hosting"
    assert f["sector_shares"] == {"water": 0.85, "enrm": 0.05}
    assert [x["feature"] for x in f["features"]] == ["water_points_wash", "nrm_landscape_forest"]
    assert abs(f["features"][1]["financing_share"] - 0.023) < 1e-9
    json.dumps(f)  # JSON-safe for the done event


def test_missing_block_still_returns_datasheet_facts():
    f = extract_sector_facts("no block here", DATASHEET)
    assert f["error"] is True and f["pa_lead_parsed"] == "Water" and f["features"] == []


def _routing():
    return route_from_facts(extract_sector_facts(STAGE1, DATASHEET), instrument="IPF")


def test_route_from_facts_and_reason_line():
    r = _routing()
    assert r["sectors"] == ["water"]
    assert r["eligible"] and len(r["eligible"]) <= 8
    assert r["reason_line"].startswith("Sector lens: Water (lead Practice Area)")
    json.dumps(r)


def test_user_switch_off():
    facts = extract_sector_facts(STAGE1, DATASHEET)
    assert route_from_facts(facts, "IPF", disabled=True)["eligible"] == []
    first = _routing()["eligible"][0]["card_id"]
    r = route_from_facts(facts, "IPF", disabled_cards=[first])
    assert first not in [e["card_id"] for e in r["eligible"]]
    assert any(x["reason"] == "switched off by the user" for x in r["rejected"])


def test_stage2_slice_lists_only_eligible_cards_and_is_empty_without_them():
    r = _routing()
    s = build_stage2_card_slice(r)
    for e in r["eligible"]:
        assert f"[{e['card_id']}]" in s
    assert "%%%SECTOR_CARDS_START%%%" in s and "AT MOST 3" in s
    assert build_stage2_card_slice({"eligible": []}) == ""
    assert build_stage2_card_slice(None) == ""


def _stage2_output(cards):
    return "Stage 2 text\n%%%SECTOR_CARDS_START%%%\n" + json.dumps({"cards": cards}) + "\n%%%SECTOR_CARDS_END%%%"


def test_extract_sector_cards_validates_and_caps():
    r = _routing()
    ids = [e["card_id"] for e in r["eligible"]]
    good = [{"card_id": i, "finding": f"Finding {i}.", "page_ref": "22"} for i in ids]
    bad = [{"card_id": "mc-99", "finding": "x", "page_ref": "1"},           # not eligible
           {"card_id": ids[0], "finding": "duplicate", "page_ref": "1"},     # duplicate
           {"card_id": ids[0], "finding": "", "page_ref": "1"}]              # empty
    out = extract_sector_cards(_stage2_output(bad + good), r)
    assert len(out) <= 3 and len({o["card_id"] for o in out}) == len(out)
    assert all(o["card_id"] in ids for o in out)
    assert extract_sector_cards(_stage2_output([{"card_id": ids[0], "finding": "The project must fix it.",
                                                 "page_ref": "2"}]), r) == []


def test_missing_or_malformed_block_is_empty_not_an_error():
    r = _routing()
    assert extract_sector_cards("no block", r) == []
    assert extract_sector_cards("%%%SECTOR_CARDS_START%%% {bad json %%%SECTOR_CARDS_END%%%", r) == []
    assert extract_sector_cards(_stage2_output([]), r) == []


def test_strip_sector_blocks():
    text = STAGE1 + "\n" + _stage2_output([])
    out = strip_sector_blocks(text)
    assert "SECTOR_FACTS" not in out and "SECTOR_CARDS" not in out
    assert out.startswith("Analysis text.") and "More text." in out


def test_stage3_slice_and_readout_fields_fold_and_overflow():
    r = _routing()
    ids = [e["card_id"] for e in r["eligible"]][:3]
    findings = extract_sector_cards(_stage2_output(
        [{"card_id": i, "finding": f"Finding {i}.", "page_ref": "22"} for i in ids]), r)
    assert build_stage3_card_slice(findings).count("[mc-") == len(findings)
    priorities = [{"title": "A", "sector_cards": [ids[0], "mc-99"]}, {"title": "B"}]
    apply_sector_cards(priorities, findings)
    assert priorities[0]["sector_cards"] == [ids[0]] and priorities[1]["sector_cards"] == []
    fields = build_readout_fields(r, findings, priorities)
    assert fields["sector_provenance"].startswith("Sector lens: Water")
    assert "Reflected in priority 1." in fields["sector_provenance"]
    assert len(fields["sector_additional"]) == min(2, len(findings) - 1)
    assert all(a["card_id"] != ids[0] for a in fields["sector_additional"])
    assert all(a["sources"] for a in fields["sector_additional"])


def test_readout_fields_empty_when_nothing_applies():
    assert build_readout_fields({"eligible": []}, [], []) == {"sector_provenance": "", "sector_additional": []}
    r = _routing()
    fields = build_readout_fields(r, [], [])
    assert fields["sector_additional"] == [] and "No additional sector considerations" in fields["sector_provenance"]


def test_dpf_end_to_end():
    facts = extract_sector_facts("%%%SECTOR_FACTS_START%%%\nfcv_setting: post_conflict\n%%%SECTOR_FACTS_END%%%", "")
    r = route_from_facts(facts, "DPF", prior_actions=["The Recipient adopted a new electricity tariff schedule"])
    assert r["sectors"] == [] and [e["card_id"] for e in r["eligible"]] == ["mc-13"]
    assert "prior actions" in r["reason_line"]


def test_context_from_flags_and_setting():
    from sector_cards.integration import context_from
    assert context_from({"displacement_context": True}, "any") == frozenset({"displacement"})
    assert context_from({}, "criminal_violence") == frozenset({"insecurity"})
    assert context_from({"tpi_mentioned": True, "security_risks_noted": True}, "any") == \
        frozenset({"parallel_delivery", "insecurity"})
    assert context_from(None, "institutional_fragility") == frozenset()
