# South Sudan Climate-FCV testing handover

**Date:** 2026-08-03  
**Branch:** `feat/climate-country-bank`

## Objective

Continue testing and improving the Climate-FCV module so its output is more accurate, relevant, operationally useful, and trustworthy than a naive Copilot prompt. Preserve the useful operational structure of the earlier app output while preventing unsupported precision, invented routing, contradictory ratings, truncation, and recommendations that ignore existing project mitigation.

The next live test is the South Sudan PCN. Use the branch-testing Render service, begin with the cheap smoke profile, and use a full quality run only after the workflow and validators are sound.

## Render service split

### Stable ITS service

- URL: `https://fcv-agent.onrender.com`
- Required branch: `main`
- Purpose: stable service used by ITS colleagues
- Current restored main commit: `79f0c164954bdeb575c27a5a8136d79a9a7490a4`
- Main-compatible build command: `pip install -r requirements.txt`

Never repoint this service to a feature branch or use it for branch testing.

### Branch-testing service

- URL: `https://fcv-agent-1.onrender.com`
- Climate branch: `feat/climate-country-bank`
- Purpose: all smoke and quality testing of feature branches
- The Climate branch may use `python render_build.py` because it contains the companion-bank build helper.

Before each test, check the linked branch in the Render service header and call `/health` to confirm the live build and runtime profile.

## Primary-service repair completed on 2026-08-03

The stable service was linked back to `main`, but repeated deploys failed with status 2 and the previously deployed Climate build remained live.

Root cause: the stable Render service retained the Climate branch build command:

```text
python render_build.py
```

The restored `main` branch does not contain that helper. Render failed before dependency installation with:

```text
python: can't open file '/opt/render/project/src/render_build.py': [Errno 2] No such file or directory
```

The stable service build command was changed to `pip install -r requirements.txt`. The resulting deploy reported **live** for `79f0c16`, and `https://fcv-agent.onrender.com/health` returned `{"status":"ok"}`.

Do not change the stable service during South Sudan testing.

## Cost-controlled testing policy

The verified Climate-FCV architecture supports two server-selected profiles controlled by `CLIMATE_VERIFIED_RUN_MODE`.

### Pass 1: smoke

- Set `CLIMATE_VERIFIED_RUN_MODE=smoke` on `fcv-agent-1`.
- Uses the cheap model profile (Haiku by default on this Render branch).
- Tests the exact workflow architecture: upload, extraction, research handling, South Sudan bank selection, typed intermediates, recommendation admission, deterministic validation, rendering, and exports.
- Smoke output must remain visibly labelled: `Smoke test: validates workflow completion only; not a quality benchmark.`
- Do not evaluate analytical quality from smoke prose.

### Pass 2: quality

- Set `CLIMATE_VERIFIED_RUN_MODE=quality` only after smoke completes and deterministic checks pass.
- Uses `claude-sonnet-4-6` for assessment and reviewer unless deliberate server-side overrides are configured.
- Run the minimum representative quality test needed.
- Do not repeatedly pay for quality runs while a schema, timeout, rendering, or routing defect can be reproduced cheaply.

Client requests must never select or downgrade the runtime model. The server environment controls the profile.

## South Sudan input and country bank

Use the South Sudan Project Concept Note dated 15 June 2026 that was used in the earlier comparison. The app previously extracted about 5,713 words and identified it as a South Sudan PCN.

Reviewed-candidate bank:

- Country: South Sudan (`SSD`)
- Release: `2026.08-preview`
- Content: 16 sources, 27 evidence records, 7 pathways
- Dossier: `data/climate-fcv-country-bank/countries/SSD/candidates/2026.08/dossier.md`
- Runtime: `data/climate-fcv-country-bank/countries/SSD/candidates/2026.08/runtime.json`
- Preview must be explicitly enabled.
- Output must remain labelled `preview; not approved`.
- Parent bank baseline: `f1d9f0f`
- Companion candidate: `d6b1a18` on `feat/south-sudan-bank-v2`
- Prior bank verification: 281 companion-bank tests and 66 app Climate tests passed.

