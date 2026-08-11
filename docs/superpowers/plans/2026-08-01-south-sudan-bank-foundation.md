# South Sudan Evidence Bank Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Use `superpowers:test-driven-development` for every code change and `superpowers:verification-before-completion` before each completion claim. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reviewable South Sudan schema-1.1 candidate bank and analytical dossier with systematic coverage, while leaving the currently approved 1.0 runtime release untouched until human approval.

**Architecture:** Candidate content lives under a versioned country candidate directory and is validated against the same canonical schemas as approved content. A reviewed `profile.json` supplies synthesis and a coverage matrix; canonical evidence and pathways remain atomic and source-traceable. The dossier generator combines profile synthesis with the technical register. Promotion is a separate, explicit operation that cannot run until the candidate review decision is `approved`.

**Tech Stack:** Python 3.13, JSON Schema Draft 2020-12, pytest, stdlib `json`/`pathlib`/`hashlib`, Markdown.

**Depends on:** Approved design `docs/superpowers/specs/2026-08-01-south-sudan-climate-bank-redesign.md` and companion repository commit `dd52305`.

**Safety boundary:** Do not modify `countries/SSD/*.json`, `countries/SSD/dossier.md`, or `releases/current/runtime.json` during candidate development. Do not commit source PDFs or long copyrighted extracts. Every claim must retain a precise source locator; short quotations may be used only where necessary and legally permissible.

---

## File Map

All companion-repository paths below are relative to `data/climate-fcv-country-bank/`.

- Create `schemas/profile.schema.json`: reviewed synthesis and coverage contract.
- Modify `schemas/evidence.schema.json`: schema-1.1 evidence fields and controlled values.
- Modify `schemas/runtime-release.schema.json`: accept a release version passed by the validator rather than hard-coding 1.0 only.
- Modify `climate_bank/validation.py`: validate canonical or candidate country directories, profile links, review windows, and projected-evidence requirements.
- Modify `scripts/validate_bank.py`: accept an explicit candidate directory and profile requirement.
- Modify `climate_bank/release.py`: build 1.1 candidates to an explicit output path and refuse promotion without approval.
- Modify `scripts/build_release.py`: expose candidate output and explicit promotion flags safely.
- Modify `climate_bank/dossier.py`: generate the redesigned dossier from reviewed synthesis plus canonical records.
- Modify `scripts/build_dossier.py`: accept an explicit candidate directory and deterministic check mode.
- Create `countries/SSD/candidates/2026.08/profile.json`.
- Create `countries/SSD/candidates/2026.08/sources.json`.
- Create `countries/SSD/candidates/2026.08/evidence.json`.
- Create `countries/SSD/candidates/2026.08/pathways.json`.
- Create `countries/SSD/candidates/2026.08/review.json`.
- Generate `countries/SSD/candidates/2026.08/dossier.md`.
- Create `tests/fixtures/profile.valid.json`.
- Modify `tests/test_validation.py`, `tests/test_release.py`, `tests/test_dossier.py`, `tests/test_south_sudan_content.py`, and `tests/test_repository_contract.py`.
- Modify companion `README.md` and `CLAUDE.md` to document candidate review and promotion.

## Runtime 1.1 Contracts

The expanded evidence object adds these required fields while retaining `analytical_role`:

```json
{
  "evidence_class": "adaptive-capacity",
  "administrative_level": "county",
  "ecological_level": null,
  "refresh_tier": "structural",
  "review_due": "2027-08-01"
}
```

Controlled values:

```python
EVIDENCE_CLASSES = {
    "climate-pressure", "exposure", "sensitivity", "coping-capacity",
    "adaptive-capacity", "institutional-capacity", "response-performance",
    "direct-climate-fcv", "resilience-peace-capacity",
}
REFRESH_TIERS = {"structural", "current"}
ADMIN_LEVELS = {"national", "state", "administrative-area", "county", "payam", "boma", "site", "cross-border", "not-applicable"}
```

`profile.json` stores reviewed synthesis and a reviewed selection alias catalog. Every synthesis statement names at least one evidence or pathway ID. Aliases may normalize explicit text matches but may not add a fact that is absent from a project document:

