# Climate Quality Tiering and Grounding Guardrails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent document defects from becoming duplicate priorities, prevent country context from becoming unsupported site-specific obligations, and repair unsupported numeric document labels without malformed prose.

**Architecture:** Keep model prompts preventive and make deterministic Python admission authoritative. Validate fact-stage integrity findings once, pass a bounded reservation to downstream model stages, then apply structural guards before ranking; keep label repair inside the existing drafting normalizer so public schemas and reader structure do not change.

**Tech Stack:** Python 3.13, frozen dataclasses, regular expressions, pytest, existing `climate-verified-v2.1` structured pipeline.

---

## File map

- Modify `sector_lenses/climate_recommendations.py`: phrase-aware label repair and pure deterministic grounding-classification helpers.
- Modify `sector_lenses/climate_verified_pipeline.py`: early integrity validation, bounded payload projection, pre-ranking suppression, diagnostics, and prompt-version increments.
- Modify `sector_lenses/climate_verified_prompts.py`: prevention instructions for reserved checks, context-only actions, neutral labels, and semantic review.
- Modify `tests/test_climate_recommendations.py`: unit tests for label repair and both deterministic guard boundaries.
- Modify `tests/test_climate_verified_pipeline.py`: end-to-end payload, suppression, preservation, and diagnostics tests.
- Modify `tests/test_climate_verified_client.py`: prompt contract assertions.
- Reuse `tests/test_climate_document_integrity.py`: regression coverage for validated integrity findings and reader-tier retention.
- Do not modify schemas, renderers, bank content, rating logic, caps, or context budgets.

### Task 1: Repair unsupported document labels as whole phrases

**Files:**
- Modify: `sector_lenses/climate_recommendations.py:35-50,288-374`
- Test: `tests/test_climate_recommendations.py`

- [ ] **Step 1: Write failing phrase-repair tests**

Add imports for `normalize_unsupported_drafting_precision` if absent, then add:

```python
def test_supported_drafting_label_is_preserved_whole():
    candidate = replace(
        _candidate(),
        current_document_drafting=_draft(
            "Add this under Sub-component 1.4 before the risk discussion."
        ),
        supported_numeric_tokens=("1.4",),
    )

    normalized, repairs = normalize_unsupported_drafting_precision(candidate)

    assert normalized.current_document_drafting.text == (
        "Add this under Sub-component 1.4 before the risk discussion."
    )
    assert repairs == ()


def test_unsupported_drafting_label_is_replaced_as_a_whole_phrase():
    candidate = replace(
        _candidate(),
        current_document_drafting=_draft(
            "Add this under Sub-component 1.4 before the risk discussion."
        ),
        supported_numeric_tokens=(),
    )

    normalized, repairs = normalize_unsupported_drafting_precision(candidate)

    assert normalized.current_document_drafting.text == (
        "Add this under the relevant sub-component before the risk discussion."
    )
    assert "under Sub-component" not in normalized.current_document_drafting.text
    assert repairs == ("DRAFTING_UNSUPPORTED_PRECISION_REMOVED",)


def test_unsupported_year_label_uses_preparation_year_wording():
    candidate = replace(
        _candidate(),
        current_document_drafting=_draft(
            "Record the review in Year 2 and update Annex 3."
        ),
        supported_numeric_tokens=(),
    )

    normalized, _ = normalize_unsupported_drafting_precision(candidate)

    assert normalized.current_document_drafting.text == (
        "Record the review during the relevant preparation year and update "
        "the relevant annex."
    )
```

