# Gap-Directed Climate Research Reliability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Use `superpowers:test-driven-development` for every code change, `superpowers:systematic-debugging` for any failed live run, and `superpowers:verification-before-completion` before each completion claim. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Direct the existing bounded live search at the most material project-specific gaps and report exactly why evidence is accepted or rejected, without adding searches, provider calls, context, or timeout.

**Architecture:** A deterministic agenda planner compares the structured project profile with selected bank coverage and emits at most three ranked questions. The existing two-search pass receives that agenda and the compact bank summary. Normalization records bounded structural rejection counts before discarding invalid untrusted fields. The evidence gate returns one controlled subreason; retry occurs only for structurally repairable partial results. Rejected research remains completely excluded and bank-only fallback remains valid.

**Tech Stack:** Python 3.13, Flask, Anthropic web-search API already used by the app, stdlib JSON/URL validation, pytest, existing browser/Render deployment workflow.

**Depends on:** `2026-08-01-climate-bank-project-selection.md`.

**Hard limits:** two searches per attempt; at most two attempts; 150-second aggregate Stage 1 research budget; 4-6 requested claims and six accepted maximum; 12,000 combined grounding characters; no source/project content in telemetry.

---

## File Map

- Create `sector_lenses/climate_research_agenda.py`: deterministic gap ranking and bounded questions.
- Modify `sector_lenses/research.py`: agenda-aware prompts, normalization rejection counts, gate subreasons, and retry classification.
- Modify `sector_lenses/climate_grounding.py`: deduplicate bank/live claims and retain safe gate metadata.
- Modify `sector_lenses/__init__.py`: export agenda and gate contracts.
- Modify `app.py`: build the agenda after selection, thread it into both attempts, log bounded subreasons/counts, and preserve fallback.
- Create `tests/test_climate_research_agenda.py`.
- Modify `tests/test_climate_research.py`, `tests/test_climate_grounding.py`, and `tests/test_climate_workflow_contract.py`.
- Create `tests/test_climate_research_acceptance.py`: five synthetic profile/response combinations.
- Modify `README.md` and private dual-build parity notes.

## Gate Contract

```python
CLIMATE_RESEARCH_GATE_REASONS = {
    "no_authoritative_source",
    "source_url_invalid",
    "claim_without_source",
    "claim_not_project_linked",
    "claim_not_geographically_linked",
    "insufficient_distinct_sources",
    "response_truncated",
    "invalid_time_horizon",
    "unsupported_inference",
}
```

Decision shape:

```json
{
  "ok": false,
  "code": "climate_research_insufficient",
  "subreason": "claim_not_project_linked",
  "counts": {
    "valid_sources": 2,
    "valid_claims": 1,
    "invalid_urls": 0,
    "claims_without_source": 0,
    "claims_without_project_link": 2
  },
  "bundle": {
    "status": "partial",
    "sources": [],
    "claims": []
  }
}
```

Counts are clamped to 99. Public fallback bundles contain no rejected source or claim content.

### Task 1: Build a deterministic three-question research agenda

**Files:**
- Create `sector_lenses/climate_research_agenda.py`
- Create `tests/test_climate_research_agenda.py`

- [ ] **Step 1: Write failing agenda tests for the five golden profiles**

```python
@pytest.mark.parametrize("slug,expected_kind", [
    ("agriculture_livestock", "project_lifetime_hazard"),
    ("fisheries_forestry_nrm", "unmatched_project_signal"),
    ("roads_infrastructure", "weak_geographic_coverage"),
    ("health_wash", "missing_evidence_class"),
    ("social_protection_resilience", "stale_current_evidence"),
])
def test_agenda_prioritizes_material_gap(slug, expected_kind, profiles, selections):
    agenda = build_climate_research_agenda(profiles[slug], selections[slug])
    assert 1 <= len(agenda) <= 3
    assert agenda[0]["reason"] == expected_kind
```

- [ ] **Step 2: Add deterministic, privacy, and no-gap tests**