Expected testing-service environment for the first pass:

```text
CLIMATE_COUNTRY_BANK_PATH=data/climate-fcv-country-bank/countries/SSD/candidates/2026.08/runtime.json
CLIMATE_COUNTRY_BANK_PREVIEW=reviewed-candidate
CLIMATE_VERIFIED_RUN_MODE=smoke
```

Switch only the final variable to `quality` after smoke succeeds.

## Verified-v2 architecture

The redesign replaced the earlier confidence-amplifying prompt chain with a bounded evidence-to-decision pipeline:

1. Extract source blocks and atomic project facts with provenance.
2. Separate project facts, existing responses, pathways, residual gaps, and contextual evidence into typed products with stable IDs.
3. Apply evidence-entitlement rules: project documents establish project truth; country evidence supports contextual plausibility, not unsupported project- or site-specific facts.
4. Produce four judgments: Climate-FCV relevance, FCV sensitivity, FCV responsiveness, and operationalization.
5. Compile at most three priorities, allowing fewer where candidates do not pass materiality, residuality, actionability, timing, evidence, and distinctiveness gates.
6. Validate deterministically, use targeted semantic review only for high-risk judgments, and render a short executive readout, ranked priorities, separate readiness flags, and a technical annex.

The standard workflow is automatic. Human expert review is not a mandatory pipeline stage; optional review may be supported without blocking normal generation.

## Latest successful quality run

- Run ID: `407faea6-2603-4ec0-8739-cdc9d1191f34`
- Live branch build: `4dd84b39bf0b`
- Runtime: quality
- Country-bank release: `2026.08-preview`
- Grounding log: `iso3=SSD`, 12 bank items selected, 3,713-character bank packet
- Live research did not pass its evidence gate after two attempts. The app correctly continued with `grounding_state=bank-only` and `warning_code=climate_research_failed`.

Reader-facing judgments:

- Climate-FCV relevance: **High**
- FCV sensitivity: **Moderate**
- FCV responsiveness: **Emerging**
- Operationalization: **Partial**

The narrative identified three issues as potentially warranting preparation-stage action:

1. A conflict-sensitivity and do-no-harm screen for Sub-components 1.2 and 2.2 before infrastructure sites and conservancy boundaries are fixed.
2. Explicit GBV risk-mitigation requirements in appropriate E&S preparation instruments.
3. Resolution of the PDO indicator overlap between climate-resilience beneficiaries and displaced-person beneficiaries.

However, the final reader displayed:

```text
No recommendation passed the admission threshold for this run.
```

Automated validation status was `attention`. This contradiction is the highest-priority unresolved defect.

Four readiness flags were displayed:

- unresolved PDO indicator targets and possible beneficiary double counting;
- the draft risk table's explicit need for updating;
- GBV mitigation not yet specified despite the High E&S risk discussion;
- absence of a defined early-warning or climate-information linkage.

## Fixes already made during live testing

Relevant branch commits:

- `cce6f59` - add Climate response diagnostics
- `736706c` / `163eab5` - increase fact-registry output budget
- `52ffd47` - allow judgment review to complete
- `990a150` - allow readiness flags to describe documented project placeholders while preserving true placeholder rejection
- `7064e30` - extend verified fact-extraction timeout
- `4dd84b3` - set the executive editorial target to 500-800 words while using tolerant 300-900 integrity bounds

Last verified local results after `4dd84b3`:

```text
34 passed
11 passed, 71 deselected
```

## Highest-priority unresolved work

### 1. Diagnose the zero-priority contradiction

The judgment stage said three issues could pass admission, yet the reader showed zero priorities. Determine exactly where candidates were lost:

- malformed candidate parsing;
- invalid or unknown evidence references;
- routing, authority, enhanced-activation, completion-evidence, or unsupported-number validation;
- deterministic admission score/gate failure;
- conditional semantic reviewer returning `revise` or `block` and suppressing every admitted priority.

Relevant code:

- `sector_lenses/climate_verified_pipeline.py`
- `sector_lenses/climate_recommendations.py`
- `sector_lenses/climate_verified_prompts.py`
- `sector_lenses/climate_semantic_review.py`
- `sector_lenses/climate_verified_render.py`