- [ ] **Step 2: Run the new tests and confirm RED**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_recommendations.py -k "drafting_label or year_label" -p no:cacheprovider --basetemp "$env:TEMP\codex-quality-label-red-20260811" -q
```

Expected: the unsupported-label assertions fail because `_without_numeric_tokens` removes only the digits.

- [ ] **Step 3: Add phrase-aware repair before generic token deletion**

Add near the numeric patterns:

```python
NUMBERED_DOCUMENT_LABEL_PATTERN = re.compile(
    r"\b(?:the\s+)?(?P<label>sub[- ]?component|component|section|annex)\s+"
    r"(?P<number>\d+(?:\.\d+)*)\b",
    re.IGNORECASE,
)
YEAR_LABEL_PATTERN = re.compile(
    r"\b(?:(?:in|during)\s+)?(?:the\s+)?year\s+"
    r"(?P<number>\d+(?:\.\d+)*)\b",
    re.IGNORECASE,
)
```

Add immediately before `_without_numeric_tokens`:

```python
def _repair_unsupported_numeric_labels(
    text: str,
    unsupported: set[str],
) -> str:
    """Replace an unsupported numbered label without leaving broken prose."""

    replacements = {
        "component": "the relevant component",
        "sub-component": "the relevant sub-component",
        "sub component": "the relevant sub-component",
        "section": "the relevant section",
        "annex": "the relevant annex",
    }

    def replace_document_label(match: re.Match[str]) -> str:
        if match.group("number") not in unsupported:
            return match.group(0)
        return replacements[match.group("label").casefold()]

    def replace_year_label(match: re.Match[str]) -> str:
        if match.group("number") not in unsupported:
            return match.group(0)
        return "during the relevant preparation year"

    repaired = NUMBERED_DOCUMENT_LABEL_PATTERN.sub(replace_document_label, text)
    return YEAR_LABEL_PATTERN.sub(replace_year_label, repaired)
```

At the top of `_without_numeric_tokens`, add:

```python
    text = _repair_unsupported_numeric_labels(text, unsupported)
```

- [ ] **Step 4: Run recommendation tests and confirm GREEN**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_recommendations.py -p no:cacheprovider --basetemp "$env:TEMP\codex-quality-label-green-20260811" -q
```

Expected: all tests in the file pass, including existing generic numeric cleanup tests.

- [ ] **Step 5: Commit the label repair**

```powershell
git add -- sector_lenses/climate_recommendations.py tests/test_climate_recommendations.py
git diff --cached --check
git commit -m "fix: preserve climate drafting label grammar"
```

### Task 2: Add pure deterministic grounding guards

**Files:**
- Modify: `sector_lenses/climate_recommendations.py`
- Test: `tests/test_climate_recommendations.py`

- [ ] **Step 1: Write failing unit tests for the document-check boundary**

Add a helper and three tests:

```python
def _grounding_context(**overrides):
    values = {
        "gap_types": {"RG-001": "not_yet_specified"},
        "gap_pathway_ids": {"RG-001": frozenset({"PW-001"})},
        "fact_source_blocks": {"PF-001": frozenset({"DOC-1-B-1"})},
        "integrity_source_blocks": frozenset({"DOC-1-B-1"}),
    }
    values.update(overrides)
    return RecommendationGroundingContext(**values)


def test_document_completion_candidate_is_reserved_for_document_checks():
    candidate = replace(
        _candidate(),
        decision="Populate the placeholder target in the results table.",
        minimum_action="Complete the unfinished document section.",
        enhanced_action=None,
        enhanced_activation=None,
    )

    assert deterministic_grounding_failure_codes(
        candidate, _grounding_context()
    ) == ("ADMISSION_DUPLICATES_DOCUMENT_CHECK",)


def test_independent_climate_fcv_design_gap_sharing_block_is_retained():
    candidate = replace(
        _candidate(),
        decision="Define a continuity response for flood-related access disruption.",
    )
    context = _grounding_context(
        gap_types={"RG-001": "partial_response"},
    )

    assert deterministic_grounding_failure_codes(candidate, context) == ()


def test_document_candidate_needs_structural_source_overlap_to_be_suppressed():
    candidate = replace(
        _candidate(),
        decision="Populate the placeholder target in the results table.",
    )
    context = _grounding_context(
        integrity_source_blocks=frozenset({"DOC-1-B-9"}),
    )

    assert deterministic_grounding_failure_codes(candidate, context) == ()
```

