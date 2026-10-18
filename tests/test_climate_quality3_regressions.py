"""Offline reproductions of quality trial 3 defects; source passages are synthetic."""

import json
import subprocess

from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_render import build_reader_model
from sector_lenses.climate_verified_schemas import validate_summary_fragment
from tests.test_climate_lens_frontend import INDEX, _extract_js_function


def test_ordinary_capitalized_stopwords_are_not_new_entities():
    for prefix in ("After", "Between", "With"):
        assert validate_summary_fragment(
            prefix + " flooding, the project supports climate resilience.",
            canonical_text="Flooding affects the project, which supports climate resilience.",
        )
    assert not validate_summary_fragment(
        "Rwanda supports climate resilience.",
        canonical_text="The project supports climate resilience in Burundi.",
    )


def test_all_verified_stages_share_scope_and_status_calibration():
    for stage in ("fact_extraction", "bounded_analysis", "judgment_review",
                  "recommendation_compiler", "drafting_compiler", "conditional_review"):
        prompt = build_verified_stage_prompt(stage, {})
        assert "Routine climate hazard screening is sensitivity" in prompt
        assert "wider peace or social dividend mechanism" in prompt
        assert "required or planned update is not a completed update" in prompt


def test_drafting_does_not_guess_a_relative_placement():
    prompt = build_verified_stage_prompt("drafting_compiler", {})
    assert "Do not prefix the paragraph with Add, Insert or Place instructions" in prompt
    assert 'Place immediately after the' not in prompt


def test_af_reader_does_not_presume_an_upcoming_approval():
    reader = build_reader_model({
        "operation_context": {"document_type": "AF", "instrument_type": "IPF"},
        "priorities": [{"recommendation_id": "REC-001", "rank": 1}],
    })
    cycle = reader["priorities"][0]["project_cycle"]
    assert cycle["secondary_label"] == "At the applicable Additional Financing review"


def test_saved_scope_uses_authoritative_climate_reader_context():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "syncClimateCountryScope")
    script = "let countryScope='single';let climateVerifiedReader=null;\n" + helper + """
climateVerifiedReader={operation_context:{country_scope:'multi'}};
syncClimateCountryScope();if(countryScope!=='multi')throw new Error('multi-country scope lost');
climateVerifiedReader={operation_context:{country_scope:'invalid'}};
syncClimateCountryScope();if(countryScope!=='multi')throw new Error('invalid scope accepted');
climateVerifiedReader=null;syncClimateCountryScope();
"""
    result = subprocess.run(["node", "-"], input=script, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    for name in ("renderOut", "epSafeStore", "saveSession"):
        assert "syncClimateCountryScope()" in _extract_js_function(source, name)


def _quoted_bundle():
    from tests.test_climate_research import _valid_bundle
    bundle = _valid_bundle()
    quote = "Flood timing affects access roads and fishing households."
    bundle["claims"][0].update(claim=quote, source_excerpt=quote)
    return bundle


def test_research_admits_only_matching_provider_passages():
    from sector_lenses.research import verify_climate_research_claims
    bundle = _quoted_bundle()
    quote = bundle["claims"][0]["source_excerpt"]
    content = [{"type": "text", "text": "Uncited model synthesis is not evidence.",
                "citations": [{"url": bundle["sources"][0]["url"], "cited_text": quote}]}]
    result = verify_climate_research_claims(bundle, content)
    assert result["claims"][0]["claim"] == quote
    assert result["claims"][0]["source_excerpt"] == quote
    assert bundle["claims"][0]["claim"] == quote  # input is not mutated
    assert not verify_climate_research_claims(bundle, [])['claims']
    fabricated = json.loads(json.dumps(bundle))
    fabricated["claims"][0]["source_excerpt"] = "A fabricated source sentence."
    assert not verify_climate_research_claims(fabricated, content)['claims']


def test_research_rejects_changed_quantities_and_wrong_source_urls():
    from sector_lenses.research import verify_climate_research_claims
    bundle = _quoted_bundle()
    quote = "Sediment loss in Burundi could increase by 200 percent by 2050."
    bundle["claims"][0].update(
        claim="Burundi loses 5.2 percent of its land every year.", source_excerpt=quote)
    content = [{"type": "text", "citations": [{
        "url": bundle["sources"][0]["url"], "cited_text": quote}]}]
    assert not verify_climate_research_claims(bundle, content)['claims']
    bundle["claims"][0]["claim"] = quote
    content[0]["citations"][0]["url"] = "https://www.un.org/different-source"
    assert not verify_climate_research_claims(bundle, content)['claims']


def test_research_uses_the_passage_not_a_model_measure_interpretation():
    from sector_lenses.research import verify_climate_research_claims
    bundle = _quoted_bundle()
    quote = "Flood timing affects access roads and fishing households."
    bundle["claims"][0]["claim"] = "Changing flood timing affects access roads and fishing households."
    content = [{"type": "text", "citations": [{
        "url": bundle["sources"][0]["url"], "cited_text": quote}]}]
    result = verify_climate_research_claims(bundle, content)
    assert result["claims"][0]["claim"] == quote


def test_native_citation_short_clauses_are_preserved_without_invented_punctuation():
    from sector_lenses.research import verify_climate_research_claims
    bundle = _quoted_bundle()
    quote = "Flood timing affects access roads"
    bundle["claims"][0].update(claim=quote, source_excerpt=quote)
    content = [{"type": "text", "citations": [{
        "url": bundle["sources"][0]["url"], "cited_text": quote}]}]
    assert verify_climate_research_claims(bundle, content)["claims"][0]["claim"] == quote


def test_citation_blocks_can_split_inside_research_json_strings():
    import app
    from tests.test_climate_research import _SequencedResearchClient, _valid_climate_response
    from types import SimpleNamespace
    response = _valid_climate_response()
    block = response.content[0]
    cut = block.text.index("timing") + 3
    response.content = [SimpleNamespace(type="text", text=block.text[:cut], citations=block.citations),
                        SimpleNamespace(type="text", text=block.text[cut:], citations=[])]
    client = _SequencedResearchClient([response])
    result = app.run_climate_web_research("South Sudan", "Fisheries", {}, client)
    assert result["status"] == "complete"
    assert len(client.calls) == 1
