# Project Climate Profile and Bank Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Use `superpowers:test-driven-development` for every code change and `superpowers:verification-before-completion` before each completion claim. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert extracted project text into a bounded deterministic climate profile, select a balanced project-specific bank packet, and preserve useful geography, system, uncertainty, and relevance metadata within the existing 6,000-character limit.

**Architecture:** The loader projects runtime schemas 1.0 and 1.1 into one internal record shape. A local profile extractor uses controlled aliases and explicit text matches only. A coverage-aware selector scores canonical records against the profile, applies balance, source-diversity, duplicate, and staleness rules, and returns IDs plus safe diagnostics. Materialization produces compact capsules but does not automatically inflate a selected pathway with every supporting evidence statement.

**Tech Stack:** Python 3.13, Flask, stdlib `dataclasses`/`json`/`re`/`datetime`, pytest.

**Depends on:** Approved redesign spec and Plan 1 schema contract. Real South Sudan 1.1 approval is not required: this plan uses synthetic 1.1 fixtures while retaining production compatibility with 1.0.

**Unchanged limits:** target 8 items, hard maximum 12 items, hard bank maximum 6,000 characters, no provider call, no confidential project text in logs.

---

## File Map

- Modify `sector_lenses/climate_bank.py`: dual-version loading, internal projection, and non-inflating materialization.
- Create `sector_lenses/climate_project_profile.py`: deterministic profile extraction and controlled aliases.
- Modify `sector_lenses/climate_bank_selector.py`: structured matching, balance, diversity, staleness, deduplication, and diagnostics.
- Modify `sector_lenses/climate_grounding.py`: richer evidence/pathway capsules and accurate selection counts.
- Modify `sector_lenses/__init__.py`: export new contracts.
- Modify `app.py`: build the profile once, pass it to selection and research, persist only safe metadata, and improve count telemetry.
- Create `tests/fixtures/climate_bank/runtime_v1_1.json`.
- Create `tests/fixtures/climate_projects/*.txt` and matching expected profile JSON files for five archetypes.
- Modify `tests/test_climate_bank.py`, `tests/test_climate_bank_selector.py`, `tests/test_climate_bank_selector_realistic.py`, `tests/test_climate_grounding.py`, and `tests/test_climate_workflow_contract.py`.
- Create `tests/test_climate_project_profile.py`.
- Modify `README.md` and the private dual-build parity log after contracts settle.

## Internal Project Profile

```python
@dataclass(frozen=True)
class ProjectClimateProfile:
    country: str
    instrument: str
    document_stage: str
    geographies: tuple[str, ...]
    sectors: tuple[str, ...]
    project_elements: tuple[str, ...]
    affected_groups: tuple[str, ...]
    institutions: tuple[str, ...]
    systems_assets: tuple[str, ...]
    documented_hazards: tuple[str, ...]
    time_horizons: tuple[str, ...]
    signal_metadata: tuple[SignalMatch, ...]
    unresolved: tuple[str, ...]
```

`SignalMatch` contains `field`, `canonical_value`, `matched_text`, `source`, and `confidence`. `source` is one of `document-explicit`, `document-metadata`, or `bank-candidate`. Only the first two may populate explicit project facts; `bank-candidate` is retained separately for research planning.

## Selection Result

```python
{
  "bank_status": "ok",
  "schema_version": "1.1.0",
  "content_version": "2026.08.south-sudan-v2",
  "country_iso3": "SSD",
  "evidence_ids": ["SSD-E-021", "SSD-E-034"],
  "pathway_ids": ["SSD-P-003"],
  "diagnostics": {
    "selected": [
      {"id": "SSD-E-021", "score": 28, "matched_fields": ["geographies", "sectors"], "balance_role": "climate-pressure"}
    ],
    "suppressed": [],
    "missing_classes": ["response-performance"]
  }
}
```

Diagnostics contain controlled field names, IDs, counts, and reason codes only. They never contain the original document text or `matched_text`.