- [ ] **Step 2: Write failing unit tests for the context-promotion boundary**

```python
def test_context_only_candidate_cannot_mandate_new_protocol():
    candidate = replace(
        _candidate(),
        recommendation_basis="country_context",
        instrument_claim_ids=(),
        decision="Establish a herder-fisher agreement at each project site.",
        minimum_action="Create a site protocol and assign a new coordination actor.",
    )

    assert deterministic_grounding_failure_codes(
        candidate, _grounding_context()
    ) == ("RECOMMENDATION_CONTEXT_PROMOTION_UNSUPPORTED",)


def test_context_only_candidate_may_verify_applicability():
    candidate = replace(
        _candidate(),
        recommendation_basis="country_context",
        instrument_claim_ids=(),
        decision="Assess whether seasonal resource conflict applies at project sites.",
        minimum_action="Confirm applicability before deciding a response.",
    )

    assert deterministic_grounding_failure_codes(
        candidate, _grounding_context()
    ) == ()


def test_project_evidence_can_support_proportionate_project_action():
    candidate = replace(
        _candidate(),
        recommendation_basis="project_evidence",
        decision="Update the documented site-selection method.",
    )

    assert deterministic_grounding_failure_codes(
        candidate, _grounding_context()
    ) == ()
```

- [ ] **Step 3: Run the new guard tests and confirm RED**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_recommendations.py -k "document_completion_candidate or independent_climate_fcv or structural_source_overlap or context_only_candidate or project_evidence_can" -p no:cacheprovider --basetemp "$env:TEMP\codex-quality-guards-red-20260811" -q
```

Expected: collection fails because `RecommendationGroundingContext` and `deterministic_grounding_failure_codes` do not exist.

- [ ] **Step 4: Implement the bounded structural classifiers**

Add constants near the existing gate constants:

```python
DOCUMENT_GAP_TYPES = {"not_yet_specified", "contradictory"}
SUBSTANTIVE_GAP_TYPES = {"confirmed_omission", "partial_response"}
DOCUMENT_ACTION_PATTERN = re.compile(
    r"\b(?:complete|populate|fill|replace|remove|delete|reconcile|correct|repair|update)\b",
    re.IGNORECASE,
)
DOCUMENT_OBJECT_PATTERN = re.compile(
    r"\b(?:placeholder|draft|section|table|field|cross-reference|document|target|indicator)\b",
    re.IGNORECASE,
)
SUBSTANTIVE_ACTION_PATTERN = re.compile(
    r"\b(?:implement|construct|operate|deliver|train|finance|procure|deploy|enforce|maintain)\b",
    re.IGNORECASE,
)
PROJECT_OBLIGATION_ACTION_PATTERN = re.compile(
    r"\b(?:establish|create|adopt|require|mandate|set up|formalize|introduce|assign)\b",
    re.IGNORECASE,
)
PROJECT_OBLIGATION_OBJECT_PATTERN = re.compile(
    r"\b(?:instrument|agreement|protocol|actor|system|committee|unit|mechanism|commitment)\b",
    re.IGNORECASE,
)
```

Add the context and helper below `CandidateRecommendation`:

```python
@dataclass(frozen=True)
class RecommendationGroundingContext:
    gap_types: dict[str, str]
    gap_pathway_ids: dict[str, frozenset[str]]
    fact_source_blocks: dict[str, frozenset[str]]
    integrity_source_blocks: frozenset[str]


def _candidate_action_text(candidate: CandidateRecommendation) -> str:
    return " ".join(
        value
        for value in (
            candidate.decision,
            candidate.minimum_action,
            candidate.enhanced_action,
            candidate.completion_evidence,
        )
        if value
    )


