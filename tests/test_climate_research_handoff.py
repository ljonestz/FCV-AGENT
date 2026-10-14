from tests.test_climate_verified_pipeline import _native_pass_review
"""No-cost regressions for native citations and empty contextual evidence."""

from copy import deepcopy
from types import SimpleNamespace
import json

from sector_lenses.research import build_climate_evidence_packet, build_climate_search_prompt
from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_render import build_reader_model
from tests.test_climate_summary_completeness import _multiple_responses
from tests.test_climate_verified_pipeline import FakeClient, _arguments
from sector_lenses.climate_verified_pipeline import PipelineClients, run_verified_climate_pipeline


def test_later_citations_enrich_metadata_and_survive_the_four_source_cap():
    hits = [{"type":"web_search_result","url":f"https://worldbank.org/report-{i}",
             "title":f"Report {i}","encrypted_content":"opaque"} for i in range(6)]
    bdi = {"url":hits[0]["url"],"title":"Report 0","cited_text":"Flooding disrupts access to border infrastructure in Burundi."}
    drc = {"url":"https://worldbank.org/drc-report","title":"DRC report","cited_text":"Flooding and insecurity interrupt road access in eastern DRC."}
    blocks = [{"type":"web_search_tool_result","content":hits},
              {"type":"text","text":"Observed regional climate evidence.","citations":[bdi,drc]}]
    packet=build_climate_evidence_packet(blocks,{"country_scope":"multi"})
    assert packet["notes"] == "Observed regional climate evidence."
    assert len(packet["sources"]) == 4
    assert packet["sources"][0]["excerpt"] == bdi["cited_text"]
    assert packet["sources"][1]["url"] == drc["url"]
    assert "opaque" not in json.dumps(packet)


def test_search_requests_bounded_native_quotes_for_the_structurer():
    prompt=build_climate_search_prompt("Burundi","Transport",{})
    assert "four to six short verbatim passages" in prompt
    assert "native web-source citations" in prompt
    assert "140 characters" in prompt


def test_analysis_explains_reference_types_and_empty_context():
    prompt=build_verified_stage_prompt("bounded_analysis",{})
    assert "pathways.evidence_ids" in prompt and "context_evidence" in prompt
    assert "empty" in prompt and "Do not invent" in prompt
    assert "project_anchor_ids" in prompt and "facts.claim_id" in prompt


def test_project_only_analysis_retains_supported_gaps_responses_and_actions():
    responses=deepcopy(_multiple_responses())
    for item in responses[1]["pathways"]:item["evidence_ids"]=[]
    for item in responses[1]["residual_gaps"]:item["evidence_ids"]=["PF-001"]
    responses[1]["existing_responses"]=[{"response_id":"ER-001","project_fact_ids":["PF-001"],"pathway_ids":["PW-001"],"description":"The design addresses flood resilience. Seasonal access is linked to documented project activities.","limitation":"Access criteria remain unclear."}]
    args=_arguments();args["context_evidence"]=[]
    result=run_verified_climate_pipeline(**args,clients=PipelineClients(
        FakeClient(responses,[]),FakeClient([_native_pass_review],[])))
    reader=build_reader_model(result)
    assert len(reader["summary_gaps"])==5
    assert len(reader["priorities"])==5
    assert result["analysis"]["existing_responses"]


def test_pruned_analysis_has_a_plain_reader_limitation():
    responses=deepcopy(_multiple_responses())
    for item in responses[1]["pathways"]:item["evidence_ids"]=["CE-NOT-SUPPLIED"]
    result=run_verified_climate_pipeline(**_arguments(),clients=PipelineClients(
        FakeClient(responses,[]),FakeClient([_native_pass_review],[])))
    reader=build_reader_model(result)
    assert reader["analysis_status"]=="partial"
    assert "withheld" in reader["analysis_message"]
    assert "absence of risks or gaps" in reader["analysis_message"]



def test_pruned_analysis_notice_is_retained_in_html_word_and_both_views():
    from io import BytesIO
    from docx import Document
    from sector_lenses.climate_verified_render import render_reader_html, write_reader_docx
    from tests.test_climate_lens_frontend import INDEX, _extract_js_function
    message="Fewer findings or actions do not establish an absence of risks or gaps."
    reader={"analysis_status":"partial","analysis_message":message}
    assert message in render_reader_html(reader)
    stream=BytesIO();write_reader_docx(reader,stream);stream.seek(0)
    assert message in " ".join(p.text for p in Document(stream).paragraphs)
    source=INDEX.read_text(encoding="utf-8")
    for name in ("renderClimateVerifiedSummary","renderClimateVerifiedAssessment"):
        helper=_extract_js_function(source,name)
        assert "analysis_status" in helper and "analysis_message" in helper
        assert "Assessment evidence is incomplete" in helper


