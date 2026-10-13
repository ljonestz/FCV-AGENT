"""Free regressions for final-trial narrative and source-metadata safeguards."""

from copy import deepcopy
import json
import subprocess

from sector_lenses.climate_verified_render import build_reader_model
from sector_lenses.research import verify_climate_research_claims
from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from tests.test_climate_summary_completeness import _run_multiple, GAP_TEXTS
from tests.test_climate_quality3_regressions import _quoted_bundle
from tests.test_climate_lens_frontend import INDEX, _extract_js_function, _js_escape_helper


def test_new_responsiveness_classification_cannot_enter_only_through_narrative():
    assessment,_,_=_run_multiple(3)
    original=assessment["priorities"][1]
    original["narrative"]="Clarify the definition and pending baseline of the existing climate-resilient access indicator. This is an optional responsiveness-and-measurement improvement, not a required correction."
    before=deepcopy(original)
    reader=build_reader_model(assessment)
    item=reader["priorities"][1]
    assert item["narrative"]==""
    assert item["minimum_action"]==before["minimum_action"]
    assert len(reader["priorities"])==3
    assert reader["technical_annex"]["withheld_narrative_count"]==1
    assert original==before
    original["decision"]="Consider responsiveness through a documented wider peace-dividend mechanism."
    assert build_reader_model(assessment)["priorities"][1]["narrative"]==before["narrative"]


def test_only_cited_sources_and_provider_publication_dates_are_retained():
    bundle=_quoted_bundle()
    bundle["sources"][0]["publication_date"]="2023-11-15"
    bundle["sources"].append({**bundle["sources"][0],"id":"unused","url":"https://worldbank.org/unused"})
    quote=bundle["claims"][0]["source_excerpt"]
    citation={"url":bundle["sources"][0]["url"],"cited_text":quote}
    content=[{"type":"text","citations":[citation]}]
    result=verify_climate_research_claims(bundle,content)
    assert len(result["sources"])==1
    assert result["sources"][0]["publication_date"]==""
    assert bundle["sources"][0]["publication_date"]=="2023-11-15"
    citation["publication_date"]="2023-11-16"
    assert verify_climate_research_claims(bundle,content)["sources"][0]["publication_date"]=="2023-11-16"


def test_dividend_gap_list_keeps_scope_relative_optional_message():
    source=INDEX.read_text(encoding="utf-8")
    script=_js_escape_helper()+_extract_js_function(source,"boldEscapedFirstSentence")+_extract_js_function(source,"renderClimateSummaryGaps")
    script+="\nconsole.log(renderClimateSummaryGaps("+json.dumps({"summary_gaps":[{"text":text} for text in GAP_TEXTS]})+",[]));"
    result=subprocess.run(["node","-"],input=script,text=True,capture_output=True)
    assert result.returncode==0,result.stderr
    assert result.stdout.count('<li class="normal-summary-gap"')==5
    assert "Optional wider dividends depend on the project's scope" in result.stdout


def test_prompts_keep_titles_minimum_actions_and_dividend_classification_aligned():
    compiler=build_verified_stage_prompt("recommendation_compiler",{})
    assert "title must describe the minimum action" in compiler
    assert "Confirming a baseline" in compiler
    reviewer=build_verified_stage_prompt("conditional_review",{})
    assert "measurement alone is not responsiveness" in reviewer
