"""Review-stage selector and due-diligence checklist (2026-11-16)."""

import json
from io import BytesIO

from docx import Document

import review_stage as rs
from app import (
    app,
    append_review_stage_blocks,
    build_regime_header,
    extract_priorities,
    review_stage_done_fields,
)
from tests.test_climate_lens_frontend import _readout_harness, _run_node

NEW_TWO_STEP = {"preparation_regime": "new_model", "processing_model": "two_step"}
NEW_ONE_STEP = {"preparation_regime": "new_model", "processing_model": "one_step"}
LEGACY = {"preparation_regime": "legacy_transitional", "processing_model": "unknown"}
UNRESOLVED = {"preparation_regime": "unresolved_policy_source", "processing_model": "unknown"}

ROWS = [
    {"question_id": "results_ir", "note": "Partial: The Results Framework has no early-warning indicator; see Priority 2."},
    {"question_id": "context_ir", "note": "The risk section updates the conflict analysis to 2026; see Section II."},
    {"question_id": "design_td", "note": "Wrong column; should be dropped."},
    {"question_id": "made_up_ir", "note": "Unknown id."},
    {"question_id": "engagement_ir", "note": ""},
    {"question_id": "context_ir", "note": "Duplicate."},
]


def test_normalize_review_stage():
    assert rs.normalize_review_stage("") == rs.AUTO
    assert rs.normalize_review_stage("auto") == rs.AUTO
    assert rs.normalize_review_stage("Not sure") == rs.AUTO
    assert rs.normalize_review_stage("bogus") == rs.AUTO
    assert rs.normalize_review_stage("IR") == "ir"
    assert rs.normalize_review_stage("af-restructuring") == "af_restructuring"


def test_no_selection_leaves_regime_unchanged():
    assert rs.apply_review_stage(LEGACY, "") == LEGACY
    assert rs.apply_review_stage(None, "auto") == {}


def test_selected_stage_pins_regime_and_keeps_detection():
    pinned = rs.apply_review_stage(LEGACY, "ir")
    assert pinned["preparation_regime"] == "new_model"
    assert pinned["processing_model"] == "two_step"
    assert pinned["detected_preparation_regime"] == "legacy_transitional"
    legacy = rs.apply_review_stage(NEW_TWO_STEP, "appraisal")
    assert legacy["preparation_regime"] == "legacy_transitional"
    # Legacy selection suppresses the new-model regime header.
    assert build_regime_header(legacy["preparation_regime"], legacy["processing_model"], "", "IPF") == ""
    # AF / restructuring keeps the detected regime.
    assert rs.apply_review_stage(NEW_ONE_STEP, "af_restructuring")["preparation_regime"] == "new_model"


def test_conflict_notice_only_on_material_mismatch():
    assert rs.stage_conflict_notice(rs.apply_review_stage(NEW_TWO_STEP, "td"), "td") == ""
    assert rs.stage_conflict_notice(rs.apply_review_stage(UNRESOLVED, "td"), "td") == ""
    assert rs.stage_conflict_notice(rs.apply_review_stage(LEGACY, "", ), "") == ""
    notice = rs.stage_conflict_notice(rs.apply_review_stage(LEGACY, "ir"), "ir")
    assert notice == ("The documents look like a legacy-process operation; the note is framed for the "
                      "Implementation Readiness review as chosen.")
    assert "new operating model" in rs.stage_conflict_notice(rs.apply_review_stage(NEW_TWO_STEP, "concept"), "concept")
    assert "One Review" in rs.stage_conflict_notice(rs.apply_review_stage(NEW_ONE_STEP, "td"), "td")
    assert "two-step" in rs.stage_conflict_notice(rs.apply_review_stage(NEW_TWO_STEP, "one_review"), "one_review")


def test_prompt_block_frames_stage_and_timing():
    assert rs.review_stage_prompt_block("") == ""
    ir = rs.review_stage_prompt_block("ir")
    assert "Implementation Readiness review" in ir
    assert "do not use before-TD-review" in ir
    concept = rs.review_stage_prompt_block("concept")
    assert "legacy timing vocabulary" in concept
    assert "Additional Financing" in rs.review_stage_prompt_block("af_restructuring")


def test_checklist_column_rules():
    assert rs.checklist_column("", LEGACY, "implementation") == ("impl", "")
    assert rs.checklist_column("td", UNRESOLVED) == ("td", "")
    assert rs.checklist_column("one_review", UNRESOLVED) == ("key", "")
    assert rs.checklist_column("af_restructuring", LEGACY) == ("impl", "")
    assert rs.checklist_column("concept", NEW_TWO_STEP) == (None, rs.LEGACY_CHECKLIST_NOTE)
    assert rs.checklist_column("", NEW_TWO_STEP) == ("key", "")
    assert rs.checklist_column("", LEGACY) == (None, rs.LEGACY_CHECKLIST_NOTE)
    assert rs.checklist_column("", UNRESOLVED) == (None, "")