def test_pause_turn_search_hits_are_counted_across_preserved_turns():
    import app
    from tests.test_climate_research import _SequencedResearchClient
    from sector_lenses.research import CLIMATE_RESEARCH_START, CLIMATE_RESEARCH_END
    hits = [SimpleNamespace(type='web_search_tool_result', content=[SimpleNamespace(
        title=title, url=url, encrypted_content='opaque')])
        for title, url in [('Burundi climate report', 'https://worldbank.org/climate'),
                           ('Burundi flood report', 'https://un.org/flood')]]
    citations = [SimpleNamespace(title=title, url=url, cited_text='Flooding disrupts access in Burundi.')
        for title, url in [('Burundi climate report', 'https://worldbank.org/climate'),
                           ('Burundi flood report', 'https://un.org/flood')]]
    paused = SimpleNamespace(content=[hits[0], SimpleNamespace(type='text', text='Source notes.',
        citations=[citations[0]])], stop_reason='pause_turn')
    continued = SimpleNamespace(content=[hits[1], SimpleNamespace(type='text', text='Source notes.',
        citations=[citations[1]])], stop_reason='end_turn')
    selections = [{'passage_id': identifier, 'geographies': ['Burundi'],
        'project_elements': ['Border infrastructure'], 'affected_groups': ['Traders'],
        'systems_or_assets': ['Road access'], 'evidence_status': 'observed',
        'confidence': 'medium', 'time_horizons': ['project-lifetime']}
        for identifier in ('CP-001', 'CP-002')]
    classified = SimpleNamespace(content=[SimpleNamespace(type='text',
        text=CLIMATE_RESEARCH_START + json.dumps({'selections': selections}) + CLIMATE_RESEARCH_END)],
        stop_reason='end_turn')
    client = _SequencedResearchClient([paused, continued, classified])
    result = app.run_climate_web_research('Burundi', 'Transport', {'beneficiary_countries': ['Burundi'], 'project_elements': ['Border infrastructure']}, client)
    assert result['status'] == 'complete'
    assert len(client.calls) == 3
    assert client.calls[0]['thinking'] == {'type': 'between_tools'}
    assert client.calls[0]['tools'][0]['max_uses'] == 2
    # Preserve encrypted provider blocks only for actual search continuation.
    assert client.calls[1]['messages'][1]['content'] is paused.content
    assert 'tools' not in client.calls[-1]
    assert [message['role'] for message in client.calls[-1]['messages']] == ['user']
    assert 'CP-001' in client.calls[-1]['messages'][0]['content']
    assert 'CP-002' in client.calls[-1]['messages'][0]['content']


def test_source_notice_explains_regional_coverage_and_omits_normal_primary_selection():
    import app
    codes=["PRIMARY_APPLICABILITY_USER_DESIGNATED","MULTI_COUNTRY_BANK_WITHHELD"]
    messages=app._climate_source_warning_messages(codes)
    assert len(messages)==1
    assert "each beneficiary country" in messages[0]["message"]
    assert "Primary Applicability" not in messages[0]["message"]
    assert codes==["PRIMARY_APPLICABILITY_USER_DESIGNATED","MULTI_COUNTRY_BANK_WITHHELD"]
    assert app._climate_source_warning_messages(["PRIMARY_DOCUMENT_PRECEDENCE_UNRESOLVED"])[0]["message"].startswith("Confirm which document")


def test_metadata_snippets_cannot_displace_received_citations():
    hits = [{"url": f"https://worldbank.org/hit-{i}", "title": f"Search hit {i}",
             "snippet": "Metadata context " * 20} for i in range(6)]
    citations = [
        {"url": "https://worldbank.org/bdi", "title": "Burundi climate report",
         "cited_text": "Flooding interrupts road access in Burundi."},
        {"url": "https://worldbank.org/drc", "title": "DRC climate report",
         "cited_text": "Flooding interrupts road access in DRC."},
    ]
    packet = build_climate_evidence_packet([
        {"type": "web_search_tool_result", "content": hits},
        {"type": "text", "citations": citations},
    ], {"beneficiary_countries": ["Burundi", "Congo, Democratic Republic of"]})
    assert {p["url"] for p in packet["passages"]} == {c["url"] for c in citations}
    assert len(packet["sources"]) == 4


def test_later_country_citation_survives_source_and_passage_caps():
    citations = [{"url": f"https://worldbank.org/bdi-{i}", "title": "Burundi climate",
                  "cited_text": f"Flooding disrupts Burundi road route {i}."} for i in range(8)]
    drc = {"url": "https://worldbank.org/drc", "title": "Democratic Republic of the Congo",
           "cited_text": "Flooding interrupts road access in DRC."}
    citations.append(drc)
    packet = build_climate_evidence_packet([{"type": "text", "citations": citations}],
        {"beneficiary_countries": ["Burundi", "Congo, Democratic Republic of"]})
    assert any(p["excerpt"] == drc["cited_text"] and p["url"] == drc["url"]
               for p in packet["passages"])
    assert len(packet["sources"]) == 4
    assert len(packet["passages"]) <= 12
    assert len(json.dumps(packet, ensure_ascii=False)) <= 12_000


def test_passage_cap_retains_proof_for_each_selected_source():
    citations = [{"url": "https://worldbank.org/bdi", "title": "Burundi climate",
                  "cited_text": f"Flooding disrupts Burundi road route {i}."} for i in range(12)]
    drc = {"url": "https://worldbank.org/drc", "title": "DRC climate",
           "cited_text": "Flooding interrupts road access in DRC."}
    citations.append(drc)
    packet = build_climate_evidence_packet([{"type": "text", "citations": citations}],
        {"beneficiary_countries": ["Burundi", "Congo, Democratic Republic of"]})
    assert len(packet["passages"]) == 12
    assert any(p["url"] == drc["url"] for p in packet["passages"])