### Task 1: Add dual-version loader projection

**Files:**
- Modify `sector_lenses/climate_bank.py`
- Create `tests/fixtures/climate_bank/runtime_v1_1.json`
- Modify `tests/test_climate_bank.py`

- [ ] **Step 1: Write failing compatibility tests**

```python
@pytest.mark.parametrize("fixture_name", ["runtime_v1.json", "runtime_v1_1.json"])
def test_loader_accepts_supported_schema_versions(fixture_name):
    bank = load_climate_bank(FIXTURES / fixture_name)
    assert bank["schema_version"] in {"1.0.0", "1.1.0"}
    assert all("evidence_class" in record for record in bank["evidence"])
    assert "selection_aliases" in bank["countries"]["SSD"]


def test_v1_projection_sets_compatibility_defaults():
    bank = load_climate_bank(FIXTURES / "runtime_v1.json")
    record = bank["evidence"][0]
    assert record["evidence_class"] in EVIDENCE_CLASSES
    assert record["administrative_level"] == "not-applicable"
    assert record["refresh_tier"] == "structural"
    assert record["review_due"] is None


def test_loader_rejects_unsupported_minor_version(tmp_path):
    path = write_runtime(tmp_path, schema_version="1.2.0")
    with pytest.raises(ClimateBankError, match="unsupported schema_version"):
        load_climate_bank(path)
```

- [ ] **Step 2: Run the tests and confirm failure**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_bank.py
```

- [ ] **Step 3: Implement explicit version adapters**

```python
SUPPORTED_CLIMATE_BANK_SCHEMA_VERSIONS = {"1.0.0", "1.1.0"}

V1_ROLE_TO_CLASS = {
    "physical-baseline": "climate-pressure",
    "vulnerability-capacity": "sensitivity",
    "direct-climate-fcv": "direct-climate-fcv",
}

def _project_evidence_record(record: dict, schema_version: str) -> dict:
    projected = dict(record)
    if schema_version == "1.0.0":
        projected.update({
            "evidence_class": V1_ROLE_TO_CLASS[record["analytical_role"]],
            "administrative_level": "not-applicable",
            "ecological_level": None,
            "refresh_tier": "structural",
            "review_due": None,
        })
    return projected
```

The compatibility mapping is intentionally conservative. It does not claim that old `vulnerability-capacity` records distinguish sensitivity from capacity.

- [ ] **Step 4: Verify and commit**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_bank.py
git add sector_lenses/climate_bank.py tests/fixtures/climate_bank/runtime_v1_1.json tests/test_climate_bank.py
git commit -m "feat: support climate bank schema 1.1"
```

### Task 2: Build the deterministic Project Climate Profile

**Files:**
- Create `sector_lenses/climate_project_profile.py`
- Create `tests/test_climate_project_profile.py`
- Create five synthetic fixture text files and expected JSON profiles under `tests/fixtures/climate_projects/`

- [ ] **Step 1: Write five archetype tests before the extractor**

```python
@pytest.mark.parametrize("slug", [
    "agriculture_livestock",
    "fisheries_forestry_nrm",
    "roads_infrastructure",
    "health_wash",
    "social_protection_resilience",
])
def test_golden_project_profile(slug, bank_alias_catalog):
    text = (FIXTURES / f"{slug}.txt").read_text(encoding="utf-8")
    expected = json.loads((FIXTURES / f"{slug}.json").read_text(encoding="utf-8"))
    profile = build_project_climate_profile(
        text,
        country="South Sudan",
        instrument="IPF",
        document_stage="PCN",
        alias_catalog=bank_alias_catalog,
    )
    assert profile.to_public_dict() == expected
```

Each fixture must name different states/counties, components, groups, institutions, assets, and hazards. Use synthetic text only; no confidential project text.

- [ ] **Step 2: Add negative tests against inference and false matches**