def test_prompts_unchanged_without_selection_on_legacy_and_unresolved():
    base = "STAGE PROMPT"
    for regime in (LEGACY, UNRESOLVED):
        for stage in (2, 3):
            assert append_review_stage_blocks(base, stage, "", regime, "design") == base


def test_checklist_prompt_lists_column_ids_and_forbids_labels():
    prompt = append_review_stage_blocks("X", 3, "ir", rs.apply_review_stage(LEGACY, "ir"), "design")
    assert "REVIEW STAGE (selected by the user)" in prompt
    assert '"dd_checklist"' in prompt
    for element, _ in rs.CHECKLIST_ELEMENTS:
        assert f'"{element}_ir"' in prompt
    assert "_td\"" not in prompt
    assert "no ratings, scores, yes/no answers, status words" in prompt
    # Stage 2 gets the framing but never the checklist instruction.
    assert '"dd_checklist"' not in append_review_stage_blocks("X", 2, "ir", NEW_TWO_STEP, "design")


def test_normalize_dd_checklist_filters_orders_and_strips_status():
    rows = rs.normalize_dd_checklist(ROWS, "ir")
    assert [r["question_id"] for r in rows] == ["context_ir", "results_ir"]
    assert rows[1]["note"].startswith("The Results Framework")
    assert rows[0]["element"] == "Country context and FCV risks"
    assert rows[0]["question"].startswith("Have teams validated the FCV analysis")
    many = [{"question_id": f"{e}_key", "note": "Note."} for e, _ in rs.CHECKLIST_ELEMENTS]
    assert len(rs.normalize_dd_checklist(many, "key")) == rs.CHECKLIST_MAX_ROWS
    assert rs.normalize_dd_checklist("not a list") == []


def test_extract_priorities_passes_checklist_and_done_fields():
    text = "%%%JSON_START%%%" + json.dumps({"priorities": [{"title": "T", "the_gap": "G", "actions": []}], "dd_checklist": ROWS}) + "%%%JSON_END%%%"
    parsed = extract_priorities(text)
    assert parsed["dd_checklist"] == ROWS
    regime = rs.apply_review_stage(LEGACY, "ir")
    done = review_stage_done_fields(parsed, "ir", regime, "design")
    assert [r["question_id"] for r in done["dd_checklist"]] == ["context_ir", "results_ir"]
    assert done["dd_checklist_column"] == "Implementation Readiness review"
    assert done["review_stage_label"] == "Implementation Readiness review"
    assert "legacy-process" in done["review_stage_notice"]
    legacy_done = review_stage_done_fields(parsed, "", LEGACY, "design")
    assert legacy_done["dd_checklist"] == []
    assert legacy_done["dd_checklist_note"] == rs.LEGACY_CHECKLIST_NOTE
    assert extract_priorities("no json")["dd_checklist"] == []


def _dd_state():
    return {"review_stage": "ir", "review_stage_notice": "The documents look like a legacy-process operation.",
            "dd_checklist": rs.normalize_dd_checklist(ROWS, "ir"),
            "dd_checklist_column": "Implementation Readiness review", "dd_checklist_note": ""}