```json
{
  "iso3": "SSD",
  "profile_version": "2026.08",
  "executive_assessment": [{"text": "South Sudan evidence is strongest for current flood-related vulnerability and remains limited for quantified future impacts.", "evidence_ids": ["SSD-E-001"], "pathway_ids": []}],
  "coverage": [{"dimension": "evidence_class", "value": "climate-pressure", "status": "covered", "record_ids": ["SSD-E-001"], "gap_note": null}],
  "geographic_notes": [],
  "sector_notes": [],
  "known_gaps": [],
  "selection_aliases": {
    "geographies": {"Jonglei": ["Jonglei State"]},
    "sectors": {"livestock": ["pastoralism", "cattle keeping"]},
    "affected_groups": {"displaced people": ["IDPs", "internally displaced persons"]},
    "institutions": {},
    "systems_assets": {"wetlands": ["Sudd", "Sudd wetland"]},
    "hazards": {"riverine-flood": ["river flooding", "inundation"]}
  },
  "review_status": "reviewed",
  "review_date": "2026-08-01"
}
```

### Task 1: Isolate candidate work and record the baseline

**Files:**
- Modify git state only in `data/climate-fcv-country-bank/`
- No content files yet

- [ ] **Step 1: Verify both repositories are clean and record their heads**

```powershell
git status --short --branch
git -C data/climate-fcv-country-bank status --short --branch
git rev-parse HEAD
git -C data/climate-fcv-country-bank rev-parse HEAD
```

Expected: parent is `feat/climate-country-bank`; companion is clean at `dd52305` or its documented successor.

- [ ] **Step 2: Create the companion feature branch**

```powershell
git -C data/climate-fcv-country-bank switch -c feat/south-sudan-bank-v2
```

- [ ] **Step 3: Run the companion baseline tests**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider data/climate-fcv-country-bank/tests
```

Expected: all baseline tests pass. Record the count in the implementation log before changing schemas.

### Task 2: Add the profile schema and candidate-directory validation

**Files:**
- Create `data/climate-fcv-country-bank/schemas/profile.schema.json`
- Modify `data/climate-fcv-country-bank/climate_bank/validation.py`
- Modify `data/climate-fcv-country-bank/scripts/validate_bank.py`
- Create `data/climate-fcv-country-bank/tests/fixtures/profile.valid.json`
- Modify `data/climate-fcv-country-bank/tests/test_validation.py`

- [ ] **Step 1: Write failing tests for profile references and alternate country directories**

```python
def test_validate_country_directory_accepts_reviewed_profile(tmp_path, valid_country):
    profile = json.loads((FIXTURES / "profile.valid.json").read_text())
    (valid_country / "profile.json").write_text(json.dumps(profile), encoding="utf-8")
    assert validate_country_directory(valid_country) == []


def test_profile_rejects_unknown_evidence_reference(tmp_path, valid_country):
    profile = json.loads((FIXTURES / "profile.valid.json").read_text())
    profile["executive_assessment"][0]["evidence_ids"] = ["SSD-E-999"]
    (valid_country / "profile.json").write_text(json.dumps(profile), encoding="utf-8")
    errors = validate_country_directory(valid_country)
    assert any("SSD-E-999" in error and "profile" in error for error in errors)


def test_candidate_directory_requires_profile():
    errors = validate_country_directory(CANDIDATE_DIR, require_profile=True)
    assert any("profile.json" in error for error in errors)
```

- [ ] **Step 2: Run the focused tests and confirm failure**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider data/climate-fcv-country-bank/tests/test_validation.py
```

Expected: failures because `profile.schema.json` and `validate_country_directory` do not exist.

- [ ] **Step 3: Implement the profile schema and parameterized validator**

Add `profile.json` to validation only when `require_profile=True` or the file exists. Resolve all referenced IDs against the directory being validated, not against canonical `countries/SSD/`.

```python
def validate_country_directory(
    country_dir: Path,
    *,
    require_profile: bool = False,
) -> list[str]:
    filenames = ["sources.json", "evidence.json", "pathways.json", "review.json"]
    if require_profile or (country_dir / "profile.json").exists():
        filenames.append("profile.json")
    documents = {name: _load_json(country_dir / name) for name in filenames}
    errors = _validate_documents(documents)
    errors.extend(_validate_cross_links(documents))
    return errors
```