```python
def test_agenda_is_empty_when_packet_covers_profile(complete_profile, complete_selection):
    assert build_climate_research_agenda(complete_profile, complete_selection) == []


def test_agenda_contains_controlled_values_not_document_excerpt(profile, selection, confidential_phrase):
    serialized = json.dumps(build_climate_research_agenda(profile, selection))
    assert confidential_phrase not in serialized


def test_agenda_is_byte_deterministic(profile, selection):
    first = json.dumps(build_climate_research_agenda(profile, selection), sort_keys=True)
    second = json.dumps(build_climate_research_agenda(profile, selection), sort_keys=True)
    assert first == second
```

- [ ] **Step 3: Confirm tests fail**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_research_agenda.py
```

- [ ] **Step 4: Implement ranked gap candidates**

```python
GAP_PRIORITY = {
    "unmatched_project_signal": 100,
    "project_lifetime_hazard": 90,
    "weak_geographic_coverage": 80,
    "missing_evidence_class": 70,
    "stale_current_evidence": 60,
}

def build_climate_research_agenda(profile: dict, selection: dict) -> list[dict[str, object]]:
    candidates = _gap_candidates(profile, selection)
    ranked = sorted(candidates, key=lambda row: (-GAP_PRIORITY[row["reason"]], row["key"]))
    return [_question_from_gap(row, profile) for row in ranked[:3]]
```

Questions use matched canonical values, for example: `"What authoritative evidence describes current or projected flood impacts on roads in Jonglei during the project lifetime?"` The planner never inserts an undocumented place, hazard, institution, or group.

- [ ] **Step 5: Bound each question and commit**

Limit each question to 300 characters and the serialized agenda to 1,000 characters by dropping the third and then second question; do not truncate a question mid-sentence.

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_research_agenda.py
git add sector_lenses/climate_research_agenda.py tests/test_climate_research_agenda.py
git commit -m "feat: plan climate research from bank coverage gaps"
```

### Task 2: Pass profile, bank summary, and agenda to exactly two searches

**Files:**
- Modify `sector_lenses/research.py`
- Modify `tests/test_climate_research.py`

- [ ] **Step 1: Write failing prompt-contract tests**

```python
def test_search_prompt_contains_profile_and_ranked_agenda(project_profile, bank_summary, agenda):
    prompt = build_climate_search_prompt("South Sudan", "NRM", project_profile, bank_summary, agenda)
    assert "Jonglei" in prompt
    assert agenda[0]["question"] in prompt
    assert "SELECTED BANK COVERAGE" in prompt


def test_search_request_keeps_two_use_cap(fake_client, research_inputs):
    run_climate_web_research(**research_inputs, api_client=fake_client)
    first = fake_client.calls[0]
    assert first["tools"][0]["max_uses"] == 2


def test_prompt_never_contains_full_dossier(project_profile, bank_summary, agenda):
    prompt = build_climate_search_prompt("South Sudan", "NRM", project_profile, bank_summary, agenda)
    assert len(prompt) <= CLIMATE_SEARCH_PROMPT_MAX_CHARS
    assert "Technical evidence register" not in prompt
```

- [ ] **Step 2: Confirm failures**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_research.py -k "prompt or two_use"
```

- [ ] **Step 3: Add bounded prompt inputs**

`bank_summary` contains only selected IDs, class/role coverage, geographies, source organizations, and missing classes; it does not duplicate full claims. The first search targets the top-ranked authoritative physical/project-lifetime gap. The second targets the next distinct material gap. If only one gap exists, the second search triangulates it with a distinct authoritative or current-operations source type.

- [ ] **Step 4: Keep structuring output at 4-6 claims and existing horizon enum**

Add `institutions` to the structured claim schema and normalized claim contract. The prompt requires each claim to cite a source, name a project element, and name a geography, affected group, institution, system, or asset. Project-profile facts and bank claims are context, not sources; the model may not cite them as web evidence.

- [ ] **Step 5: Verify and commit**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_research.py -k "prompt or search or packet"
git add sector_lenses/research.py tests/test_climate_research.py
git commit -m "feat: target climate searches at project evidence gaps"
```

### Task 3: Preserve structural rejection counts during normalization

**Files:**
- Modify `sector_lenses/research.py`
- Modify `tests/test_climate_research.py`

- [ ] **Step 1: Write one failing normalization test per rejected structure**

