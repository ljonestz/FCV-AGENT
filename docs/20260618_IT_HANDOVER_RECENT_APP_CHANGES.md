# ITS Handover Brief - Recent FCV Project Screener Changes

Date: 2026-06-19

Audience: ITS colleagues maintaining the internal World Bank version of the FCV Project Screener.

Purpose: explain the main recent changes in the Render-hosted GitHub version of the app, why they were made, and how to reproduce or adapt them in the internal clone.

---

## 1. Executive Summary

The public/Render version of the FCV Project Screener has recently been expanded from a PAD/PCN/PID-oriented screener into a broader design-stage project assessment tool. The main additions are:

- Support for additional World Bank lending and process types: Additional Financing, Restructuring, DPF/DPO, PforR/P4R, MPA, and regional or multi-country operations.
- Better instrument-aware analysis, so recommendations use the right operational levers for the instrument instead of applying IPF/PAD assumptions to all documents.
- Updated frontend copy and upload UX to make clear which documents are supported and which workflows remain future functionality.
- Expanded document upload handling, with one primary project document, up to 10 supporting package documents, and up to 3 contextual documents.
- Secondary-document distillation, so extra uploaded documents provide useful evidence without overloading model context windows.
- Improved Stage 3 recommendation fields, including alignment with CPF pillars and RRA/conflict-driver evidence when those contextual documents are uploaded.

The internal version should replicate these changes, but it may eventually diverge in one important way: it can add application-layer retrieval from permission-aware internal WBG sources. That internal retrieval should be injected into the model context by the backend. The model should not be asked to search internal systems by itself.

---

## 2. Source Branches, PRs, and Current Baseline

Use the GitHub repository as the source of truth:

`https://github.com/ljonestz/FCV-AGENT`

As of 2026-06-19, the current Render/GitHub baseline is:

