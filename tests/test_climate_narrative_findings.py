"""Question-led findings preserve evidence while admitting concise prose."""
import copy
from pathlib import Path
from sector_lenses.climate_verified_render import _assessment_themes, _themes_html
from sector_lenses.climate_verified_prompts import _judgment_prompt, _common
from sector_lenses.climate_verified_schemas import stage_output_schema

TEXT = "The project protects the market from flooding and supports access for small traders. The design provides a basis for more reliable trading, but access during construction remains unclear. This matters because the same households need safe routes to reach the market while works are under way."

def example():
    gaps = [{"gap_id":"RG-1", "text":"Access during construction remains unclear."}]
    assessment = {"facts":[{"claim_id":"PF-1", "statement":TEXT}], "analysis":{"residual_gaps":[{"gap_id":"RG-1", "statement":gaps[0]["text"]}]}, "assessment_narratives":[{"theme":"design", "paragraphs":[TEXT], "evidence_ids":["PF-1","RG-1"]}]}
    return gaps, assessment

def test_narrative_is_admitted_and_links_preserved():
    gaps, assessment = example()
    themes = _assessment_themes(gaps, [], [{"rank":2,"residual_gap_ids":["RG-1"]}], [], assessment=assessment)
    assert themes[0]["paragraphs"] == [TEXT]
    assert themes[0]["question"].endswith("design and delivery?")
    html = _themes_html({"assessment_themes":themes})
    assert '<p>'+TEXT+'</p>' in html
    assert 'href="#climate-priority-2"' in html
    assert 'climate-theme-evidence' not in html

def test_unknown_evidence_and_new_numbers_fall_back_to_complete_findings():
    for edit in ("evidence", "number", "entity", "duplicate"):
        gaps, assessment = example()
        if edit == "evidence": assessment["assessment_narratives"][0]["evidence_ids"].append("PF-UNKNOWN")
        elif edit == "number": assessment["assessment_narratives"][0]["paragraphs"] = [TEXT.replace("small traders", "9000 small traders")]
        elif edit == "entity": assessment["assessment_narratives"][0]["paragraphs"] = [TEXT.replace("small traders", "Atlantis Cooperative traders")]
        else: assessment["assessment_narratives"].append(copy.deepcopy(assessment["assessment_narratives"][0]))
        themes = _assessment_themes(gaps, [], [], [], assessment=assessment)
        assert themes[0]["paragraphs"] == [gaps[0]["text"]]

def test_dividends_calibration_and_provider_schema_are_aligned():
    prompt = _common("", {})
    assert "Do not penalize" in prompt
    assert "terminology" in prompt
    assert "enabling conditions" in prompt
    assert "assessment_narratives" in _judgment_prompt({})
    schema = stage_output_schema("judgment_review")["properties"]
    assert "180" in schema["executive_readout"]["description"]
    assert "assessment_narratives" in schema

def test_supporting_sections_have_distinct_panels_and_question_prose():
    source = (Path(__file__).resolve().parents[1]/"index.html").read_text(encoding="utf-8")
    assert "const question=theme.question||" in source
    assert "climate-reference-panel" in source
    assert "climate-section-description" in source


def test_paraphrase_permission_does_not_relax_existing_summary_contract():
    from sector_lenses.climate_verified_schemas import validate_summary_fragment
    text = "The project supports opportunities for collaboration."
    canonical = "The project supports opportunities for traders."
    assert not validate_summary_fragment(text, canonical_text=canonical)
    assert validate_summary_fragment(text, canonical_text=canonical, allow_paraphrase=True)


def test_plain_paraphrase_retains_number_entity_and_markup_controls():
    from sector_lenses.climate_verified_schemas import validate_summary_fragment
    assert validate_summary_fragment("For Component 3, the project supports collaboration.", canonical_text="Component 3 supports traders.", allow_paraphrase=True)
    for text in ("The project supports 999 traders.", "The project supports Atlantis Cooperative.", "The project supports <b>traders</b>."):
        assert not validate_summary_fragment(text, canonical_text="The project supports traders.", allow_paraphrase=True)


def test_ordinary_narrative_nouns_are_not_mistaken_for_names():
    from sector_lenses.climate_verified_schemas import validate_summary_fragment
    canonical = "The project supports traders and participation."
    text = "Links to wider benefits depend on participation."
    assert validate_summary_fragment(text, canonical_text=canonical, allow_paraphrase=True)
    assert not validate_summary_fragment(text, canonical_text=canonical)
    assert validate_summary_fragment("Fair access depends on participation.", canonical_text=canonical, allow_paraphrase=True)
    assert validate_summary_fragment("Clarifying access supports participation.", canonical_text=canonical, allow_paraphrase=True)
    for text in ("Links Cooperative supports traders.",
                 "LINKS supports traders.", "Links reach 999 traders."):
        assert not validate_summary_fragment(text, canonical_text=canonical, allow_paraphrase=True)


def test_legacy_reader_theme_still_displays_complete_findings():
    html = _themes_html({"assessment_themes":[{"title":"Climate risks, design and delivery", "findings":[{"text":"The original complete finding remains available.", "priority_ranks":[1]}]}]})
    assert "The original complete finding remains available." in html
    assert "Does the project address" in html


def test_malformed_legacy_paragraphs_do_not_hide_original_findings():
    html = _themes_html({"assessment_themes":[{"title":"Climate risks, design and delivery", "paragraphs":[None], "priority_ranks":None, "findings":[{"text":"The original finding remains available.", "priority_ranks":None}]}]})
    assert "The original finding remains available." in html


def test_verified_drc_alias_and_today_opening_preserve_entity_boundaries():
    from sector_lenses.climate_verified_schemas import validate_summary_fragment
    canonical = "The project supports traders in DRC."
    assert validate_summary_fragment(
        "Today, the project supports traders in the Democratic Republic of Congo.",
        canonical_text=canonical, allow_paraphrase=True,
    )
    for text, support in (
        ("The project supports traders in the Democratic Republic of Congo.", "The project supports traders in the Republic of Congo."),
        ("The project supports traders in the Republic of Congo.", canonical),
        ("Today Cooperative supports traders.", canonical),
        ("TODAY supports traders.", canonical),
    ):
        assert not validate_summary_fragment(text, canonical_text=support, allow_paraphrase=True)


def test_summary_does_not_require_rating_labels_in_flowing_prose():
    from sector_lenses.climate_verified_schemas import validate_summary_overview
    first = "The project recognizes flooding risks and supports access for traders. " * 8
    second = "The remaining priorities confirm access for traders during works and support reliable delivery. " * 7
    paragraphs = [first.strip(), second.strip()]
    assert validate_summary_overview({"paragraphs": paragraphs}, canonical_text=paragraphs) == paragraphs
