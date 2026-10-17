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


def test_native_finding_links_directly_cited_accepted_priority():
    _, assessment = example()
    assessment['reader_contract'] = 'final-reader-v1'
    priority = {'recommendation_id':'REC-2', 'rank':2, 'residual_gap_ids':[]}
    assessment['priorities'] = [priority]
    assessment['assessment_narratives'][0]['evidence_ids'] = ['PF-1', 'REC-2']
    themes = _assessment_themes([], [], [priority], [], assessment=assessment)
    assert themes[0]['priority_ranks'] == [2]
    assert 'href="#climate-priority-2"' in _themes_html({'assessment_themes':themes})

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
    assert 'assessment_narratives' not in schema
    assert schema['reader_contract']['enum'] == ['final-reader-v1']
    assert 'assessment_narratives' in stage_output_schema('reader_compiler')['properties']

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


def test_benefits_prose_prompts_build_mechanisms_before_diagnosing_gaps():
    from sector_lenses.climate_verified_prompts import (
        _analysis_prompt, _reader_prompt, _reader_review_prompt,
    )

    analysis = _analysis_prompt({})
    assert 'who could benefit' in analysis
    assert 'existing_responses and pathways' in analysis
    assert 'not a documented omission' in analysis
    reader = ' '.join(_reader_prompt({}).split())
    assert '150-180 words' in reader
    assert 'answer directly without repeating questions' in reader
    assert 'Start with what the project could make possible' in reader
    assert 'who could be left out' in reader
    assert 'instrument content was not supplied' in reader
    review = ' '.join(_reader_review_prompt({}).split())
    assert 'absence of an explicit dividend mechanism' in review
    assert 'conditional mechanism' in review


def test_clear_sentence_opening_keeps_proper_name_and_acronym_guards():
    from sector_lenses.climate_verified_schemas import validate_summary_fragment

    canonical = 'The project supports traders and fair access.'
    assert validate_summary_fragment(
        'Clear access arrangements support fair participation.',
        canonical_text=canonical, allow_paraphrase=True)
    for text in ('Clear Cooperative supports traders.', 'CLEAR supports traders.',
                 'Clear supports traders.'):
        assert not validate_summary_fragment(
            text, canonical_text=canonical, allow_paraphrase=True)


def test_grammatical_opening_phrases_do_not_admit_single_word_actors():
    from sector_lenses.climate_verified_schemas import validate_summary_fragment

    canonical = 'The project supports traders. The plans are updated and operations are described.'
    for text in (
        'Accepted priorities support fair access.',
        'Setting out operations supports fair access.',
        'Updates to the plans are described.',
        'Limited visibility leaves access unverified.',
        'Alongside this sit access arrangements.',
    ):
        assert validate_summary_fragment(
            text, canonical_text=canonical, allow_paraphrase=True)
    for actor in ('Accepted', 'Setting', 'Updates', 'Limited', 'Alongside'):
        assert not validate_summary_fragment(
            actor + ' supports traders.', canonical_text=canonical, allow_paraphrase=True)


def test_reader_reference_binding_uses_only_explicit_same_passage_project_facts():
    from sector_lenses.climate_final_reader import bind_same_passage_project_references

    payload = {'summary_paragraphs': [{'object_id':'SUM-001',
        'text':'The project supports the Rumonge market.', 'evidence_ids':['PF-1']}],
        'assessment_narratives':[]}
    assessment = {'facts':[
        {'claim_id':'PF-1','epistemic_status':'explicit','statement':'The project supports markets.',
         'source_block_ids':['BLOCK-1']},
        {'claim_id':'PF-2','epistemic_status':'explicit','object_value':'Rumonge market',
         'source_block_ids':['BLOCK-1']},
        {'claim_id':'PF-3','epistemic_status':'explicit','object_value':'Atlantis market',
         'source_block_ids':['BLOCK-2']},
    ]}
    repaired, count = bind_same_passage_project_references(payload, assessment)
    assert count == 1
    assert repaired['summary_paragraphs'][0]['evidence_ids'] == ['PF-1','PF-2']
    assert payload['summary_paragraphs'][0]['evidence_ids'] == ['PF-1']
    generic = copy.deepcopy(assessment)
    generic['facts'].append({'claim_id':'PF-4', 'epistemic_status':'explicit',
                            'statement':'The Project has another activity.', 'source_block_ids':['BLOCK-1']})
    assert bind_same_passage_project_references(payload, generic)[1] == 1
    ambiguous = copy.deepcopy(assessment)
    ambiguous['facts'].append({'claim_id':'PF-4', 'epistemic_status':'explicit',
                              'statement':'Rumonge has another activity.', 'source_block_ids':['BLOCK-1']})
    assert bind_same_passage_project_references(payload, ambiguous) == (payload, 0)
    for edit in ('other_passage','unknown_place','not_explicit','country_evidence'):
        candidate = copy.deepcopy(payload)
        source = copy.deepcopy(assessment)
        if edit == 'other_passage': candidate['summary_paragraphs'][0]['text']='The project supports the Atlantis market.'
        elif edit == 'unknown_place': candidate['summary_paragraphs'][0]['text']='The project supports the Neverland market.'
        elif edit == 'not_explicit': source['facts'][1]['epistemic_status']='not_found'
        else:
            source['facts'].pop(1)
            source['context_evidence']=[{'evidence_id':'CE-1','statement':'Rumonge market','source_block_ids':['BLOCK-1']}]
        assert bind_same_passage_project_references(candidate, source) == (candidate,0)


def test_conditional_consequences_keep_new_action_and_entity_checks():
    from sector_lenses.climate_verified_schemas import validate_summary_fragment
    canonical = 'The project changes layouts and access.'
    for verb in ('reduce', 'cause', 'prevent', 'lead'):
        text = 'The changes could ' + verb + ' access problems.'
        assert validate_summary_fragment(text, canonical_text=canonical, allow_paraphrase=True)
        assert not validate_summary_fragment(text, canonical_text=canonical)
    for text in ('The project will reduce access.', 'The project could launch a review.',
                 'The changes could reduce access for Atlantis.', 'The changes could reduce access for 999 traders.'):
        assert not validate_summary_fragment(text, canonical_text=canonical, allow_paraphrase=True)