- [ ] **Step 4: Run focused and full companion tests**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider data/climate-fcv-country-bank/tests/test_validation.py
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider data/climate-fcv-country-bank/tests
```

- [ ] **Step 5: Commit the profile-validation contract**

```powershell
git -C data/climate-fcv-country-bank add schemas/profile.schema.json climate_bank/validation.py scripts/validate_bank.py tests/fixtures/profile.valid.json tests/test_validation.py
git -C data/climate-fcv-country-bank commit -m "feat: add reviewed country profile contract"
```

### Task 3: Expand evidence schema to 1.1 without weakening 1.0 validation

**Files:**
- Modify `data/climate-fcv-country-bank/schemas/evidence.schema.json`
- Modify `data/climate-fcv-country-bank/climate_bank/validation.py`
- Modify `data/climate-fcv-country-bank/scripts/validate_bank.py`
- Modify `data/climate-fcv-country-bank/tests/test_validation.py`

- [ ] **Step 1: Write failing tests for new fields and semantic rules**

```python
@pytest.mark.parametrize("evidence_class", sorted(EVIDENCE_CLASSES))
def test_schema_accepts_each_evidence_class(valid_evidence, evidence_class):
    valid_evidence.update({
        "evidence_class": evidence_class,
        "administrative_level": "national",
        "ecological_level": None,
        "refresh_tier": "structural",
        "review_due": "2027-08-01",
    })
    assert validate_evidence_document([valid_evidence], schema_version="1.1.0") == []


def test_projected_record_requires_scenario_and_future_horizon(valid_evidence):
    valid_evidence.update({"evidence_status": "projected", "scenario": None, "time_horizons": ["current"]})
    errors = validate_evidence_document([valid_evidence], schema_version="1.1.0")
    assert any("projected" in error and "scenario" in error for error in errors)


def test_current_record_review_due_cannot_precede_review_date(valid_evidence):
    valid_evidence.update({"refresh_tier": "current", "review_date": "2026-08-01", "review_due": "2026-07-31"})
    errors = validate_evidence_document([valid_evidence], schema_version="1.1.0")
    assert any("review_due" in error for error in errors)
```

- [ ] **Step 2: Confirm the tests fail**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider data/climate-fcv-country-bank/tests/test_validation.py
```

- [ ] **Step 3: Add fields, enums, and semantic validation**

Keep the JSON schema strict with `additionalProperties: false`. The validator accepts a `schema_version` so 1.0 canonical content remains valid during migration; 1.1 content requires all new fields. Reject projected records without `near-term`, `medium-term`, or `long-term`, and without a non-null scenario.

- [ ] **Step 4: Add staleness reporting without deleting records**

```python
def review_state(record: dict, *, as_of: date) -> str:
    due = date.fromisoformat(record["review_due"])
    if record["refresh_tier"] == "current" and due < as_of:
        return "stale"
    return record["review_status"]
```

Validation reports stale approved/current records as release-blocking errors for 1.1 candidates. Structural records remain subject to their explicit annual review window.

- [ ] **Step 5: Run tests and commit**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider data/climate-fcv-country-bank/tests/test_validation.py
git -C data/climate-fcv-country-bank add schemas/evidence.schema.json climate_bank/validation.py tests/test_validation.py
git -C data/climate-fcv-country-bank commit -m "feat: add climate evidence schema 1.1 fields"
```

### Task 4: Add safe candidate release building and promotion refusal

**Files:**
- Modify `data/climate-fcv-country-bank/schemas/runtime-release.schema.json`
- Modify `data/climate-fcv-country-bank/climate_bank/release.py`
- Modify `data/climate-fcv-country-bank/scripts/build_release.py`
- Modify `data/climate-fcv-country-bank/tests/test_release.py`

- [ ] **Step 1: Write failing release tests**

```python
def test_build_candidate_uses_explicit_input_and_output(tmp_path, candidate_country):
    output = tmp_path / "runtime.json"
    release = build_release([candidate_country], output_path=output, schema_version="1.1.0")
    assert output.exists()
    assert release["schema_version"] == "1.1.0"