def _duplicates_reserved_document_check(
    candidate: CandidateRecommendation,
    context: RecommendationGroundingContext,
) -> bool:
    gap_types = {
        context.gap_types.get(gap_id)
        for gap_id in candidate.residual_gap_ids
    }
    if not gap_types or None in gap_types or not gap_types <= DOCUMENT_GAP_TYPES:
        return False
    if any(
        context.gap_types.get(gap_id) in SUBSTANTIVE_GAP_TYPES
        and context.gap_pathway_ids.get(gap_id)
        for gap_id in candidate.residual_gap_ids
    ):
        return False
    linked_blocks = {
        block_id
        for fact_id in candidate.project_anchor_ids
        for block_id in context.fact_source_blocks.get(fact_id, frozenset())
    }
    if not linked_blocks or not linked_blocks <= context.integrity_source_blocks:
        return False
    action = _candidate_action_text(candidate)
    return bool(
        DOCUMENT_ACTION_PATTERN.search(action)
        and DOCUMENT_OBJECT_PATTERN.search(action)
        and not SUBSTANTIVE_ACTION_PATTERN.search(action)
    )


def _promotes_context_to_project_obligation(
    candidate: CandidateRecommendation,
) -> bool:
    if candidate.recommendation_basis != "country_context":
        return False
    action = _candidate_action_text(candidate)
    return bool(
        PROJECT_OBLIGATION_ACTION_PATTERN.search(action)
        and PROJECT_OBLIGATION_OBJECT_PATTERN.search(action)
        and not candidate.instrument_claim_ids
    )


def deterministic_grounding_failure_codes(
    candidate: CandidateRecommendation,
    context: RecommendationGroundingContext,
) -> tuple[str, ...]:
    """Return content-free deterministic grounding failures before ranking."""

    codes: list[str] = []
    if _duplicates_reserved_document_check(candidate, context):
        codes.append("ADMISSION_DUPLICATES_DOCUMENT_CHECK")
    if _promotes_context_to_project_obligation(candidate):
        codes.append("RECOMMENDATION_CONTEXT_PROMOTION_UNSUPPORTED")
    return tuple(codes)
```

Do not use text similarity or source excerpts in either classifier.

- [ ] **Step 5: Run all recommendation tests and confirm GREEN**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_recommendations.py -p no:cacheprovider --basetemp "$env:TEMP\codex-quality-guards-green-20260811" -q
```

Expected: all recommendation tests pass.

- [ ] **Step 6: Commit the deterministic guards**

```powershell
git add -- sector_lenses/climate_recommendations.py tests/test_climate_recommendations.py
git diff --cached --check
git commit -m "feat: guard climate recommendation grounding"
```

### Task 3: Integrate reservations, suppression diagnostics, and prompts

**Files:**
- Modify: `sector_lenses/climate_verified_pipeline.py:37-57,83-93,828-1240`
- Modify: `sector_lenses/climate_verified_prompts.py:190-300`
- Modify: `tests/test_climate_verified_pipeline.py`
- Modify: `tests/test_climate_verified_client.py`
- Test: `tests/test_climate_document_integrity.py`

- [ ] **Step 1: Write failing pipeline tests for bounded reservations**

In `tests/test_climate_verified_pipeline.py`, add a helper that inserts a valid fact-stage finding:

```python
def _with_integrity_finding(responses):
    responses[0]["document_integrity_findings"] = [{
        "flag_id": "DIF-001",
        "category": "material_placeholder",
        "flag": "The target remains a placeholder.",
        "why_it_matters": "The expected result cannot be verified.",
        "document_basis_ids": ["DOC-1-B-1"],
        "suggested_verification": "Populate the target from the source document.",
        "residual_gap_ids": [],
    }]
    return responses


def test_validated_document_checks_are_reserved_for_both_compilers():
    responses = _with_integrity_finding(_responses())
    recommendation = responses[3]["recommendation_candidates"][0]
    recommendation["current_document_drafting"] = None
    assessment = FakeClient(responses + [{"drafting_sets": []}], [])

    run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(assessment, FakeClient([], [])),
    )

    recommendation_payload = next(
        call["payload"] for call in assessment.calls
        if call["stage"] == "recommendation_compiler"
    )
    drafting_payload = next(
        call["payload"] for call in assessment.calls
        if call["stage"] == "drafting_compiler"
    )
    expected = [{
        "flag_id": "DIF-001",
        "category": "material_placeholder",
        "flag": "The target remains a placeholder.",
        "document_basis_ids": ["DOC-1-B-1"],
        "suggested_verification": "Populate the target from the source document.",
    }]
    assert recommendation_payload["reserved_document_checks"] == expected
    assert drafting_payload["reserved_document_checks"] == expected
```