```python
@pytest.mark.parametrize("mutation,count_key", [
    ("invalid_url", "invalid_urls"),
    ("missing_source", "claims_without_source"),
    ("missing_project_element", "claims_without_project_link"),
    ("missing_anchor", "claims_without_geographic_link"),
    ("invalid_horizon", "invalid_time_horizons"),
    ("unsupported_inference", "unsupported_inferences"),
])
def test_normalizer_counts_rejected_untrusted_items(valid_raw_bundle, mutation, count_key):
    mutate_bundle(valid_raw_bundle, mutation)
    normalized = normalize_climate_research_bundle(valid_raw_bundle)
    assert normalized["_diagnostics"][count_key] == 1
```

- [ ] **Step 2: Define unsupported inference narrowly**

An `inferred` claim is structurally unsupported when it has `confidence: high`, or when `evidence_gap` is empty. This rule does not determine substantive truth; it prevents an inference from being presented without an explicit limitation.

- [ ] **Step 3: Confirm failures, then implement counters before filtering**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_research.py -k "normalizer or rejected_untrusted"
```

Use only fixed diagnostic keys. Clamp every count. `_diagnostics` is internal and is removed by the display-safe envelope and prompt formatter.

- [ ] **Step 4: Preserve existing six-claim and trusted-host behavior**

Do not admit an invalid record to obtain a diagnostic. Invalid URLs, missing source links, invalid enums, or unsupported inference remain absent from `sources`/`claims`.

- [ ] **Step 5: Verify and commit**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_research.py
git add sector_lenses/research.py tests/test_climate_research.py
git commit -m "feat: retain climate research rejection diagnostics"
```

### Task 4: Return precise evidence-gate subreasons

**Files:**
- Modify `sector_lenses/research.py`
- Modify `tests/test_climate_research.py`

- [ ] **Step 1: Write failing table-driven gate tests**

```python
@pytest.mark.parametrize("fixture,subreason", [
    ("no_authoritative_source", "no_authoritative_source"),
    ("source_url_invalid", "source_url_invalid"),
    ("claim_without_source", "claim_without_source"),
    ("claim_not_project_linked", "claim_not_project_linked"),
    ("claim_not_geographically_linked", "claim_not_geographically_linked"),
    ("insufficient_distinct_sources", "insufficient_distinct_sources"),
    ("response_truncated", "response_truncated"),
    ("invalid_time_horizon", "invalid_time_horizon"),
    ("unsupported_inference", "unsupported_inference"),
])
def test_gate_returns_precise_subreason(fixture, subreason, gate_fixtures):
    decision = climate_research_evidence_gate(**gate_fixtures[fixture])
    assert decision["ok"] is False
    assert decision["subreason"] == subreason
```

- [ ] **Step 2: Implement deterministic precedence**

Use this precedence when more than one problem exists:

1. `response_truncated`;
2. `source_url_invalid` when invalid URLs leave too few valid cited sources;
3. `claim_without_source`;
4. `claim_not_project_linked`;
5. `claim_not_geographically_linked`;
6. `invalid_time_horizon`;
7. `unsupported_inference`;
8. `insufficient_distinct_sources`;
9. `no_authoritative_source`.

If a bundle has two valid distinct sources but neither is authoritative, return `no_authoritative_source`. If it has fewer than two valid distinct sources and no more specific structural failure, return `insufficient_distinct_sources`.

- [ ] **Step 3: Pass truncation diagnostics explicitly**

```python
decision = climate_research_evidence_gate(
    bundle,
    response_diagnostic={
        "stop_reason": diagnostic["stop_reason"],
        "json_status": diagnostic["json_status"],
    },
)
```

Do not infer truncation only from empty JSON; use `max_tokens` or incomplete structured JSON.

- [ ] **Step 4: Keep generic top-level codes compatible**

Retain `climate_research_failed` and `climate_research_insufficient` for existing display behavior. Add `subreason` and counts without changing accepted-bundle semantics.