def test_promotion_refuses_reviewed_candidate(tmp_path, candidate_country):
    candidate_country.joinpath("review.json").write_text(REVIEWED_REVIEW, encoding="utf-8")
    with pytest.raises(ReleaseError, match="approved"):
        promote_release(candidate_country, current_dir=tmp_path / "current")


def test_candidate_build_does_not_modify_current_release(candidate_country):
    before = CURRENT_RUNTIME.read_bytes()
    build_release([candidate_country], output_path=candidate_country / "runtime.preview.json", schema_version="1.1.0")
    assert CURRENT_RUNTIME.read_bytes() == before
```

- [ ] **Step 2: Confirm the tests fail**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider data/climate-fcv-country-bank/tests/test_release.py
```

- [ ] **Step 3: Implement explicit candidate output and approval gate**

`build_release` may create a preview from `reviewed` records for testing, but must label it `candidate: true` and must never write to `releases/current`. Runtime 1.1 embeds the reviewed `selection_aliases` in the country entry so local project profiling uses the same controlled vocabulary as the bank. `promote_release` accepts only an approved country review and approved records/pathways/profile, then writes a deterministic release and checksums.

- [ ] **Step 4: Verify and commit**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider data/climate-fcv-country-bank/tests/test_release.py data/climate-fcv-country-bank/tests/test_repository_contract.py
git -C data/climate-fcv-country-bank add schemas/runtime-release.schema.json climate_bank/release.py scripts/build_release.py tests/test_release.py tests/test_repository_contract.py
git -C data/climate-fcv-country-bank commit -m "feat: separate candidate build from release promotion"
```

### Task 5: Build the South Sudan coverage matrix before adding records

**Files:**
- Create `data/climate-fcv-country-bank/countries/SSD/candidates/2026.08/profile.json`
- Create candidate copies of the four canonical ledgers in the same directory
- Modify `data/climate-fcv-country-bank/tests/test_south_sudan_content.py`

- [ ] **Step 1: Seed candidate ledgers from the approved source without modifying it**

Use file copies through the repository-native implementation script or PowerShell `Copy-Item`; preserve IDs and approved provenance. The candidate review becomes `reviewed`, not `approved`, until the full candidate is reviewed.

- [ ] **Step 2: Write the initial coverage matrix**

Include every evidence class and the 12 priority domains from the approved design. Each row is `covered`, `partial`, or `gap`; `record_ids` must substantiate `covered`/`partial`, while `gap_note` is required for `gap`.

- [ ] **Step 3: Migrate every copied record to the required 1.1 metadata**

Assign `evidence_class`, administrative/ecological level, refresh tier, and review-due date by reading each atomic record and its locator. Do not mechanically label every old `vulnerability-capacity` record as sensitivity: distinguish coping, adaptive, institutional, and response evidence only where the source supports it. Preserve the old `analytical_role` for compatibility.

- [ ] **Step 4: Replace release-lock assertions with coverage assertions for the candidate**

```python
def test_candidate_declares_every_evidence_class(candidate_profile):
    rows = {(row["dimension"], row["value"]): row for row in candidate_profile["coverage"]}
    assert all(("evidence_class", value) in rows for value in EVIDENCE_CLASSES)


def test_candidate_covered_rows_resolve_to_records(candidate_profile, candidate_ids):
    for row in candidate_profile["coverage"]:
        if row["status"] in {"covered", "partial"}:
            assert row["record_ids"]
            assert set(row["record_ids"]) <= candidate_ids


def test_candidate_does_not_claim_comprehensive_national_coverage(candidate_profile):
    rendered = json.dumps(candidate_profile).casefold()
    assert "comprehensive national coverage" not in rendered
