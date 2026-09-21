# ITS production-readiness handover: Climate Preview recommendation routing

Date: 14 August 2026
Branch: `codex/climate-summary-quality-fixes`
Accepted deployment commit: `c990d13`
Quality service: `fcv-agent-climate-preview` (`srv-d9usolvqj5pc738duvd0`)
Smoke service: `fcv-agent-climate-smoke` (`srv-d6gsivcr85hc73a2833g`)

## Handover decision

The reported silent recommendation-loss defect is fixed and the supported
Climate-only Express routing matrix has passed local and live acceptance. Both
Render services are live on commit `c990d13`. The branch is suitable for ITS
handover, subject to the standing product constraint that LLM output remains
probabilistic and requires expert review. The descendant commit adding this
handover file changes documentation only.

The release no longer treats a failed recommendation stage as a successful
zero-priority result. If the model emits candidates and every candidate is
suppressed, the run is marked `attention` and the reader explicitly states that
the recommendation stage is incomplete.

## Incident and root cause

The original Somalia DPF PID runs completed extraction, research, grounding,
and recommendation generation. Each model emitted four recommendation
candidates, but all four were rejected with
`DRAFTING_CURRENT_TARGET_INVALID`. The operational guidance registry contained
DPF Program Document targets but no DPF PID targets. The pipeline returned HTTP
200 and the reader showed no recommendations, making a routing failure look
like a valid analytical result.

Original affected assessments:

- Quality: `624654e5-6868-4f6a-92a1-7d8edd7938a4`
- Smoke: `c92b46cb-2ec5-418c-bfa1-a09e11cbf776`

## Implemented controls

1. `climate-guidance-v3` covers the complete supported active matrix:
   - IPF: PCN, PID, PAD, Project Paper, Additional Financing, Restructuring
   - PforR: PCN, PID, PAD, Program Paper
   - DPF/DPO: PCN, PID, PAD, Program Document
   - MPA: program-layer overlay for every supported base instrument
2. Unknown documents, unresolved instruments, TA, and ISR remain fail-closed.
3. A Somalia-shaped DPF PID regression confirms that valid current-document
   sections survive validation and admission.
4. Parsed candidates with zero surviving priorities add
   `RECOMMENDATIONS_ALL_SUPPRESSED`, set `review_status=attention`, and render an
   incomplete-stage warning in detailed HTML, five-minute HTML, standalone
   HTML, and DOCX.
5. A true zero-candidate compiler response retains the neutral no-priority
   result; the system does not manufacture recommendations.
6. Existing candidate-level controls remain active. Unsupported sections,
   actors, terminology, numbers, and evidence promotions can reject individual
   candidates without discarding valid recommendations.

## Verification evidence

### Automated gates

- Focused production matrix: `213 passed in 94.35s`
- Full repository suite: `965 passed in 93.93s`
- `git diff --check`: passed
- Credential-pattern scan of production-code diff: no matches
- Both Render event streams confirm `Deploy live for c990d13`

The focused suite covers route selection, drafting-target validation, the DPF
PID regression, all-suppressed diagnostics, the legitimate zero-candidate case,
reader assembly, HTML/DOCX warning parity, frontend messaging, and workflow
contracts. The full suite additionally covers unrelated FCV flows, exports,
sessions, timeouts, and application contracts.

### Live acceptance runs on deployed commit `c990d13`

| Service | Document | Assessment ID | Diagnostics | Outcome |
|---|---|---|---|---|
| Quality | Somalia DPF PID | `347299b5-3944-47b2-a6fd-35c98513e50b` | raw 3; parsed 3; valid 3; admitted 3; final 3; reviewer pass; no reason codes | UI routed `DPF / PID`; recommendations rendered with PID targets; no incomplete warning |
| Smoke | Somalia DPF PID | `4c451523-b48d-4cbe-930e-977035246ce6` | raw 5; parsed 5; valid 5; admitted 5; final 5; reviewer pass; no reason codes | UI routed `DPF / PID`; recommendations rendered with PID targets; no incomplete warning |
| Smoke | India STARS PforR PID | `30762e3c-30e6-4d9b-9fac-1ca62bc78ef3` | raw 5; parsed 5; valid 3; admitted 3; final 3; reviewer pass | UI routed `PforR / PID`; three recommendations rendered; two unsafe candidates rejected (`DRAFTING_CURRENT_TARGET_INVALID`, `DRAFTING_ACTOR_UNVERIFIED`) |
| Quality | Regional FSRP Phase 2 MPA PID | `6223995d-4a4b-4a74-866d-c9abc459b785` | raw 4; parsed 4; valid 3; admitted 3; final 3; reviewer pass | HTTP 200; three recommendations; one unsafe actor rejected; regional bank correctly unavailable and run degraded to accepted research-only grounding |

The MPA browser-control connection ended during the live wait, but the Render
service continued correctly and emitted the final diagnostics and HTTP 200.
The MPA route and base-instrument overlay are also covered by deterministic
matrix tests.

## Failure-mode acceptance

| Failure point | Required behavior | Verified result |
|---|---|---|
| Unsupported or unresolved route | No guessed IPF guidance | Fails closed |
| One unsafe candidate | Reject candidate, retain safe candidates | Observed in PforR and MPA live runs |
| Every parsed candidate suppressed | Mark run incomplete; do not show success | Automated pipeline and all reader surfaces pass |
| Model returns no candidates | Honest neutral zero-priority result | Automated regression passes |
| Regional operation has no single-country bank | Continue with bounded research-only grounding | Observed in MPA live run |
| PDF extraction | Complete or emit bounded warning/error | All four live files extracted without warnings |
| Semantic review required | One bounded review; fail safely on unresolved result | Live reviewers passed; conditional-review tests pass |
| UI/export parity | Same incomplete status in browser, HTML, and DOCX | Automated parity tests pass |

## ITS actions

1. Use commit `c990d13` as the accepted Render reference for handover review.
2. If the internal FastAPI build adopts the verified Climate pipeline, mirror
   `climate-guidance-v3`, the complete route matrix, the
   `RECOMMENDATIONS_ALL_SUPPRESSED` invariant, and the incomplete-reader state.
3. Preserve build-specific differences, including the internal OPCS retrieval
   path and provider defaults. No generic FCV delimiter, Stage-3 priority JSON,
   rating semantic, or `background_docs.py` constant changed in this patch.
4. Alert on `RECOMMENDATIONS_ALL_SUPPRESSED` and on completed runs where
   `parsed_candidate_count > 0` and `final_priority_count == 0`.
5. Treat free-instance cold starts and resource limits as infrastructure
   constraints. They are not application-correctness failures, but production
   deployment should use the ITS-approved service tier and monitoring.

## Residual product constraints

- No finite test programme can guarantee that future model output is defect
  free. The production control is deterministic validation plus explicit
  fail-loud behavior, not a promise that every model candidate will be usable.
- Individual candidates may be suppressed for legitimate safety reasons. A run
  is acceptable when valid candidates remain; it is explicitly incomplete when
  all parsed candidates are lost.
- Outputs remain advisory and require FCV specialist review before operational
  use.

## Technical references

- Design: `docs/superpowers/specs/2026-08-14-production-readiness-instrument-routing-design.md`
- Implementation plan: `docs/superpowers/plans/2026-08-14-production-readiness-instrument-routing.md`
- Route reference: `docs/reference/reference_backend_routes.md`
- Cross-build divergence log: `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`, section 33