- [ ] **Step 5: Verify and commit**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_research.py -k "gate or truncat"
git add sector_lenses/research.py tests/test_climate_research.py
git commit -m "feat: diagnose climate evidence gate failures"
```

### Task 5: Restrict retry to repairable evidence failures

**Files:**
- Modify `sector_lenses/research.py`
- Modify `app.py`
- Modify `tests/test_climate_research.py`

- [ ] **Step 1: Write failing retry matrix tests**

```python
REPAIRABLE = {
    "claim_without_source",
    "claim_not_project_linked",
    "claim_not_geographically_linked",
    "insufficient_distinct_sources",
    "no_authoritative_source",
}

@pytest.mark.parametrize("subreason", sorted(CLIMATE_RESEARCH_GATE_REASONS))
def test_retry_only_for_repairable_partial_results(subreason):
    decision = {"ok": False, "subreason": subreason, "bundle": PARTIAL_BUNDLE}
    assert should_retry_climate_research(decision, stop_reason="end_turn") is (subreason in REPAIRABLE)
```

- [ ] **Step 2: Add no-retry tests for truncation, timeouts, empty results, and invalid inference**

Retry must be false when the first response used `max_tokens`, exceeded the parent deadline, contains no usable sources/claims, or failed because of `response_truncated`, `source_url_invalid`, `invalid_time_horizon`, or `unsupported_inference`.

- [ ] **Step 3: Build a narrow retry prompt**

The retry receives the same bounded agenda plus the controlled subreason and says what structural requirement to repair. It does not include rejected claim text. It still has `max_uses: 2`, shares the original 135-second attempt cap/150-second parent deadline, and remains the second and final attempt.

- [ ] **Step 4: Verify no added calls and commit**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_research.py -k "retry or timeout or overload or truncat"
git add app.py sector_lenses/research.py tests/test_climate_research.py
git commit -m "fix: narrow climate research retries by gate reason"
```

### Task 6: Integrate safe diagnostics, fallback, and bank/live deduplication

**Files:**
- Modify `app.py`
- Modify `sector_lenses/climate_grounding.py`
- Modify `tests/test_climate_grounding.py`
- Modify `tests/test_climate_workflow_contract.py`

- [ ] **Step 1: Write failing fallback tests**

```python
def test_rejected_research_is_excluded_but_subreason_is_retained(bank_manifest, rejected_bundle):
    grounding, public_research = resolve_climate_grounding(bank_manifest, rejected_bundle)
    assert grounding["state"] == "bank-only"
    assert public_research["sources"] == []
    assert public_research["claims"] == []
    assert grounding["research_subreason"] == "claim_not_project_linked"


def test_bank_live_duplicate_keeps_distinct_provenance_without_duplicate_claim(bank_packet, accepted_bundle):
    merged = merge_climate_grounding(bank_packet, accepted_bundle)
    assert len(merged["live_claims"]) == 0
    assert "climate-source-1" in merged["duplicate_live_source_ids"]
```

- [ ] **Step 2: Deduplicate conservatively**

Treat a live claim as duplicate only when its normalized claim-token similarity exceeds the tested threshold and it shares a hazard/sector or geography/system anchor with a bank capsule. Retain live provenance in the display-safe source list even when the duplicate claim is omitted from the prompt.

- [ ] **Step 3: Add privacy-safe logs**

```text
Climate research gate assessment_id=<id> code=<generic> subreason=<controlled> valid_sources=<n> valid_claims=<n> rejected_sources=<n> rejected_claims=<n>
```

Never log URL, title, claim, project element, location, question, or source content.

- [ ] **Step 4: Confirm every grounding state**

Test `bank+research`, `bank-only`, `research-only`, and `thematic-only`. The combined serialized context remains at or below 12,000 characters and accepted live claims at or below six.

