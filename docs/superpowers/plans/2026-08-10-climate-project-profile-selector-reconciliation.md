# Climate Project Profile and Selector Reconciliation Plan

> **Execution:** Work task by task in the existing worktree and branch. Use
> strict TDD for every production change. Do not start a paid assessment,
> change Render configuration, touch the stable service, or edit reviewed
> companion-bank content.

**Goal:** Build one deterministic Project Climate Profile and use it to select
balanced, explainable, project-specific South Sudan bank packets without
changing existing context, provenance, approval, or fallback contracts.

**Baseline:** `feat/climate-country-bank` after merge commit `43b7789`,
duplicate cleanup `89715db`, and approved design `01b7fbc`.

**Architecture:** The companion release remains canonical. A pure local
extractor maps explicit project text and metadata to a bounded immutable
profile using reviewed aliases. The selector matches structured fields, applies
balance/diversity/staleness/deduplication rules, and returns canonical IDs plus
content-safe diagnostics. Server-side materialization emits whole rich
capsules for prompts while the verified adapter retains full canonical records.

**Unchanged limits:** target 8 items, maximum 12 items, bank maximum 6,000
characters, maximum 6 accepted live claims, combined maximum 12,000
characters, and no provider call for profiling or selection.

**Python:** `C:/WBG/Python313/python.exe`

**Pytest:** always include `-p no:cacheprovider`. Use a new explicit
`--basetemp` outside the repository when a test uses `tmp_path`; Windows ACL
failures in old pytest directories are environmental, not assertion failures.

---

## Task 1: Build the deterministic Project Climate Profile

**Files**

- Create `sector_lenses/climate_project_profile.py`
- Create `tests/test_climate_project_profile.py`
- Create `tests/fixtures/climate_projects/*.txt`
- Create matching `tests/fixtures/climate_projects/*.json`
- Modify `tests/fixtures/climate_bank/runtime_v1_1_candidate.json` to add
  synthetic reviewed selection aliases
- Modify `sector_lenses/__init__.py`

### Step 1: Write failing golden-profile tests

Create five synthetic archetypes:

1. agriculture and livestock;
2. fisheries, forestry, and natural-resource management;
3. roads and infrastructure;
4. health and WASH; and
5. social protection and community resilience.

Each fixture must use invented project prose and name different explicit
geographies, components, groups, institutions, systems/assets, and hazards.
No source document or paid-run output enters a fixture.

Parametrize a test that:

1. loads fixture text and expected JSON;
2. loads the reviewed alias catalog from the synthetic schema 1.1 bank fixture;
3. calls `build_project_climate_profile(...)`; and
4. compares `to_public_dict()` with the expected JSON.

### Step 2: Write failing safety and bound tests

Cover:

- word-boundary matching (`heat` must not match an unrelated substring);
- case-insensitive aliases and acronym boundaries;
- longest/most-specific alias wins;
- no inferred geography, actor, hazard, or component;
- a bank-candidate signal cannot populate an explicit project-fact field;
- duplicate aliases collapse deterministically;
- signal metadata contains controlled values, not surrounding source text;
- all tuple fields and public lists are bounded; and
- repeated calls return equal profiles.

### Step 3: Run RED

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_project_profile.py -q -p no:cacheprovider
```

Confirm failure because the module/contract does not exist.

### Step 4: Implement the minimum pure extractor

Add frozen dataclasses:

```python
@dataclass(frozen=True)
class SignalMatch:
    field: str
    canonical_value: str
    source: str
    confidence: str


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

Requirements:

- accept the country release's `selection_aliases`;
- treat canonical values as aliases of themselves;
- compile escaped boundary-aware patterns;
- use deterministic category and canonical-value ordering;
- record only controlled names and provenance labels;
- cap each category and the total signal metadata;
- expose a JSON-safe public projection; and
- make no logging or provider call.