The projection intentionally omits `why_it_matters` and `residual_gap_ids` to stay bounded.

- [ ] **Step 2: Write failing end-to-end suppression and preservation tests**

```python
def test_document_only_candidate_is_suppressed_but_check_remains():
    responses = _with_integrity_finding(_responses())
    candidate = responses[3]["recommendation_candidates"][0]
    candidate["decision"] = "Populate the placeholder target in the results table."
    candidate["minimum_action"] = "Complete the unfinished document section."

    result = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(FakeClient(responses, []), FakeClient([], [])),
    )

    assert result["priorities"] == []
    assert [item["flag_id"] for item in result["review_readiness_flags"]] == [
        "DIF-001"
    ]
    assert result["recommendation_diagnostics"]["candidate_suppressions"] == [{
        "recommendation_id": "REC-001",
        "stage": "grounding",
        "reason_codes": ["ADMISSION_DUPLICATES_DOCUMENT_CHECK"],
        "unsupported_numeric_fields": [],
    }]


def test_context_only_site_protocol_is_suppressed_with_bounded_diagnostic():
    responses = _responses()
    candidate = responses[3]["recommendation_candidates"][0]
    candidate["recommendation_basis"] = "country_context"
    candidate["instrument_claim_ids"] = []
    candidate["decision"] = "Establish a herder-fisher agreement at project sites."
    candidate["minimum_action"] = "Create a site protocol and assign an actor."

    result = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(FakeClient(responses, []), FakeClient([], [])),
    )

    assert result["priorities"] == []
    suppression = result["recommendation_diagnostics"]["candidate_suppressions"][0]
    assert suppression == {
        "recommendation_id": "REC-001",
        "stage": "grounding",
        "reason_codes": ["RECOMMENDATION_CONTEXT_PROMOTION_UNSUPPORTED"],
        "unsupported_numeric_fields": [],
    }
    assert "herder" not in str(suppression).casefold()


def test_context_only_applicability_check_remains_admissible():
    responses = _responses()
    candidate = responses[3]["recommendation_candidates"][0]
    candidate["recommendation_basis"] = "country_context"
    candidate["instrument_claim_ids"] = []
    candidate["decision"] = (
        "Assess whether seasonal resource conflict applies at project sites."
    )
    candidate["minimum_action"] = (
        "Confirm applicability before deciding a response."
    )

    result = run_verified_climate_pipeline(
        **_arguments(),
        clients=PipelineClients(FakeClient(responses, []), _pass_review_client()),
    )

    assert [item["recommendation_id"] for item in result["priorities"]] == [
        "REC-001"
    ]
```

- [ ] **Step 3: Write failing prompt/version tests**

Extend `test_every_stage_uses_structured_json_and_evidence_entitlements` in `tests/test_climate_verified_client.py`:

```python
    assert "reserved_document_checks" in prompts["recommendation_compiler"]
    assert "already own the document-check tier" in prompts["recommendation_compiler"]
    assert "assess, verify, or confirm applicability" in prompts["recommendation_compiler"]
    assert "neutral document label" in prompts["drafting_compiler"]
    assert "reserved_document_checks" in prompts["drafting_compiler"]
    assert "country context alone" in prompts["conditional_review"]
```

Update the three version expectations in `test_manifest_is_privacy_safe_and_scoped_to_the_run` to:

```python
    assert first["manifest"]["prompt_versions"]["recommendation_compiler"] == (
        "climate-recommendations-v2.5"
    )
    assert first["manifest"]["prompt_versions"]["conditional_review"] == (
        "climate-review-v2.6"
    )
    assert first["manifest"]["prompt_versions"]["drafting_compiler"] == (
        "climate-drafting-v1.1"
    )
```

- [ ] **Step 4: Run the new pipeline and prompt tests and confirm RED**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_verified_pipeline.py tests/test_climate_verified_client.py -k "reserved_for_both or document_only_candidate or context_only_site or applicability_check or every_stage or manifest_is_privacy" -p no:cacheprovider --basetemp "$env:TEMP\codex-quality-pipeline-red-20260811" -q
```

Expected: failures show missing reserved payloads, missing grounding suppression, missing prompt text, and old prompt versions.

- [ ] **Step 5: Validate and project integrity findings once**

Import `RecommendationGroundingContext` and `deterministic_grounding_failure_codes` into `climate_verified_pipeline.py`.

Immediately after fact/assertion normalization and before `bounded_analysis`, compute:

```python
    integrity_flags = _integrity_readiness_flags(fact_payload, known_block_ids)
    reserved_document_checks = [
        {
            "flag_id": item.flag_id,
            "category": item.category,
            "flag": item.flag,
            "document_basis_ids": list(item.document_basis_ids),
            "suggested_verification": item.suggested_verification,
        }
        for item in integrity_flags
    ]
```

Remove the later duplicate `_integrity_readiness_flags` call and reuse this list when merging readiness flags.

- [ ] **Step 6: Pass the reservation into downstream stages**

Add:

```python
            "reserved_document_checks": reserved_document_checks,
```

to the `recommendation_compiler` payload and, when invoked, the `drafting_compiler` payload. Also add it to the `conditional_review` payload so the reviewer sees the same tier ownership boundary.

- [ ] **Step 7: Apply grounding suppression before ordinary admission**

After candidate validation and before the admission loop, build:

```python
    grounding_context = RecommendationGroundingContext(
        gap_types={item.gap_id: item.gap_type for item in gaps},
        gap_pathway_ids={
            item.gap_id: frozenset(item.pathway_ids) for item in gaps
        },
        fact_source_blocks={
            item.claim_id: frozenset(item.source_block_ids) for item in facts
        },
        integrity_source_blocks=frozenset(
            block_id
            for item in integrity_flags
            for block_id in item.document_basis_ids
        ),
    )
```

Replace the existing admission loop and rank call with:

```python
    grounded_candidates: list[CandidateRecommendation] = []
    admitted_count = 0
    for candidate in candidates:
        failure_codes = (
            deterministic_grounding_failure_codes(candidate, grounding_context)
            + admission_failure_codes(candidate)
        )
        if failure_codes:
            recommendation_reasons.extend(failure_codes)
            reasons.extend(failure_codes)
            if len(candidate_suppressions) < 3:
                grounding_codes = [
                    code for code in failure_codes
                    if code in {
                        "ADMISSION_DUPLICATES_DOCUMENT_CHECK",
                        "RECOMMENDATION_CONTEXT_PROMOTION_UNSUPPORTED",
                    }
                ]
                candidate_suppressions.append({
                    "recommendation_id": candidate.recommendation_id,
                    "stage": "grounding" if grounding_codes else "admission",
                    "reason_codes": list(failure_codes)[:12],
                    "unsupported_numeric_fields": [],
                })
            continue
        grounded_candidates.append(candidate)
        admitted_count += 1
    priorities = admit_and_rank(grounded_candidates)
    suppressed["recommendations"] += len(candidates) - len(priorities)