def test_readout_renders_collapsed_checklist_without_labels():
    state = json.dumps(_dd_state())
    script = _readout_harness() + f"""
const html = frApi().renderNormal({{stage3Markdown:'', sensitivitySummary:'S.', responsivenessSummary:'R.',
  priorities:[], riskExposure:{{}}, ddChecklist:{state}}});
if (!html.includes('Due-Diligence Checklist')) throw new Error('section missing');
if (!html.includes('<details class="fr-disc">')) throw new Error('not collapsed');
if (html.match(/<details class="fr-disc" open/)) throw new Error('should be collapsed');
if (!html.includes('Have teams validated the FCV analysis')) throw new Error('question missing');
if (!html.includes('see Section II')) throw new Error('note missing');
if (html.includes('Partial:')) throw new Error('status label leaked');
if (!html.includes('fr-stage-notice')) throw new Error('conflict notice missing');
const legacy = frApi().renderNormal({{stage3Markdown:'', priorities:[], riskExposure:{{}},
  ddChecklist:{{dd_checklist:[], dd_checklist_note:{json.dumps(rs.LEGACY_CHECKLIST_NOTE)}}}}});
if (legacy.includes('Due-Diligence Checklist')) throw new Error('legacy run should have no checklist');
if (!legacy.includes('not needed for this operation')) throw new Error('legacy note missing');
const none = frApi().renderNormal({{stage3Markdown:'', priorities:[], riskExposure:{{}}}});
if (none.includes('Due-Diligence Checklist') || none.includes('not needed for this operation')) throw new Error('saved sessions without the field should be unchanged');
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


def _download(extra):
    response = app.test_client().post("/api/download-report", json={
        "summary": "", "metadata": {},
        "priorities": [{"title": "Keep the route", "the_gap": "Gap.", "why_it_matters": "Why.", "actions": []}],
        **extra,
    })
    assert response.status_code == 200, response.get_data(as_text=True)
    document = Document(BytesIO(response.data))
    return "\n".join([p.text for p in document.paragraphs]
                     + [c.text for t in document.tables for r in t.rows for c in r.cells])


def test_word_export_carries_checklist_rows_and_legacy_note():
    body = _download(_dd_state())
    assert "Due-Diligence Checklist" in body
    assert "Have teams validated the FCV analysis" in body
    assert "see Section II" in body
    assert "Partial:" not in body
    assert "legacy-process operation" in body
    legacy = _download({"dd_checklist": [], "dd_checklist_note": rs.LEGACY_CHECKLIST_NOTE})
    assert "Due-Diligence Checklist" not in legacy
    assert "not needed for this operation" in legacy
    plain = _download({})
    assert "Due-Diligence Checklist" not in plain and "not needed for this operation" not in plain


def test_selector_has_no_default_and_offers_legacy_and_af_or_restructuring():
    from tests.test_climate_lens_frontend import INDEX
    html = INDEX.read_text(encoding="utf-8")
    start = html.index('id="review-stage"')
    select = html[start:html.index("</select>", start)]
    assert '<option value="" selected>' in select
    assert select.count(" selected") == 1
    for value in ("td", "ir", "one_review", "concept", "appraisal", "af_restructuring", "auto"):
        assert f'value="{value}"' in select
    assert "Additional Financing OR Restructuring" in select
    assert "review_stage:reviewStage" in html


# ── 2026-11-17: climate-route checklist, Snapshot label, responsiveness note ──

def test_climate_checklist_prompt_lists_column_ids_and_reader_digest():
    reader = {"assessment_themes": [{"title": "Fair benefits", "paragraphs": ["Hub selection is needs-based."]}],
              "priorities": [{"rank": 1, "title": "Screen facility siting"}]}
    prompt = rs.climate_checklist_prompt("td", reader)
    assert '"dd_checklist"' in prompt and '"context_td"' in prompt and "_ir\"" not in prompt
    assert "Screen facility siting" in prompt and "Hub selection is needs-based." in prompt
    assert rs.climate_checklist_prompt(None, reader) == ""


def test_climate_done_fields_call_once_for_new_model_and_skip_legacy():
    from app import climate_review_stage_done_fields
    calls = []

    def fake(prompt):
        calls.append(prompt)
        return 'Sure: {"dd_checklist": [{"question_id": "context_td", "note": "Partial: The Overview flags no RRA."}]}'

    done = climate_review_stage_done_fields({}, "td", {"preparation_regime": "unresolved_policy_source"}, "design", call=fake)
    assert len(calls) == 1
    assert [r["question_id"] for r in done["dd_checklist"]] == ["context_td"]
    assert done["dd_checklist"][0]["note"] == "The Overview flags no RRA."
    assert done["dd_checklist_column"] == "Technical Design review"

    legacy = climate_review_stage_done_fields({}, "concept", {}, "design", call=fake)
    assert len(calls) == 1 and legacy["dd_checklist"] == []
    assert legacy["dd_checklist_note"] == rs.LEGACY_CHECKLIST_NOTE


def test_climate_done_fields_omit_checklist_when_the_call_fails():
    from app import climate_review_stage_done_fields

    def broken(prompt):
        raise RuntimeError("provider down")

    done = climate_review_stage_done_fields({}, "ir", {}, "design", call=broken)
    assert done["dd_checklist"] == [] and done["dd_checklist_note"] == ""


def test_climate_readout_renders_checklist_snapshot_and_responsiveness_note():
    from tests.test_fcv_readout import CLIMATE_READER, climate
    state = _dd_state()
    html = climate(CLIMATE_READER, {"draftingAllowed": True, "noticesHtml": "", "ddChecklist": state})
    assert "Due-Diligence Checklist" in html and "Have teams validated the FCV analysis" in html
    assert "<strong>Snapshot:</strong>" in html
    assert "Responsiveness is not required of every project." in html
    plain = climate(CLIMATE_READER)
    assert "Due-Diligence Checklist" not in plain


def test_climate_word_carries_checklist_and_responsiveness_intro():
    from sector_lenses.climate_verified_render import (
        build_reader_model,
        write_reader_docx,
    )
    reader = build_reader_model({"judgments": {"sensitivity": {"value": "moderate", "rationale": "Design fits. More detail."},
                                               "responsiveness": {"value": "moderate", "rationale": "Some dividends. Detail."}}})
    stream = BytesIO()
    write_reader_docx(reader, stream, dd=_dd_state())
    stream.seek(0)
    document = Document(stream)
    text = "\n".join([p.text for p in document.paragraphs]
                     + [c.text for t in document.tables for r in t.rows for c in r.cells])
    assert "Due-Diligence Checklist" in text and "see Section II" in text
    assert "Responsiveness is not required of every project." in text
    assert "Snapshot: " in text


def test_normal_word_scorecard_and_responsiveness_intro():
    body = _download({"sensitivity_summary": "Design fits the context. More detail.",
                      "responsiveness_summary": "It engages two drivers. More detail."})
    assert "Snapshot: Design fits the context." in body
    assert "Responsiveness is not required of every project." in body
