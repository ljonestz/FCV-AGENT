"""Offline fixture checks; these do not measure model semantic performance."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/climate/source_scope_calibration.json"


def test_scope_pairs_use_existing_offline_harness_without_label_leakage(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "scope_calibration", ROOT / "scripts/20261015_climate_reviewer_check.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fixture = module.load_fixture(FIXTURE)
    report = module.run_checks(fixture_path=FIXTURE, output_dir=tmp_path)
    assert report["mode"] == "offline"
    assert report["coverage"] == {
        "cases": 4, "conditional_review": 2, "reader_review": 2,
    }
    assert list(tmp_path.iterdir()) == []
    for case in fixture["cases"]:
        prompt = module.render_case_prompt(case)
        assert case["case_id"] not in prompt
        assert case["adjudication"] not in prompt
        assert json.dumps(case["expected"], sort_keys=True) not in prompt
        assert "synthetic_counterfactual" not in prompt


def test_scope_pairs_hold_claims_constant_and_change_documented_provision():
    cases = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]
    broad, explicit, general, targeted = cases
    assert [case["expected"]["accepted"] for case in cases] == [True, False, False, True]
    assert broad["payload"]["recommendations"] == explicit["payload"]["recommendations"]
    assert general["payload"]["final_reader"] == targeted["payload"]["final_reader"]
    assert broad["payload"]["source_blocks"] != explicit["payload"]["source_blocks"]
    assert general["payload"]["support_records"] != targeted["payload"]["support_records"]
    assert "registered traders from the cancelled market" in explicit["payload"]["source_blocks"][0]["text"]
    assert "to prevent their exclusion" in targeted["payload"]["source_passages"][0]["text"]