```

Retain the priority-cap diagnostic based on `admitted_count > len(priorities)`.

- [ ] **Step 8: Reinforce all three prompt boundaries and increment versions**

In `_recommendation_prompt`, state that `reserved_document_checks` already own the document-check tier; candidates must not restate them without an independently supported substantive pathway gap. Add that country context alone may support only an action to assess, verify, or confirm applicability and cannot establish a site-specific instrument, agreement, protocol, actor, system, or commitment.

In `_drafting_prompt`, state that reserved checks must not become recommendation drafting and that a numbered Component, Sub-component, Section, Annex, or Year label may be used only when the exact label appears in linked project facts; otherwise use a neutral document label.

In `_review_prompt`, state that country context alone cannot establish a site-specific project obligation and that a reserved document check must remain in its tier unless the recommendation has an independent substantive gap.

Update only:

```python
    "recommendation_compiler": "climate-recommendations-v2.5",
    "conditional_review": "climate-review-v2.6",
    "drafting_compiler": "climate-drafting-v1.1",
```

- [ ] **Step 9: Run focused integration tests and confirm GREEN**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_recommendations.py tests/test_climate_verified_pipeline.py tests/test_climate_verified_client.py tests/test_climate_document_integrity.py -p no:cacheprovider --basetemp "$env:TEMP\codex-quality-integration-green-20260811" -q
```

Expected: all four suites pass. Confirm the existing document-check cap, priority cap, and diagnostic-shape tests remain green.

- [ ] **Step 10: Commit pipeline integration**

```powershell
git add -- sector_lenses/climate_verified_pipeline.py sector_lenses/climate_verified_prompts.py tests/test_climate_verified_pipeline.py tests/test_climate_verified_client.py
git diff --cached --check
git commit -m "fix: separate climate priorities from document checks"
```

### Task 4: Regression, scope, and acceptance verification

**Files:**
- Verify only; no new production scope unless a test identifies a defect.

- [ ] **Step 1: Run focused Climate-FCV suites with a fresh external basetemp**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_recommendations.py tests/test_climate_verified_pipeline.py tests/test_climate_verified_client.py tests/test_climate_document_integrity.py tests/test_climate_analysis.py tests/test_climate_verified_render.py tests/test_climate_grounding.py tests/test_climate_bank.py tests/test_climate_bank_selector.py tests/test_climate_bank_selector_realistic.py tests/test_climate_context_materializer.py tests/test_sector_lens_pipeline.py tests/test_sector_lens_app_contract.py -p no:cacheprovider --basetemp "$env:TEMP\codex-quality-focused-final-20260811" -q
```

Expected: zero failures; record pass and deselection counts.

- [ ] **Step 2: Run the full tracked test suite once**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest -p no:cacheprovider --basetemp "$env:TEMP\codex-quality-full-final-20260811" -q
```

Expected: zero failures; record the complete count. Do not rerun merely because pytest later hits the known Windows shutdown/ACL issue after reporting all results; inspect the final pytest status first.

- [ ] **Step 3: Review committed scope and cleanliness**

Run:

```powershell
git status --short --untracked-files=no
git diff HEAD~3..HEAD --check
git diff --name-status 839f9a0..HEAD
git log --oneline --decorate -5
```

Expected production scope is limited to:

```text
sector_lenses/climate_recommendations.py
sector_lenses/climate_verified_pipeline.py
sector_lenses/climate_verified_prompts.py
```

Expected test scope is limited to the three listed test files. The worktree is clean. No schema, renderer, country-bank data, rating, cap, or budget file changes.

- [ ] **Step 4: Perform the acceptance review before any push**

Confirm from tests and diff:

1. A document-only candidate is absent from priorities while its `DIF-*` check remains.
2. An independent `confirmed_omission` or `partial_response` pathway gap is not suppressed merely because it shares a source block.
3. Context-only obligations are suppressed; conditional applicability checks survive.
4. Supported labels remain exact; unsupported labels remain grammatical.
5. Suppression diagnostics expose only bounded IDs and reason codes.
6. The five-priority cap, four-check cap, schema version, rating semantics, bank release, 6,000/12,000 character limits, and six-live-claim limit are unchanged.

Do not merge to `main`. Push and Render smoke/quality runs remain a separate explicit deployment step under the existing user authorization boundary.