```python
def test_extractor_does_not_add_unmentioned_geography(bank_alias_catalog):
    profile = build_project_climate_profile("National agriculture support project", country="South Sudan", alias_catalog=bank_alias_catalog)
    assert profile.geographies == ()


def test_bank_candidate_hazard_is_not_documented_hazard(bank_alias_catalog):
    profile = build_project_climate_profile("Community forestry in Western Equatoria", country="South Sudan", alias_catalog=bank_alias_catalog)
    assert "flooding" not in profile.documented_hazards


def test_word_boundaries_prevent_short_alias_false_match(bank_alias_catalog):
    profile = build_project_climate_profile("The road component includes drainage works.", country="South Sudan", alias_catalog=bank_alias_catalog)
    assert "rain" not in profile.documented_hazards
```

- [ ] **Step 3: Confirm failures**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_project_profile.py
```

- [ ] **Step 4: Implement normalized aliases and bounded extraction**

Use the reviewed `selection_aliases` projected from the runtime release, plus minimal schema-level generic aliases. Do not hard-code an independent South Sudan gazetteer in the app. Apply Unicode normalization, casefolding, word-boundary regexes, longest-alias-first matching, and stable output sorting. Limit each list to 12 values, `project_elements` to 16, and total serialized public profile to 4,000 characters by dropping lowest-confidence `bank-candidate` signals first.

```python
FIELD_LIMITS = {
    "geographies": 12, "sectors": 12, "project_elements": 16,
    "affected_groups": 12, "institutions": 12, "systems_assets": 12,
    "documented_hazards": 8, "time_horizons": 6,
}

def _match_aliases(text: str, aliases: dict[str, tuple[str, ...]], field: str) -> list[SignalMatch]:
    matches = []
    for canonical, variants in sorted(aliases.items()):
        for variant in sorted(variants, key=len, reverse=True):
            if re.search(rf"(?<!\w){re.escape(variant.casefold())}(?!\w)", text):
                matches.append(SignalMatch(field, canonical, variant, "document-explicit", "high"))
                break
    return matches
```

Component extraction recognizes numbered headings and verbs such as rehabilitate, construct, strengthen, finance, establish, support, and restore, but stores the bounded matched heading/phrase rather than inventing a standardized component.

- [ ] **Step 5: Run deterministic and privacy tests**

```python
def test_profile_is_deterministic(golden_text, bank_alias_catalog):
    first = build_project_climate_profile(golden_text, country="South Sudan", alias_catalog=bank_alias_catalog).to_json()
    second = build_project_climate_profile(golden_text, country="South Sudan", alias_catalog=bank_alias_catalog).to_json()
    assert first == second


def test_profile_logger_emits_counts_not_text(caplog, golden_text, bank_alias_catalog):
    profile = build_project_climate_profile(golden_text, country="South Sudan", alias_catalog=bank_alias_catalog)
    log_project_climate_profile("assessment-1", profile)
    assert golden_text not in caplog.text
    assert "geographies=" in caplog.text
```

- [ ] **Step 6: Verify and commit**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_project_profile.py
git add sector_lenses/climate_project_profile.py tests/test_climate_project_profile.py tests/fixtures/climate_projects
git commit -m "feat: extract bounded project climate profiles"
```

### Task 3: Replace excerpt scoring with structured coverage-aware selection

**Files:**
- Modify `sector_lenses/climate_bank_selector.py`
- Modify `tests/test_climate_bank_selector.py`
- Modify `tests/test_climate_bank_selector_realistic.py`

- [ ] **Step 1: Write failing structured-score tests**