Do not simply lower the admission threshold. First surface exact suppression reason codes and compare the candidates with the analysis-stage statement.

### 2. Make `attention` diagnostically useful

The technical annex currently shows only `Automated validation: attention`. Add bounded developer telemetry showing candidate count, admitted count, reviewer invocation, reviewer verdict, and reason codes. Do not expose chain-of-thought or sensitive project text.

### 3. Recheck live-research evidence handling separately

The bank-only fallback was correct. Investigate separately why research structuring repeatedly failed the evidence gate despite returning some apparently valid fields. This must not block bank-grounded analysis and should not be mixed with the recommendation-admission fix.

### 4. Reassess readiness boundaries

Confirm whether GBV mitigation and early-warning linkages should be substantive priorities rather than readiness flags. Readiness flags must not absorb residual design gaps merely because recommendation admission failed.

## Recommended next-session sequence

1. Open `feat/climate-country-bank` and confirm it is clean and synchronized.
2. Confirm the stable service remains on `main`; do not modify it.
3. Confirm `fcv-agent-1` is linked to `feat/climate-country-bank`, the reviewed-candidate SSD path is enabled, and runtime mode is `smoke`.
4. Add low-cardinality recommendation-stage telemetry and a regression test reproducing the contradiction.
5. Run the targeted verified-v2 tests locally.
6. Deploy only to `fcv-agent-1`.
7. Run the South Sudan PCN once in smoke mode and verify full completion, 0-3 coherent priorities, readiness separation, exports, and visible preview/smoke labels.
8. If smoke passes, switch only `fcv-agent-1` to quality and run the PCN once.
9. Compare the final output against the Example B/C criteria: factual accuracy, accurate representation of mitigation, instrument existence/scope/timing/authority, residual-gap logic, rating coherence, operational utility, no truncation, and no unsupported precision.
10. Switch the testing service back to smoke after quality assessment unless another quality run is explicitly intended.

## Verification commands

```powershell
python -m pytest tests/test_climate_verified_south_sudan.py tests/test_climate_verified_runtime.py tests/test_climate_verified_render.py tests/test_climate_verified_pipeline.py tests/test_climate_verified_contracts.py tests/test_climate_verified_client.py -q
python -m pytest tests/test_sector_lens_app_contract.py -q -k "verified or runtime_mode"
git status --short --untracked-files=no
git rev-list --left-right --count origin/feat/climate-country-bank...HEAD
```

## Completion criteria for the next quality run

A run is not satisfactory merely because it reaches the final page:

- The candidate South Sudan bank is explicitly confirmed in logs and the annex.
- Country evidence stays contextual and does not create unsupported project/site facts.
- Existing mitigation is represented before residual gaps are stated.
- Four judgments are coherent with the executive narrative.
- Zero to three priorities are acceptable, but zero is acceptable only when the analysis also concludes none pass; otherwise validation must explain and resolve the contradiction.
- Every recommendation is linked to verified project anchors and uses conditional language where scope, timing, or authority is unresolved.
- Readiness flags remain separate and non-scoring.
- No placeholders, truncations, unsupported numbers/dates, duplicate priorities, or indiscriminate High ratings appear.
- HTML and DOCX exports match the reader model.
- Quality output remains labelled `preview; not approved` while the reviewed candidate bank is used.

## Source-comparison context

- **Example A:** strong operational container and drop-in drafting, but a load-bearing factual/routing error repeatedly assigned actions to an unrelated Year 1 school-feeding feasibility study; it also overstated existing mitigation, used an incoherent Low rating, and contained truncations.
- **Example B:** more accurate and disciplined about existing commitments, residual gaps, financing/screening inconsistencies, and real operational instruments, but less developed operational scaffolding.
- **Example C / mAI feedback:** supported atomic project facts, evidence entitlements, multidimensional judgments, a recommendation admission test, separate deterministic and semantic validation, and bounded readiness flags.

The target product combines B/C's evidence discipline with A's useful operational structure, without mandatory human review in the standard automatic workflow.