| Ref | Commit | Status | Purpose |
|---|---|---|---|
| `origin/main` | `4e8a9d0` | Current merged baseline | Includes Stage 2 storage-quota resilience, Phase 0-6 instrument/document expansion, Phase 6 intersection composition, and secondary-document distillation. |
| [PR #34](https://github.com/ljonestz/FCV-AGENT/pull/34), `codex/integrate-secondary-phase6` | `4f24b69` head, merged as `4e8a9d0` | Merged | Canonical integration PR combining Phase 6 and secondary-document distillation on top of the current `main`. |
| [PR #29](https://github.com/ljonestz/FCV-AGENT/pull/29), `feat/phase6-intersection` | `76fba9e` | Merged via PR #34 | Original Phase 0-6 lending/document-type expansion: policy registry, AF/restructuring, DPF/DPO, PforR/P4R, MPA, multi-country/regional layer, intersection matrix, and policy/timing corrections. |
| [PR #33](https://github.com/ljonestz/FCV-AGENT/pull/33), `feat/secondary-doc-distillation` | `1f6b0d2` | Merged via PR #34 | Original secondary-document upload expansion and distillation layer. |
| [PR #31](https://github.com/ljonestz/FCV-AGENT/pull/31), `fix/stage2-storage-quota-main` | `67c9110` | Merged before PR #34 | Makes Stage 2 "Under the Hood" browser storage best-effort, so quota failures do not block Stage 3. |

Recommended adoption path for ITS: start from `origin/main` at `4e8a9d0` if possible. This is safer than replaying PR #29 and PR #33 separately because their conflicts have already been reconciled and tested in PR #34.

If the internal clone cannot fast-forward to `4e8a9d0`, use PR #34 as the primary diff reference. Only fall back to the original PRs (#29, #33, #31) for file-level archaeology.

Verification performed on the PR #34 integration branch before merge:

```bash
python -m pytest tests -p no:cacheprovider
# 136 passed
```

---

## 3. Application Architecture Context

The app is a Flask single-page application:

| File | Role |
|---|---|
| `app.py` | Backend routes, document extraction, stage prompts, model calls, parsing, DOCX export. |
| `background_docs.py` | Static WBG/FCV knowledge base constants, instrument calibration, stage guidance maps. |
| `index.html` | Frontend UI, upload handling, Express/Step-by-Step flows, rendering, download triggers. |
| `fcv_distillation.py` | New secondary-document classifier/distiller for package and context documents. |
| `docs/reference/` | Architecture references for prompts, routes, and frontend behavior. |
| `tests/` | Regression tests for parsing, routing, instrument behavior, frontend constants, and distillation. |

The analysis remains a three-stage workflow:

1. Stage 1 extracts project and context evidence.
2. Stage 2 assesses FCV sensitivity and responsiveness.
3. Stage 3 produces an operational recommendations note.

Express mode and Step-by-Step mode should remain equivalent in output quality. Any internal port should update both paths where prompt assembly or document preprocessing changes.

---

## 4. Change Group A - Lending and Document-Type Expansion

### Purpose

The app needed to work for more than standard IPF/PAD reviews. TTLs may upload Additional Financing papers, restructuring papers, DPF/DPO program documents, PforR/P4R documents, MPA documentation, or regional/multi-country operations. Each requires different FCV risks, operational levers, and recommendation constraints.

### What changed

The phase 0-6 work adds:

- A policy and instrument registry in `background_docs.py`.
- Document-type and instrument-type calibration in `app.py`.
- Stage-specific rules for what can be recommended at PCN, PID, PAD, AF, restructuring, DPF/DPO, PforR/P4R, MPA, and regional/multi-country stages.
- Tests for each instrument/process expansion.
- UX copy in `index.html` and `README.md` that accurately describes supported document types.

### What ITS should port

Port these areas together:

- `background_docs.py`: instrument guide, process guide, FCV instrument calibration, stage guidance map.
- `app.py`: document classification, stage-aware prompt injection, temporal guardrails, instrument routing constraints, recommendation timing rules.
- `index.html`: upload/landing copy and any displayed document-type labels.
- `tests/test_phase0_foundation.py`
- `tests/test_mid_cycle_phase1.py`
- `tests/test_dpf_phase2.py`
- `tests/test_p4r_phase3.py`
- `tests/test_mpa_multicountry_phase45.py`
- `tests/test_intersection_phase6.py`

---

## 5. Change Group B - AF and Restructuring

### Purpose

Additional Financing and restructuring reviews are not the same as original project preparation. The assessment should focus on what is being added, scaled, changed, or restructured rather than reopening the entire original operation.

### Expected behavior

For AF:

- Screen the proposed AF scope and rationale.
- Flag whether the AF simply scales an FCV-blind design or uses the AF to course-correct.
- Apply ESF standards only to activities introduced or scaled under the AF where relevant.

For Restructuring:

- Screen the restructuring itself.
- Focus on changed components, revised results framework, implementation arrangements, financing reallocations, closing-date changes, and safeguards updates.
- Frame recommendations as adjustments to the restructuring package where feasible.

### Key implementation areas

- `STAGE_GUIDANCE_MAP` in `background_docs.py`.
- Stage 1 document/process detection in `app.py`.
- Stage 2 AF/restructuring assessment instructions.
- Stage 3 timing and actionability rules.

---

## 6. Change Group C - DPF / DPO

### Purpose

Development Policy Financing works through policy and institutional actions, not project-level investments. The app previously risked producing IPF-style recommendations that are inappropriate for DPF/DPO operations.

### Expected behavior

When the instrument is DPF/DPO/DPL:

- Do not recommend IPF-only tools such as ESCP, ESS1-10 instruments, SEP/LMP, project-level GRMs, DLIs, or CERC as if they applied to a DPF.
- Frame FCV sensitivity around prior actions, reform sequencing, political economy, distributional effects, safety-net timing, policy reversal risk, and macroeconomic transmission to vulnerable groups.
- For programmatic series, use `next-series` where a recommendation is better handled in the next operation.

### Key implementation areas

- `FCV_INSTRUMENT_CALIBRATION` in `background_docs.py`.
- DPF/DPO exclusions and framing rules in Stage 2 and Stage 3 prompts in `app.py`.
- DPF-specific tests in `tests/test_dpf_phase2.py`.

---

## 7. Change Group D - PforR / P4R

### Purpose

Program-for-Results operations use DLIs and program systems. The app now avoids both underusing those levers and importing IPF-only assumptions.

### Expected behavior

When the instrument is PforR/P4R:

- Focus on DLI design, verification, disbursement cliffs, system capacity, IVA access, ESSA limitations, and program-boundary risks.
- Do not recommend IPF-only tools where they do not apply.
- Consider FCV risks to verification, access, grievance handling, local implementation systems, and equity across program areas.

### Key implementation areas

- PforR calibration in `background_docs.py`.
- Instrument routing in `app.py`.
- PforR-specific tests in `tests/test_p4r_phase3.py`.

---

## 8. Change Group E - MPA

### Purpose

MPAs require recommendations that account for sequencing, phase transition risk, regional or institutional continuity, and the fact that later phase financing is not automatic.

### Expected behavior

For MPAs:

- Assess whether the current phase embeds adequate FCV learning loops for later phases.
- Avoid assuming that later phases are guaranteed.
- Consider phase governance, trigger logic, continuity of institutions, and risk of carrying weak design assumptions across phases.
- Where MPA and PforR features intersect, apply both sets of constraints.

### Key implementation areas

- MPA calibration in `background_docs.py`.
- Stage 2/3 prompt sections in `app.py`.
- MPA tests in `tests/test_mpa_multicountry_phase45.py`.

---

## 9. Change Group F - Regional and Multi-Country Operations

### Purpose

Regional or multi-country operations should not be forced into a single-country FCV frame. They need country-by-country differentiation plus attention to regional spillovers.

### Expected behavior

For regional or multi-country operations:

- Identify whether the project covers multiple countries or a regional corridor/platform.
- Preserve country-specific FCV differences where they matter.
- Consider cross-border conflict dynamics, refugee flows, regional institutions, and uneven implementation capacity.
- Avoid overgeneralizing from one country to the whole operation.

### Key implementation areas

- Multi-country/regional layer in `app.py`.
- Regional/multi-country calibration in `background_docs.py`.
- Multi-country tests in `tests/test_mpa_multicountry_phase45.py`.

Internal adaptation note: if the internal app performs web or internal source retrieval, retrieval should handle multi-country operations deliberately. Best practice is either a bounded per-country retrieval pass for the main countries identified, or a regional retrieval pass plus targeted country-specific retrieval for high-risk countries. Do not let the first detected country become the only context source.

---

## 10. Change Group G - Intersection Matrix

### Purpose

Some operations combine multiple complexities, such as MPA plus PforR, regional plus DPF, or AF plus safeguards transition. The app now has an intersection layer so prompt logic composes rather than applying only one instrument rule.

### Expected behavior

- Apply all relevant constraints when multiple instrument/process dimensions are present.
- Avoid contradictory recommendations, such as suggesting IPF instruments for DPFs or assuming a multi-country MPA has uniform country risk.
- Preserve frontend compatibility by keeping enum values and CSS labels stable where possible.

### Key implementation areas

- Intersection matrix logic in `background_docs.py` and `app.py`.
- Tests in `tests/test_intersection_phase6.py`.

---

## 11. Change Group H - UX and Document Scope Copy

### Purpose

The frontend copy was updated so users understand that the tool reviews appraisal/design-stage project documents across several instruments. It also clarifies that MTR/ISR implementation review is not yet live.

### Expected behavior

- Landing/upload copy should mention PCN, PID, PAD, AF, Restructuring, DPF/DPO, PforR, MPA, and regional operations.
- MTR/ISR should remain marked as future/coming soon unless the internal team explicitly enables and tests the implementation-review workflow.
- Upload zones should distinguish primary project documents, supporting package documents, and contextual documents.

### Key implementation areas

- `index.html`
- `README.md`
- `docs/reference/reference_frontend_functions.md`
- `docs/reference/reference_prompt_architecture.md`

---

## 12. Change Group I - Secondary Upload Expansion and Distillation

### Purpose

TTL use cases often require multiple documents. The previous model of reading secondary documents in full does not scale. The updated approach expands uploads while controlling context-window pressure.

### New upload tiers

| Zone | Role | Cap | Treatment |
|---|---:|---:|---|
| Zone 1 | Primary project document | 1 | Full Stage 1 project assessment path, capped by existing primary-document limits. |
| Zone 2 | Supporting project package documents | Up to 10 | Classified and distilled into key-signal cards. Not independently assessed. |
| Zone 3 | Contextual documents | Up to 3 | Distilled into context cards, especially RRA conflict drivers and CPF pillars. |

### Expected behavior

- The primary project document remains the anchor for the assessment.
- Package documents, such as SORT, DLI matrix, policy matrix, ESCP, SEP, RF, and technical assessments, provide supporting evidence only.
- Contextual documents, especially RRA and CPF, inform conflict-driver and country-strategy alignment.
- Overflow and failed distillation produce named stubs. Documents should not disappear silently.
- Stage 3 priority JSON includes `rra_driver_alignment` in addition to `cpf_alignment`.

### Key implementation areas

- New file: `fcv_distillation.py`
- `app.py`: imports and calls `distill_doc_parts_stream()` in both Express and Step-by-Step Stage 1 assembly paths.
- `index.html`: upload caps and copy.
- `docs/reference/reference_backend_routes.md`
- `docs/reference/reference_prompt_architecture.md`
- Tests:
  - `tests/test_fcv_distillation.py`
  - `tests/test_frontend_upload_caps.py`
  - updated `tests/test_extract_priorities.py`

### Context-budget logic

The distillation layer uses compact cards rather than full secondary text:

- Structured package card cap: about 2,800 characters.
- Generic package card cap: about 1,200 characters.
- Context card cap: about 1,800 characters.
- Global secondary-card budget: about 32,000 characters, with a reserve for context documents.

This keeps the primary assessment from being squeezed out by secondary evidence.

---

## 13. Stage 2 Storage-Quota Resilience

### Purpose

Stage 2 stores "Under the Hood" analytical material in browser storage for Go Deeper views. Browser storage can fail because of quota limits, especially with large outputs. The fix makes that persistence best-effort.

### Expected behavior

- Failure to write Stage 2 analytical material to local storage should not fail Stage 2.
- Stage 3 should still run.
- The user may lose some local Go Deeper convenience, but the core assessment should continue.

### Key implementation areas

- `static/fcv_storage.js`
- `index.html`
- Stage 2 handling around Under the Hood persistence.

---

## 14. Internal Version Divergence Marker - Internal Retrieval

The internal World Bank version has an important potential advantage over the Render version: it can use permission-aware internal retrieval for WBG policy, procedure, and country context sources.

### Recommended principle

Internal retrieval should be implemented at the application layer before the model call. The backend should retrieve relevant excerpts and inject them into the model context. The prompt should not ask the model to search internal systems itself.

### Why this matters

- Internal WBG systems are not necessarily exposed as model-callable tools.
- Access control must be enforced before content is injected.
- Procedural guidance can be sensitive, current, and versioned.
- The model should not invent internal policy requirements from static knowledge.

### Recommended retrieval lanes

| Lane | Examples |
|---|---|
| Country context | RRA where permitted, CPF/CEN context, country team notes, CMU/regional updates, DNR/country documents. |
| Procedure and policy | Current pre-appraisal procedures, OP 7.30 guidance, PC14 guidance, FCV Envelope guidance, ESF/SEA-SH requirements, OPCS notes, FCV operational notes. |

### Recommended injected block

```text
--- INTERNAL WBG COUNTRY CONTEXT PACK ---
[permission-aware country excerpts or explicit empty-pack fallback]

--- INTERNAL WBG PROCEDURE PACK ---
[permission-aware procedure excerpts or explicit empty-pack fallback]

--- INTERNAL SOURCE REGISTRY ---
[source id | title | system | document id/url | last updated | retrieved at | access label | retrieval lane]
```

### Empty-pack fallback rule

If no internal sources are retrieved, the backend should inject explicit fallback instructions, not empty placeholders. For example:

```text
No internal procedure sources retrieved. Do not infer WBG procedural requirements from model knowledge. Use "requires verification" language for procedural claims and identify the likely verification owner.
```

### Pre-call safety check

Before any model call, the backend should fail or substitute fallback text if unresolved placeholders remain, such as:

- `{internal_country_context_pack}`
- `{internal_procedure_pack}`
- `{internal_source_registry}`

### Source precedence in the internal app

Use this precedence order:

1. Uploaded project documents for project facts.
2. Uploaded contextual documents for country/project context supplied by the user.
3. Permission-aware internal WBG retrieval packs for current internal policy, procedure, and country context.
4. External web research for current external facts where internal sources are absent.
5. Static/model knowledge only for general analytical background, clearly labelled as not verified current procedure.

---

## 15. Recommended Internal Porting Sequence

1. Confirm the internal clone's current baseline commit and differences from the Render GitHub repo.
2. Back up any internal-only changes, especially authentication, internal search, deployment configuration, secrets handling, and network policy.
3. Prefer adopting or comparing against `origin/main` at `4e8a9d0` / PR #34, which already combines Stage 2 storage resilience, Phase 0-6, Phase 6 intersection composition, and secondary-document distillation.
4. If direct adoption of `4e8a9d0` is not possible, apply PR #34 as the primary patch reference rather than replaying PR #29 and PR #33 separately.
5. Reconcile any conflicts in:
   - `app.py`
   - `background_docs.py`
   - `index.html`
   - `docs/reference/`
   - tests
6. Re-run the full test suite.
7. Test Express mode and Step-by-Step mode manually with at least one document in each supported category.
8. Only after the public-version parity changes are stable, add the internal retrieval layer.

---

## 16. Validation Checklist

### Automated tests

Run:

```bash
python -m pytest tests -p no:cacheprovider
```

At minimum, confirm the following test areas pass:

- Classification and priority parsing.
- AF/restructuring behavior.
- DPF/DPO behavior.
- PforR/P4R behavior.
- MPA and multi-country behavior.
- Intersection matrix behavior.
- Secondary-document distillation.
- Frontend upload caps.
- Stage stream timeout behavior.

### Manual smoke tests

Run one Express analysis and, if feasible, one Step-by-Step analysis for:

- PAD or PID.
- Additional Financing.
- Restructuring.
- DPF/DPO.
- PforR/P4R.
- MPA.
- Regional or multi-country operation.
- One run with primary document plus several package documents.
- One run with primary document plus RRA and CPF contextual documents.

Check that:

- Stage 1 identifies document type and instrument type correctly.
- Stage 2 does not apply irrelevant instrument requirements.
- Stage 3 recommendations use appropriate WBG levers.
- DPF recommendations do not include ESCP/SEP/DLI/CERC errors.
- PforR recommendations use DLI/program-system framing where relevant.
- AF/restructuring recommendations focus on changed or added scope.
- Multi-country operations preserve country-specific differences.
- CPF alignment appears when CPF evidence is available.
- RRA driver alignment appears only when RRA/equivalent evidence is available.
- Overflowed or failed secondary documents are named, not silently omitted.

---

## 17. Known Caveats

- MTR/ISR implementation review is not yet live in the frontend. Backend implementation-review logic exists, but the user-facing workflow remains withheld pending dedicated testing.
- PR #34 resolves the prior integration conflict between the Phase 0-6 stack and secondary-document distillation. ITS should use PR #34 / `origin/main` at `4e8a9d0` as the canonical integrated state.
- The Render deployment uses gunicorn/gevent with long SSE timeouts. Internal hosting may use different infrastructure, but the SSE/long-running request behavior still needs equivalent timeout and keepalive handling.
- The internal retrieval layer described above is a marker for future divergence. It is not part of the Render app parity changes unless ITS implements it separately.
- Any internal retrieval must be permission-aware. Avoid broad service-account retrieval that could expose documents to users who should not have access.

---

## 18. Suggested Acceptance Criteria for ITS

The internal clone can be considered aligned with the recent Render app changes when:

1. The app accepts and correctly frames PCN, PID, PAD, AF, Restructuring, DPF/DPO, PforR/P4R, MPA, and regional/multi-country operations.
2. Stage 2 and Stage 3 are instrument-aware and do not generate recommendations based on the wrong lending instrument.
3. Upload caps are: one primary project document, up to 10 package documents, and up to 3 contextual documents.
4. Secondary documents are distilled before Stage 1 model assembly.
5. CPF and RRA evidence can be reflected in Stage 3 recommendation metadata.
6. Express and Step-by-Step workflows both work.
7. The full automated test suite passes.
8. Any internal retrieval behavior is implemented as permission-aware backend retrieval and source injection, not as a model-side instruction to search internal systems.