```python
def test_geography_and_project_element_outweigh_generic_hazard(bank_v1_1, fisheries_profile):
    result = select_climate_bank_packet(bank_v1_1, country="South Sudan", project_profile=fisheries_profile)
    selected = result["diagnostics"]["selected"]
    local = next(row for row in selected if row["id"] == "SSD-E-021")
    national = next(row for row in selected if row["id"] == "SSD-E-003")
    assert local["score"] > national["score"]


def test_selector_balances_classes_when_relevant(bank_v1_1, agriculture_profile):
    result = select_climate_bank_packet(bank_v1_1, country="South Sudan", project_profile=agriculture_profile)
    roles = {row["balance_role"] for row in result["diagnostics"]["selected"]}
    assert {"climate-pressure", "vulnerability-capacity", "institution-response", "climate-to-fcv-pathway"} <= roles


def test_selector_reports_missing_class_instead_of_filling_irrelevant_item(bank_v1_1, roads_profile):
    result = select_climate_bank_packet(bank_v1_1, country="South Sudan", project_profile=roads_profile)
    assert "response-performance" in result["diagnostics"]["missing_classes"]
    assert len(result["evidence_ids"]) + len(result["pathway_ids"]) <= CLIMATE_BANK_TARGET_ITEMS
```

- [ ] **Step 2: Add diversity, staleness, and deduplication tests**

```python
def test_source_diversity_uses_all_supporting_sources(bank_v1_1, profile):
    result = select_climate_bank_packet(bank_v1_1, country="South Sudan", project_profile=profile)
    source_counts = supporting_source_counts(result, bank_v1_1)
    assert max(source_counts.values(), default=0) <= 3


def test_stale_current_record_loses_to_reviewed_equivalent(bank_v1_1, profile):
    result = select_climate_bank_packet(bank_v1_1, country="South Sudan", project_profile=profile, as_of=date(2026, 8, 1))
    assert "SSD-E-099" not in result["evidence_ids"]
    assert any(row["id"] == "SSD-E-099" and row["reason"] == "stale_current" for row in result["diagnostics"]["suppressed"])


def test_near_duplicate_is_suppressed(bank_v1_1, profile):
    result = select_climate_bank_packet(bank_v1_1, country="South Sudan", project_profile=profile)
    assert any(row["reason"] == "near_duplicate" for row in result["diagnostics"]["suppressed"])
```

- [ ] **Step 3: Confirm failures**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_bank_selector.py tests/test_climate_bank_selector_realistic.py
```

- [ ] **Step 4: Implement weights and balance slots**

```python
MATCH_WEIGHTS = {
    "geographies": 12,
    "project_elements": 10,
    "sectors": 8,
    "affected_groups": 7,
    "institutions": 7,
    "systems_assets": 7,
    "documented_hazards": 4,
    "time_horizons": 3,
}

BALANCE_SLOTS = (
    "climate-pressure",
    "vulnerability-capacity",
    "vulnerability-capacity",
    "institution-response",
    "climate-to-fcv-pathway",
    "reverse-or-bidirectional-pathway",
)
```

First select the highest relevant candidate for each supported slot, then add up to two highest-scoring distinct records. Do not select a candidate with a non-positive relevance score solely to fill a slot. Suppress near duplicates using normalized claim-token Jaccard similarity at a fixed threshold tested with fixtures, not embeddings.

- [ ] **Step 5: Bound and sanitize diagnostics**

Return at most 12 selected rows, 12 suppressed rows, and nine missing class strings. Scores are integers; reasons and field names are controlled enums. No document phrase or matched text enters diagnostics.

- [ ] **Step 6: Verify and commit**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_bank_selector.py tests/test_climate_bank_selector_realistic.py
git add sector_lenses/climate_bank_selector.py tests/test_climate_bank_selector.py tests/test_climate_bank_selector_realistic.py
git commit -m "feat: balance climate bank selection by project profile"
```

### Task 4: Materialize rich capsules without pathway inflation

**Files:**
- Modify `sector_lenses/climate_bank.py`
- Modify `sector_lenses/climate_grounding.py`
- Modify `tests/test_climate_bank.py`
- Modify `tests/test_climate_grounding.py`

- [ ] **Step 1: Write failing materialization-count and capsule tests**