### Step 5: Run GREEN and focused regressions

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_project_profile.py tests/test_climate_bank.py -q -p no:cacheprovider
```

### Step 6: Review and commit

Check `git diff --check`, inspect the exact staged diff, and commit:

```text
feat: build deterministic climate project profiles
```

---

## Task 2: Replace excerpt scoring with coverage-aware selection

**Files**

- Modify `sector_lenses/climate_bank_selector.py`
- Modify `tests/test_climate_bank_selector.py`
- Modify `tests/test_climate_bank_selector_realistic.py`

### Step 1: Write failing structured-match tests

Replace raw `project_signals` test inputs with `ProjectClimateProfile`
instances. Prove that:

- Jonglei fisheries outranks an unrelated national record;
- a named project element/geography match outranks hazard-only overlap;
- aliases match their reviewed canonical values;
- schema 1.0 records obtain conservative compatibility balance roles;
- schema 1.1 records use `evidence_class`;
- local records retain local scope and are not generalized nationally; and
- selection is deterministic under input reordering.

### Step 2: Write failing balance and safety tests

Add synthetic candidates covering:

- climate pressure/projection;
- vulnerability, coping, or adaptive capacity;
- institutional capacity or response performance;
- climate-to-FCV pathway;
- FCV-to-climate or bidirectional pathway;
- stale current evidence;
- near-duplicate claims; and
- multiple sources for one pathway.

Assert supported classes are balanced, stale records are penalized, duplicates
are suppressed, diversity uses all supporting sources, and low-scoring records
are not selected merely to fill a class.

### Step 3: Write failing diagnostic tests

Expected manifest diagnostics contain only:

- canonical ID;
- integer score;
- controlled matched field names;
- controlled balance role;
- controlled suppression/staleness reason; and
- controlled missing-class names.

Assert that no excerpt, matched phrase, claim prose, filename, or uploaded text
is retained.

### Step 4: Run RED

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_bank_selector.py tests/test_climate_bank_selector_realistic.py -q -p no:cacheprovider
```

### Step 5: Implement minimum structured selection

- Replace signal-token scoring with typed field matching.
- Preserve the public constants for target/max items and character limits.
- Add explicit v1 analytical-role to balance-role compatibility mapping.
- Add controlled matched-field and reason enums.
- Score all supporting pathway sources for diversity.
- Apply deterministic balance, staleness, duplicate, and final-rank passes.
- Return canonical IDs and safe diagnostics.
- Keep all existing unavailable warning codes and single-country rules.

### Step 6: Run GREEN and current bank regressions

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_bank_selector.py tests/test_climate_bank_selector_realistic.py tests/test_climate_bank.py -q -p no:cacheprovider
```

### Step 7: Review and commit

```text
feat: select balanced project relevant climate evidence
```

---

## Task 3: Materialize rich bounded capsules

**Files**

- Modify `sector_lenses/climate_bank.py`
- Modify `sector_lenses/climate_bank_selector.py`
- Modify `sector_lenses/climate_grounding.py`
- Modify `tests/test_climate_bank.py`
- Modify `tests/test_climate_grounding.py`

### Step 1: Write failing materialization tests

Prove that selecting one pathway does not silently add all supporting evidence
records to the selected-item count. The server may materialize required
supporting records for validation/provenance, but prompt selection and count
must reflect explicit selected capsules.

### Step 2: Write failing capsule tests

Evidence capsules preserve:

- `id`, `class`, `claim`;
- geographies;
- groups/systems;
- bounded project relevance;
- evidence status;
- uncertainty; and
- canonical source IDs.

Pathway capsules preserve:

- `id`, direction, pressure, mediator, possible consequence;
- geography/system;
- evidence strength;
- uncertainty; and
- supporting evidence IDs.

For schema 1.0, use conservative derived classes without mutating the canonical
release.

### Step 3: Write failing bound tests

Assert:

- the bank projection is at most 6,000 characters;
- the combined grounding remains at most 12,000;
- low-priority capsules are dropped whole;
- claims and uncertainty strings are never sliced;
- source metadata is not duplicated into the prompt when IDs suffice;
- selected-item count equals emitted evidence plus pathway capsules; and
- bank/live provenance states remain unchanged.

### Step 4: Run RED

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_bank.py tests/test_climate_grounding.py -q -p no:cacheprovider
```

### Step 5: Implement minimum capsule projection

- Keep full canonical records in the server grounding result.
- Add project relevance from controlled diagnostic matches only.
- Serialize evidence and pathway capsules separately.
- Add whole-item pruning in deterministic reverse-priority order.
- Preserve candidate-preview status.
- Do not expand prompt or combined character ceilings.

### Step 6: Run GREEN and commit

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_bank.py tests/test_climate_bank_selector.py tests/test_climate_grounding.py tests/test_climate_context_adapter.py -q -p no:cacheprovider
```

Commit:

```text
feat: preserve metadata in compact climate capsules
```

---

## Task 4: Integrate one profile through both application workflows

**Files**

- Modify `app.py`
- Modify `tests/test_climate_workflow_contract.py`
- Modify `tests/test_sector_lens_app_contract.py`

### Step 1: Write failing workflow tests

Cover both step-by-step and Express research preparation. Assert:

- one profile is built from project-document text plus document metadata;
- the same public profile is passed to bank selection;
- current live research still receives its existing bounded project input;
- no extra model call or search is introduced;
- diagnostics survive only through the allowlisted safe manifest;
- the browser cannot inject profile or diagnostic prose into rematerialization;
- Climate-disabled and generic FCV routes do not build a profile; and
- profile failure degrades to existing safe bank behavior.

### Step 2: Run RED

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_workflow_contract.py tests/test_sector_lens_app_contract.py -q -p no:cacheprovider
```