```

Keep the existing exact-count tests for the canonical approved release. Candidate tests must not impose an arbitrary evidence-record target.

- [ ] **Step 5: Validate and commit the honest baseline matrix**

```powershell
C:\WBG\Python313\python.exe data/climate-fcv-country-bank/scripts/validate_bank.py --country-dir data/climate-fcv-country-bank/countries/SSD/candidates/2026.08 --require-profile
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider data/climate-fcv-country-bank/tests/test_south_sudan_content.py
git -C data/climate-fcv-country-bank add countries/SSD/candidates/2026.08 tests/test_south_sudan_content.py
git -C data/climate-fcv-country-bank commit -m "data: establish South Sudan candidate coverage matrix"
```

### Task 6: Acquire and extract priority missing evidence

**Files:**
- Modify candidate `sources.json`, `evidence.json`, `pathways.json`, and `profile.json`
- Add no raw PDFs

- [ ] **Step 1: Retrieve and verify primary/authoritative sources**

Use official pages or documents for: the full South Sudan CCDR; CCKP CMIP6 future temperature, precipitation, variability, and extremes; South Sudan NAP and NDC; IPCC AR6 Africa regional projections where country findings are unavailable; IOM/OCHA/IPC/FAO/WFP/UNHCR current operational evidence; and evaluated development, disaster-risk, humanitarian, or peacebuilding interventions. Verify title, organization, publication date, stable URL, and access date before registering a source.

- [ ] **Step 2: Extract claims with an evidence worksheet**

For each candidate claim, record: exact source locator; atomic paraphrase; compact screening implication; class; observed/projected/inferred status; geography and level; sector/livelihood; affected groups; systems/assets; institutions; horizons/scenario; confidence; uncertainty; refresh tier; review due. Do not infer magnitude, geography, or causality absent from the source.

- [ ] **Step 3: Prioritize deficiencies rather than volume**

Fill, where supported: future heat/rainfall/extremes; flood hydrology and geographic exposure; drought/dry-season water stress; livestock/fisheries/forests/Sudd; roads/WASH/health/education; differentiated vulnerability; institutional mandates and delivery; coping/adaptive capacity; evaluated response performance; and FCV-to-climate or bidirectional pathways.

- [ ] **Step 4: Split compound claims and update precise locators**

One record may contain one analytical claim. If a paragraph supports separate pressure, exposure, and capacity findings, create separate records pointing to the same locator. Local studies retain their local administrative level and an uncertainty note against national generalization.

- [ ] **Step 5: Run validation after each source batch**

```powershell
C:\WBG\Python313\python.exe data/climate-fcv-country-bank/scripts/validate_bank.py --country-dir data/climate-fcv-country-bank/countries/SSD/candidates/2026.08 --require-profile
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider data/climate-fcv-country-bank/tests/test_south_sudan_content.py data/climate-fcv-country-bank/tests/test_south_sudan_sources.py
```

- [ ] **Step 6: Commit logical evidence batches**

Use source-specific or domain-specific commits, for example:

```powershell
git -C data/climate-fcv-country-bank add countries/SSD/candidates/2026.08
git -C data/climate-fcv-country-bank commit -m "data: add South Sudan future climate evidence"
```

Repeat for livelihood/service exposure, capacity/institutions, and response/pathway evidence. Never combine unreviewed source acquisition with release promotion.

### Task 7: Redesign the deterministic dossier

**Files:**
- Modify `data/climate-fcv-country-bank/climate_bank/dossier.py`
- Modify `data/climate-fcv-country-bank/scripts/build_dossier.py`
- Modify `data/climate-fcv-country-bank/tests/test_dossier.py`
- Generate candidate `dossier.md`

- [ ] **Step 1: Write failing heading, linkage, and non-repetition tests**

```python
EXPECTED_HEADINGS = [
    "Executive assessment", "Evidence coverage and critical gaps",
    "Climate pressures and exposure", "Differentiated vulnerability",
    "Coping and adaptive capacity", "Institutions and delivery systems",
    "Climate-FCV pathways", "Resilience and peace-supporting capacities",
    "Geographic and livelihood-system differentiation",
    "Implications by project type", "Technical evidence register",
    "Bibliography and review decision",
]

def test_candidate_dossier_has_analytical_headings(candidate_dossier):
    positions = [candidate_dossier.index(f"## {heading}") for heading in EXPECTED_HEADINGS]
    assert positions == sorted(positions)