```python
def test_pathway_support_does_not_inflate_selected_evidence(bank_v1_1):
    manifest = {"bank_status": "ok", "country_iso3": "SSD", "evidence_ids": ["SSD-E-021"], "pathway_ids": ["SSD-P-003"]}
    packet = materialize_bank_manifest(bank_v1_1, manifest)
    assert [row["evidence_id"] for row in packet["evidence"]] == ["SSD-E-021"]
    assert packet["pathways"][0]["supporting_evidence_ids"]


def test_evidence_capsule_preserves_reasoning_metadata(bank_packet, project_profile):
    context = compact_bank_context(bank_packet, project_profile)
    capsule = context["evidence"][0]
    assert set(capsule) == {"id", "class", "claim", "geographies", "groups_systems", "project_relevance", "status", "uncertainty", "source_ids"}


def test_compact_context_drops_whole_capsules_under_limit(oversized_packet, profile):
    context = compact_bank_context(oversized_packet, profile)
    serialized = serialize_bank_context(context)
    assert len(serialized) <= 6_000
    assert all(row["claim"] and row["uncertainty"] for row in context["evidence"])
```

- [ ] **Step 2: Confirm failures**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_bank.py tests/test_climate_grounding.py
```

- [ ] **Step 3: Stop automatic support-record expansion**

Materialize sources referenced by selected evidence and selected pathways' supporting evidence, but include full evidence statements only for IDs explicitly present in `manifest.evidence_ids`. This preserves traceability while reconciling the eight-item target with the prior log's 12 materialized items.

- [ ] **Step 4: Implement compact capsules and whole-item pruning**

`project_relevance` is generated deterministically from matched controlled fields, for example `"Matches geography and fisheries sector"`; it is not an LLM synthesis. Pathways retain pressure, mediator, possible consequence, geography/system, direction, strength, uncertainty, and support IDs.

Order pruning as: optional extra evidence, second vulnerability/capacity item, lowest-score pathway only if another pathway of the same direction remains. Never slice a claim or uncertainty string mid-sentence.

- [ ] **Step 5: Verify exact bounds and commit**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_bank.py tests/test_climate_grounding.py
git add sector_lenses/climate_bank.py sector_lenses/climate_grounding.py tests/test_climate_bank.py tests/test_climate_grounding.py
git commit -m "feat: preserve metadata in compact climate capsules"
```

### Task 5: Integrate one profile through both app workflows

**Files:**
- Modify `app.py`
- Modify `sector_lenses/__init__.py`
- Modify `tests/test_climate_workflow_contract.py`
- Modify relevant route tests that assert research-plan fields

- [ ] **Step 1: Write failing research-plan and manifest tests**

```python
def test_stage1_plan_builds_structured_climate_profile(project_doc_parts):
    plan = build_stage1_research_plan(["climate"], "South Sudan", "NRM", project_doc_parts)
    assert plan["project_profile"]["geographies"] == ["Jonglei", "Upper Nile"]
    assert "document_excerpt" not in plan["project_profile"]


def test_safe_manifest_retains_bounded_selection_diagnostics():
    safe = _safe_climate_bank_manifest(MANIFEST_WITH_DIAGNOSTICS)
    assert safe["diagnostics"]["missing_classes"] == ["response-performance"]
    assert "matched_text" not in json.dumps(safe)
```