### Step 3: Implement minimum wiring

- Build the profile once in the shared Stage 1 research path after resolving the
  bank country and alias catalog.
- Pass the typed profile to `select_bank_manifest`.
- Allowlist only safe diagnostic fields across request/session boundaries.
- Rematerialize canonical records server-side exactly as before.
- Keep the current raw excerpt only where the unchanged live-research contract
  requires it; do not log or persist it.
- Keep both application workflows on the same helper path.

### Step 4: Run GREEN and commit

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_workflow_contract.py tests/test_sector_lens_app_contract.py tests/test_climate_bank_selector.py -q -p no:cacheprovider
```

Commit:

```text
feat: integrate climate project profiles into assessment workflows
```

---

## Task 5: Protect the verified evidence and reader contracts

**Files**

- Modify `sector_lenses/climate_context_adapter.py` only if tests prove a
  compatibility gap
- Modify `tests/test_climate_context_adapter.py`
- Modify `tests/test_climate_verified_runtime.py`
- Modify `tests/test_climate_evidence_trail.py`
- Modify `tests/test_climate_verified_render.py`

### Step 1: Write compatibility tests before production edits

Assert that rich selected records:

- become valid `ContextEvidenceRef` entries;
- retain local scope, confidence, context class, and source linkage;
- keep `preview; not approved` on reviewed-candidate evidence;
- preserve resolvable canonical evidence IDs in the reader trail;
- do not promote bank content into project facts; and
- do not alter priorities, ratings, guidance, prompts, or reader hierarchy.

### Step 2: Run tests

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_context_adapter.py tests/test_climate_verified_runtime.py tests/test_climate_evidence_trail.py tests/test_climate_verified_render.py -q -p no:cacheprovider
```

If the tests pass without a production change, commit the contract tests only.
If they fail, make the smallest adapter-only compatibility change and rerun.

### Step 3: Commit

```text
test: protect verified climate bank selection contracts
```

---

## Task 6: Document contracts and verify the phase

**Files**

- Modify `claude.md`
- Modify the relevant public reference document only if needed
- Update the private dual-build parity log (never stage or commit it)

### Step 1: Write contract documentation

Document:

- `ProjectClimateProfile` purpose and explicit-match boundary;
- safe selection diagnostics and enums;
- rich capsule fields;
- v1.0 compatibility behavior;
- unchanged prompt/context limits;
- current live-research behavior and deferred gap agenda; and
- companion-bank content ownership.

Record the shared-contract candidates and Render-specific wiring in the private
parity log without referencing the private file in tracked public documents.

### Step 2: Run focused verification

Use a new temp directory:

```powershell
$taskTemp = Join-Path $env:TEMP 'pytest-climate-selector-phase-20260810'
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_project_profile.py tests/test_climate_bank.py tests/test_climate_bank_selector.py tests/test_climate_bank_selector_realistic.py tests/test_climate_grounding.py tests/test_climate_context_adapter.py tests/test_climate_workflow_contract.py tests/test_climate_verified_runtime.py tests/test_climate_evidence_trail.py tests/test_climate_verified_render.py tests/test_sector_lens_app_contract.py -q -p no:cacheprovider --basetemp=$taskTemp
```

### Step 3: Run the full local tracked suite

```powershell
$taskTemp = Join-Path $env:TEMP 'pytest-climate-selector-full-20260810'
& 'C:\WBG\Python313\python.exe' -m pytest tests -q -p no:cacheprovider --basetemp=$taskTemp
```

Expected baseline before this increment is 907 passing tests. Record the exact
new count. Do not reinterpret Windows temp ACL setup errors as assertion
failures; use a fresh explicit elevated basetemp once rather than deleting old
pytest directories.

### Step 4: Static verification

- `git diff --check`
- no conflict markers;
- no references to the removed root flat bank;
- no source PDFs, secrets, paid-run outputs, or restricted corpus content;
- no prompt/rating/recommendation/reader changes;
- no context-limit increases;
- no confidential fixture or log text; and
- exact staged scope reviewed.

### Step 5: Commit documentation

```text
docs: document climate project selection contract
```

### Step 6: Stop for review

Report:

- commits by task;
- focused and full-suite results;
- any environmental test limitations;
- changed shared-contract fields;
- confirmation that no paid/live run or Render change occurred; and
- the deferred literature and live-research increments.

Do not push or deploy without a new explicit instruction.