- [ ] **Step 5: Verify and commit**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_grounding.py tests/test_climate_workflow_contract.py
git add app.py sector_lenses/climate_grounding.py tests/test_climate_grounding.py tests/test_climate_workflow_contract.py
git commit -m "feat: expose safe climate research gate diagnostics"
```

### Task 7: Run five synthetic end-to-end acceptance cases

**Files:**
- Create `tests/test_climate_research_acceptance.py`
- Reuse five project profiles and synthetic web responses

- [ ] **Step 1: Define one accepted or intentionally rejected response per profile**

Cases must cover: accepted authoritative projection; accepted authoritative plus current-operations evidence; rejected invalid URL; rejected missing project linkage; and truncated structuring response. Use invented fixture titles and `.example`-style URLs only if the trusted-host validator is dependency-injected for tests; otherwise use clearly synthetic paths on allowed hostnames without making network requests.

- [ ] **Step 2: Assert agenda-to-claim linkage**

Every accepted claim links to a named project element and at least one geography, group, institution, system, or asset from the profile. Reject claims that merely restate national climate context.

- [ ] **Step 3: Assert distinct outputs and unchanged limits**

The five contexts differ materially; bank-only fallbacks still contain useful capsules; no result exceeds the item, claim, character, search, attempt, or time contract.

- [ ] **Step 4: Run focused and full automated verification**

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider tests/test_climate_research_acceptance.py tests/test_climate_research.py tests/test_climate_research_agenda.py tests/test_climate_grounding.py tests/test_climate_workflow_contract.py
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
git diff --check
git status --short
```

- [ ] **Step 5: Commit acceptance tests**

```powershell
git add tests/test_climate_research_acceptance.py
git commit -m "test: validate gap-directed climate research"
```

### Task 8: Review contracts, push, and perform bounded live acceptance

**Files:**
- Modify `README.md`
- Modify private `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`
- No fixture or log may contain confidential project text

- [ ] **Step 1: Record shared-contract decisions**

Log the agenda shape, gate subreasons/counts, public grounding metadata, and retry semantics in the private parity file. Record provider-specific API invocation and Flask telemetry as build-specific.

- [ ] **Step 2: Run adversarial code review and address verified findings**

Use `superpowers:requesting-code-review` after the full automated suite. Review especially: evidence accidentally admitted after rejection; privacy leakage; count/context regressions; retry call inflation; and 1.0 compatibility.

- [ ] **Step 3: Push both feature branches only after clean verification**

Push the parent branch and, if Plan 1 candidate work has been performed, its companion branch. Update the parent submodule pointer only to a reviewed/approved commit appropriate for the deployment being tested; do not point production at an unapproved preview release.

- [ ] **Step 4: Run a bank-only deployed acceptance test**

Use the existing South Sudan project. Disable or deliberately stub live research through the approved test mechanism. Confirm the assessment completes, shows `bank-only`, uses a bounded project-specific packet, and discloses that live evidence was unavailable/rejected.

- [ ] **Step 5: Run one controlled accepted bank-plus-research test**

Pass a synthetic accepted bundle through the real server evidence gate without paid web search. Confirm `bank+research`, source provenance, combined bound, and no duplicated claim.

- [ ] **Step 6: Run one production live-search assessment**

Only after the candidate content decision and automated/deployed tests pass, run one paid production South Sudan assessment. Use the existing browser session and Render logs. Confirm: exactly two initial searches; no more than one narrow retry; precise gate subreason or acceptance; expected grounding state; completed note; correct provenance disclosure; and no project/source content in logs.

- [ ] **Step 7: Stop after one live run unless a specific defect is fixed**

If the live run fails, preserve response diagnostics and logs, use `superpowers:systematic-debugging`, and rerun only after a concrete defect has been identified and changed. Provider overload or timeout alone does not justify repeated paid runs.

- [ ] **Step 8: Final verification and documentation commit**

```powershell
git add README.md
git commit -m "docs: document climate research evidence diagnostics"
git push origin feat/climate-country-bank
```

---

## Plan 3 Definition of Done

- Research is driven by at most three explicit bank/project gaps.
- Each attempt still permits exactly two searches; there are at most two attempts.
- Every rejection produces one precise controlled subreason and bounded counts.
- Invalid or rejected evidence never enters the prompt, output, or provenance claims.
- Repairable partial evidence can receive one narrow retry; truncation and hard failures do not loop.
- All four grounding fallback states remain correct.
- Five synthetic project cases and the full suite pass.
- One bank-only, one synthetic bank-plus-research, and at most one production live acceptance run are reviewed.

## Overall Redesign Completion Gate

The redesign is complete only after the Plan 1 South Sudan candidate is substantively approved and promoted, the five golden selections are accepted, the live gate is diagnosable, the production run is reviewed, context/time limits are unchanged, and dual-build parity decisions are recorded.
