from sector_lenses.climate_run_manifest import (
    RunManifest,
    build_cache_key,
    safe_log_summary,
)


def test_cache_key_changes_with_authoritative_dependency():
    base = {
        "source_fingerprints": ("doc-a",),
        "schema_version": "climate-verified-v2",
        "prompt_version": "facts-v1",
        "reviewer_version": "review-v1",
        "model_alias": "assessment",
        "applicability_fingerprint": "verified-primary",
    }
    first = build_cache_key(**base)
    changed = build_cache_key(**{**base, "prompt_version": "facts-v2"})
    assert first != changed


def test_safe_log_summary_excludes_project_text_and_prompts():
    manifest = RunManifest(
        run_id="run-123",
        schema_version="climate-verified-v2",
        prompt_versions={"facts": "facts-v1"},
        reviewer_version="review-v1",
        extraction_version="blocks-v1",
        normalization_version="normalize-v1",
        renderer_version="renderer-v1",
        model_aliases={"facts": "assessment"},
        sampling={"temperature": 0},
        source_fingerprints=("sha-a",),
        applicability_fingerprint="app-a",
        bank_release_id="ssd-2026-08",
        live_research_timestamps=(),
        validation_reason_codes=("FACT_SOURCE_UNRESOLVED",),
        repair_actions=("normalize_enums",),
        suppressed_counts={"recommendations": 1},
        latency_ms={"facts": 1200},
        token_usage={"facts": 5000},
        cache_state={"facts": "miss"},
    )
    summary = safe_log_summary(manifest)
    serialized = str(summary)
    assert "project_text" not in serialized
    assert "supporting_excerpt" not in serialized
    assert summary["run_id"] == "run-123"
    assert summary["validation_reason_codes"] == [
        "FACT_SOURCE_UNRESOLVED"
    ]