- [ ] **Step 2: Confirm failure**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_workflow_contract.py
```

- [ ] **Step 3: Build the profile once in `build_stage1_research_plan`**

Load the bank through the existing cached loader and pass its reviewed country `selection_aliases` to the local extractor. If the bank is unavailable, use only minimal generic sector/hazard aliases and report unresolved geography rather than guessing. Keep the bounded raw excerpt only as an internal input to the local extractor; do not put it in the returned plan. Pass the public structured profile to `select_bank_manifest` and later to live research. Preserve instrument and document-stage metadata already detected by the app.

- [ ] **Step 4: Persist only safe profile and selection metadata**

The browser/server handoff may retain the bounded public profile and canonical manifest, but the server rematerializes bank content. Strip `signal_metadata.matched_text` before client serialization. Do not trust client-supplied evidence prose.

- [ ] **Step 5: Correct count telemetry**

Log both:

```text
manifest_items=<evidence_ids + pathway_ids>
materialized_items=<full evidence + pathway capsules>
```

Both must be at most 12 after the non-inflating materializer. Preserve the existing `bank_chars` metric and privacy behavior.

- [ ] **Step 6: Verify both routes and commit**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_workflow_contract.py tests/test_climate_bank_selector_realistic.py tests/test_climate_grounding.py
git add app.py sector_lenses/__init__.py tests/test_climate_workflow_contract.py
git commit -m "feat: use project climate profile in bank selection"
```

### Task 6: Run five-profile selection acceptance tests

**Files:**
- Create `tests/test_climate_selection_golden_profiles.py`
- Reuse the five fixture profiles

- [ ] **Step 1: Define contract expectations for each archetype**

```python
EXPECTED_TOPICS = {
    "agriculture_livestock": {"extreme-heat", "drought", "livestock-mobility"},
    "fisheries_forestry_nrm": {"riverine-flood", "wetlands", "resource-governance"},
    "roads_infrastructure": {"flood-exposure", "transport-access", "service-interruption"},
    "health_wash": {"flooding", "disease-risk", "service-access"},
    "social_protection_resilience": {"shock-response", "displacement", "coping-capacity"},
}
```

Assert supported topics are present or explicitly appear in `missing_classes`/gap diagnostics. Do not make tests pass by fabricating unsupported bank tags.

- [ ] **Step 2: Assert material differentiation**

```python
def test_golden_selections_are_materially_distinct(all_results):
    id_sets = [set(result["evidence_ids"] + result["pathway_ids"]) for result in all_results]
    for left, right in combinations(id_sets, 2):
        assert jaccard(left, right) < 0.75
```

- [ ] **Step 3: Assert bounds, causal labels, and determinism for every profile**

Each run stays at or below 12 items and 6,000 characters. Local evidence retains local geography and uncertainty. Repeating the same input returns byte-identical IDs, scores, diagnostics, and capsules.

- [ ] **Step 4: Run the suite and commit**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_selection_golden_profiles.py
git add tests/test_climate_selection_golden_profiles.py
git commit -m "test: cover five South Sudan project selections"
```

### Task 7: Document shared contracts and verify the increment

**Files:**
- Modify `README.md`
- Modify private `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md` only after reading it

- [ ] **Step 1: Classify parity surfaces**

Record schema 1.1 fields, profile JSON, diagnostic enums, and capsule fields as shared-contract decisions. Record Flask request persistence/logging as Render-specific. Never commit the private parity file.

- [ ] **Step 2: Run focused and full verification**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_bank.py tests/test_climate_project_profile.py tests/test_climate_bank_selector.py tests/test_climate_bank_selector_realistic.py tests/test_climate_grounding.py tests/test_climate_workflow_contract.py tests/test_climate_selection_golden_profiles.py
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
git diff --check
git status --short
```

- [ ] **Step 3: Commit documentation**

```powershell
git add README.md
git commit -m "docs: document project-aware climate bank selection"
```

---

## Plan 2 Definition of Done

- Both runtime schemas load into one conservative internal shape.
- Five project archetypes produce deterministic, materially different profiles and selections.
- Required evidence classes are covered when relevant or declared missing.
- Capsules preserve geography, groups/systems, status, uncertainty, relevance, and sources.
- Selected pathways no longer inflate the packet with unselected full evidence records.
- Bank context remains at or below 6,000 characters and 12 items.
- Logs contain only IDs, counts, scores, and controlled reason codes.
- Production remains compatible with the unchanged South Sudan 1.0 release.

## Next Plan

Implement `2026-08-01-climate-live-research-reliability.md` to convert selection gaps into a bounded research agenda and diagnose live-evidence rejection precisely.
