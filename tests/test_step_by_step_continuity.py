"""Offline regressions for the three Step-by-Step handover findings."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app


S1 = "Project extraction: retained source fact.\n%%%DOC_TYPE: PAD%%%"
S2 = "Independent Stage 2 findings."


@pytest.fixture
def stream(monkeypatch):
    calls = []

    def fake(messages, max_tokens, stage, **kwargs):
        calls.append((stage, messages))
        fake._last_result = {1: S1, 2: S2, 3: "Recommendations."}[stage]
        fake._last_stop_reason = "end_turn"
        yield 'data: {"chunk":"offline"}\n\n'

    def research(*args, **kwargs):
        yield {"result": {"core_brief": "", "climate_research": {},
                          "lens_context_sources": [], "climate_grounding": {}}}

    monkeypatch.setattr(app, "_stream_stage", fake)
    monkeypatch.setattr(app, "_iter_stage1_research", research)
    monkeypatch.setattr(app, "get_fast_client", lambda: object())
    monkeypatch.setattr(app, "extract_country_name", lambda *args: "Honduras")
    monkeypatch.setattr(app, "extract_sector_name", lambda *args: "Transport")
    return calls


def run(stage, history=None, **extra):
    response = app.app.test_client().post("/api/run-stage", json={
        "stage": stage, "history": history or [], "active_lenses": [],
        "instrument_type": "IPF", "document_type": "Unknown",
        "doc_type": "Unknown", **extra,
    })
    assert response.status_code == 200
    events = [json.loads(line[6:]) for line in response.get_data(as_text=True).splitlines()
              if line.startswith("data: ")]
    assert not [e for e in events if e.get("error")], events
    return next(e for e in events if e.get("done"))


def history():
    return [{"role": "user", "content": "[Stage 1 - project documents analysed]"},
            {"role": "assistant", "content": S1}]


def test_real_stage_outputs_survive_stage2_and_reach_stage3(stream):
    second = run(2, history())
    assert [m["content"] for m in second["history"] if m["role"] == "assistant"] == [S1, S2]
    run(3, second["history"])
    context = stream[-1][1][0]["content"]
    assert S1 in context and S2 in context
    assert "Stage 1 output:\nUnderstood" not in context


def test_legacy_stage2_history_recovers_embedded_stage1(stream):
    old = [{"role": "user", "content": "Prior FCV analysis context:\n\nStage 1 output:\n"
            + S1 + "\n\nUse this as the basis for the next stage."},
           {"role": "assistant", "content": "Understood. I will build on this prior analysis."},
           {"role": "user", "content": "[Stage 2 - analysis prompt with operational guidance injected]"},
           {"role": "assistant", "content": S2}]
    run(3, old)
    assert S1 in stream[-1][1][0]["content"]


@pytest.mark.parametrize("stage", [2, 3])
@pytest.mark.parametrize("mode", ["design", "implementation"])
def test_refine_completes_without_missing_context(stream, stage, mode):
    done = run(stage, history(), user_message="Clarify delivery risks.", review_mode=mode)
    assert done["done"] is True
    assert S1 in [m["content"] for m in done["history"]]


def test_stage1_returns_detected_document_type(stream):
    done = run(1, documents=[{"name": "project.txt", "type": "text",
                            "content": "Project Appraisal Document. " * 30}])
    assert done["doc_type"] == "PAD"


def test_unknown_document_type_recovered_from_history(stream, monkeypatch):
    seen = []
    original = app.build_doc_type_context
    monkeypatch.setattr(app, "build_doc_type_context",
                        lambda doc, stage: (seen.append(doc), original(doc, stage))[1])
    run(2, history())
    assert seen == ["PAD"]


def test_explicit_document_type_takes_precedence(stream, monkeypatch):
    seen = []
    monkeypatch.setattr(app, "build_doc_type_context",
                        lambda doc, stage: seen.append(doc) or "")
    run(2, history(), document_type="AF")
    assert seen == ["AF"]


def test_refine_replaces_current_output_without_duplicate_stages(stream):
    second = run(2, history())
    refined = run(2, second["history"], user_message="Clarify delivery risks.")
    assert [m["content"] for m in refined["history"] if m["role"] == "assistant"] == [S1, S2]
    assert S2 in stream[-1][1][0]["content"]


def test_legacy_recovery_preserves_internal_section_separators():
    original = S1 + "\n\n---\n\nFurther evidence."
    old = [{"role": "user", "content": "Prior FCV analysis context:\n\nStage 1 output:\n"
            + original + "\n\nUse this as the basis for the next stage."},
           {"role": "assistant", "content": "Understood. I will build on this prior analysis."}]
    assert app._prior_stage_outputs(old) == {1: original}


def test_history_does_not_relabel_missing_stage1_as_stage2():
    old = [{"role": "user", "content": "Prior FCV analysis context:\n\nStage 1 output:\n"
            "Understood. I will build on this prior analysis.\n\n---\n\nStage 2 output:\n"
            + S2 + "\n\nUse this as the basis for the next stage."},
           {"role": "assistant", "content": "Understood. I will build on this prior analysis."}]
    assert app._prior_stage_outputs(old) == {2: S2}
    assert app._doc_type_from_history(old) == "Unknown"


def test_saved_history_keeps_complete_output_beyond_prompt_cap(stream):
    old = history()
    old[1]["content"] = S1 + "x" * 41000 + "%%%END%%%"
    done = run(2, old)
    assert done["history"][1]["content"] == old[1]["content"]


@pytest.mark.parametrize("payload", [
    {"doc_type": "PAD", "result": "Cleaned project analysis without delimiters."},
    {"result": "%%%DOC_TYPE: PAD%%%"},
    {"doc_type": "Unknown", "result": "%%%DOC_TYPE: PAD%%%"},
])
def test_step_completion_browser_uses_document_type_field(payload):
    source = (Path(app.__file__).parent / "index.html").read_text(encoding="utf-8")
    code = source.split("// Stage 1: extract docType + research data", 1)[1]
    code = code.split("if(stage===1){", 1)[1].split("if(p.research_brief)", 1)[0]
    script = "const p=" + json.dumps(payload) + ";let docType='Unknown';"
    script += "function updateDocTypeBadge(){}\n" + code
    script += "\nprocess.stdout.write(docType);"
    result = subprocess.run([shutil.which("node") or "C:/Program Files/nodejs/node.exe", "-e", script],
                            capture_output=True, text=True, check=True)
    assert result.stdout == "PAD"