def test_profile_claim_ids_appear_in_dossier(candidate_profile, candidate_dossier):
    linked = {item for section in PROFILE_LINKED_SECTIONS for row in candidate_profile[section] for item in row.get("evidence_ids", []) + row.get("pathway_ids", [])}
    assert linked <= set(re.findall(r"SSD-(?:E|P)-\d{3}", candidate_dossier))
```

- [ ] **Step 2: Confirm failure, then implement profile-led rendering**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider data/climate-fcv-country-bank/tests/test_dossier.py
```

The main sections render reviewed profile synthesis once. The technical register renders every canonical record with status, class, geography, horizon, uncertainty, source IDs, and locators. The bibliography resolves source metadata. Avoid a second narrative repetition of every record.

- [ ] **Step 3: Generate and byte-compare for determinism**

```powershell
C:\WBG\Python313\python.exe data/climate-fcv-country-bank/scripts/build_dossier.py --country-dir data/climate-fcv-country-bank/countries/SSD/candidates/2026.08
C:\WBG\Python313\python.exe data/climate-fcv-country-bank/scripts/build_dossier.py --country-dir data/climate-fcv-country-bank/countries/SSD/candidates/2026.08 --check
```

- [ ] **Step 4: Verify and commit**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider data/climate-fcv-country-bank/tests/test_dossier.py data/climate-fcv-country-bank/tests/test_south_sudan_content.py
git -C data/climate-fcv-country-bank add climate_bank/dossier.py scripts/build_dossier.py tests/test_dossier.py countries/SSD/candidates/2026.08/dossier.md
git -C data/climate-fcv-country-bank commit -m "feat: generate analytical South Sudan dossier"
```

### Task 8: Document, verify, and stop for human evidence review

**Files:**
- Modify companion `README.md` and `CLAUDE.md`
- Do not promote the candidate

- [ ] **Step 1: Document candidate validation and promotion commands**

Explain that `runtime.preview.json` is test-only, cannot be used by production, and must not replace `releases/current/runtime.json`.

- [ ] **Step 2: Run complete companion verification**

```powershell
C:\WBG\Python313\python.exe data/climate-fcv-country-bank/scripts/validate_bank.py --country-dir data/climate-fcv-country-bank/countries/SSD
C:\WBG\Python313\python.exe data/climate-fcv-country-bank/scripts/validate_bank.py --country-dir data/climate-fcv-country-bank/countries/SSD/candidates/2026.08 --require-profile
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider data/climate-fcv-country-bank/tests
git -C data/climate-fcv-country-bank diff --check
git -C data/climate-fcv-country-bank status --short
```

- [ ] **Step 3: Confirm the approved runtime is byte-identical to baseline**

Compare its SHA-256 and git diff against the checksum recorded before Task 2. Any change is a blocker.

- [ ] **Step 4: Commit documentation and push the companion branch**

```powershell
git -C data/climate-fcv-country-bank add README.md CLAUDE.md
git -C data/climate-fcv-country-bank commit -m "docs: document South Sudan candidate review workflow"
git -C data/climate-fcv-country-bank push -u origin feat/south-sudan-bank-v2
```

- [ ] **Step 5: Present the candidate dossier and coverage matrix for review**

Report newly covered areas, remaining explicit gaps, source concentration, projected-versus-observed balance, local-versus-national evidence, and every record whose interpretation needs human judgment. Stop here. Do not mark records approved or promote runtime 1.1 without explicit user approval.

---

## Plan 1 Definition of Done

- Canonical approved South Sudan 1.0 content and runtime are unchanged.
- A schema-valid, reviewed 1.1 candidate exists in a separate directory.
- Coverage is explicit and honest rather than count-driven.
- The dossier provides synthesis plus a complete evidence trail without repeated prose.
- Every projected record has a future horizon and scenario description.
- Every current record has a review-due date.
- All companion tests pass.
- The candidate branch is pushed and awaiting substantive human approval.

## Next Plan

Implement `2026-08-01-climate-bank-project-selection.md` against synthetic 1.1 fixtures and the unchanged production 1.0 release. Promotion of real South Sudan 1.1 content remains independent.
