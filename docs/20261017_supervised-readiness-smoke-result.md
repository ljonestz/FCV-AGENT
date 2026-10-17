# Supervised IPF readiness: Smoke stopped the campaign

The user approved the prepared preview-only deployment and one Smoke assessment,
followed by one Quality assessment only if Smoke completed technically. The
candidate was `853771e5bedc1c3437028bfc6c12a611d677dd67`, recommendation compiler
v2.23, conditional reviewer v2.21, final-reader reviewer v1.11, renderer v2.21.

One paid Smoke assessment ran. It returned an incomplete Recommendations Note:
five structurally admitted candidates became zero visible priorities after an
inconsistent conditional review. Quality was not submitted. This is not full
live acceptance or production readiness, and no additional assessment is queued.

## Verified execution and failure

- Preview `srv-d6gsivcr85hc73a2833g`, branch `fix/climate-opcs-parity`, auto-deploy off.
  Smoke deployment `dep-db9qnbjncjis73ab216g` became live at 17:10:25 UTC on 17 October.
  Both deploy metadata and `/health` confirmed candidate `853771e5bedc` and Smoke mode.
- Fresh assessment `8dda1436-c4b5-4342-93f1-deb7953c21c9`, submitted once at
  17:12:42 UTC. Express returned stage completions 1, 2, 3 and `express_done` at
  17:15:11 UTC, with HTTP 200 and no transport error. The terminal payload and UI
  explicitly said recommendations were incomplete; HTTP completion is not acceptance.
- Complete standard Somalia PID/IPF/MPA PDF: eight pages, SHA256
  `61e3ee924d114ddbdf19dd6835d2cb051a852f8a1fcd8810b3e8b77b2de994e1`.
  Server extraction confirmed 21,988 characters and no extraction warnings.
- Climate research returned six admitted claims from three sources in one attempt;
  grounding was bank+research. This proves research operation, not verification of
  every current-context assertion.
- All ten native Climate calls returned, each on attempt 1, using actual
  `claude-haiku-5-5` model metadata. Native usage was 255,394 input and 24,758 output
  tokens. This excludes upstream research/helper usage and is not an invoice amount.

The exact conditional response matters. Its five per-core records all said
`supported`, cited valid source blocks and appeared in `passed_core_ids`. All
readiness records were also declared passed. The top-level verdict nevertheless
said `revise`, with empty issues, object IDs and reason codes. The pipeline's
unresolved-target fallback consequently targeted every priority and suppressed
all five, reporting `SEMANTIC_REVIEW_TARGET_UNRESOLVED` and
`RECOMMENDATIONS_ALL_SUPPRESSED`.

Offline replay decoded the complete 65-block source array from the bounded trace
and ran the real admission helper. All five core records passed; none had unknown
source IDs or invalid core structure. Do not diagnose this as fabricated source
references or failed parsing. It is a contradictory aggregate reviewer result
handled by an existing fallback. No admission rule or reviewer prompt was changed.

The final reader independently remained withheld after its bounded correction.
Its remaining issue concerned the inference that estimated overflight-reform
revenue would be enough to maintain assets. Record that as unresolved reviewer
feedback, not as an independently established factual error or a detection success.
Other validation warnings included suppressed fact/absence evidence and a Summary
paragraph-count fallback. They remain in the saved canonical artifact.

## What this demonstrates and what it leaves open

The complete document, research, native calls, UI completion, tab switching and
diagnostic export paths operated. All five raw candidates named a document/section
and concrete edit. Their narratives were 257, 210, 213, 201 and 201 words, below
the preferred main-FCV depth in this Smoke sample. Word targets remain advisory.
No priorities survived to exercise a non-first card or Practical considerations
in the fresh live output. Fresh Quality writing and useful end-to-end output are
therefore still untested.

The previously approved fuller editorial example, prose disclosure and narrow
negation display repair remain demonstrated locally. The pre-run broader suite
had 1,799 passes with four known hanging Chromium-driver tests excluded. No
application code changed during this campaign and no complete browser-suite pass
is claimed.

The earlier real REC-004 airstrip-revenue exclusion remains a semantic detection
miss despite its model pass. This run does not resolve it. Preserve the maintenance
question and have a human remove or qualify any unsupported exclusion; do not
discard otherwise useful recommendations merely because that premise needs repair.

## Exports and review boundary

The original incomplete session, standalone HTML, DOCX and review packet were
downloaded and preserved. Each export endpoint returned HTTP 200. The packet's
snapshot and report hashes verified. A cloned reader with changed visible text
was rejected live with HTTP 409 / `READER_SNAPSHOT_MISMATCH`, without altering the
original assessment. Summary and Detailed screenshots were inspected.

Packet snapshot SHA256:
`1150c4120845739de456d3b364d4cb04cbde5183c439c156591ba2d9ea56f498`.
`publication_approved=false`; status draft. Packet-internal reports carry the
snapshot stamp. Standalone exports do not carry that stamp, so their actual file
hashes are recorded separately in the verification artifact. Never imply that
the packet manifest covers a different standalone file automatically.

Word content, draft/incomplete/Smoke notices and packet hashes were checked. No
visual Word-layout acceptance or complete recommendation/export acceptance is
claimed for this incomplete run. Named human source review and approval through
the existing authenticated organisational workflow remain pending, bound to the
actual snapshot and report files before sharing.

## Restoration and spending

The experimental guard was temporarily disabled under the approved plan because
it rejects web research. No hard invoice-dollar ceiling was claimed. Historical
reservations and consumed ledgers were not reused or reset.

After the run, the preview configuration was merged back to Quality mode, empty
model overrides, `FCV_PILOT_BUDGET_MICROUSD=1`, and fresh blocking ledger path
`/tmp/fcv-ipf-readiness-20261017-853771e-post.sqlite`. Restore deployment
`dep-db9qrvu1egvs738a1kog` became live on the same commit at 17:20:18 UTC.
Health confirmed `853771e5bedc` / Quality. The merge acknowledgement, live deploy
and health are the restoration evidence; the live request hook was not independently
inspected or probed with a provider request.

Production was not changed and its read-only health still reported `1168a8f2ab2a`.
No merge or service-plan change occurred. Keep the branch and worktree. The Quality
submission lock was never created; the consumed Smoke lock remains consumed.
No automatic repeat or additional paid assessment is authorized by this result.

## Smallest practical next step

Use this exact saved response for an offline regression of contradictory-review
handling. Prepare a narrow change that keeps explicitly passed cores available
for supervised human review while exposing the inconsistent aggregate result.
Do not silently turn an unexplained `revise` into a clean pass, weaken source
checks, add another detection architecture, or discard all useful advice.

Resolve the reader's separate financing feedback through source review. Only
after a concrete handling fix and appropriate offline checks should a newly
approved Quality assessment be proposed. Full pipeline/export acceptance and
human version/file-bound approval remain necessary for the controlled IPF pilot.

## Artifact locations

All raw artifacts remain untracked under
`output/20261016-ipf-pilot-live-preflight/`, prefix
`ipf-readiness-20261017-853771e-smoke-`: `observed-api.json`, `state.json`,
`session.json`, `report.html`, `report.docx`, `review-packet.zip`,
`offline-diagnosis.json`, `verification.json`, `render-logs.json`,
`export-api-observations.json`, and `browser-detailed-selected.html`.
The earlier `browser-detailed.html` capture was made while Summary was selected;
its name does not establish which tab was visible.

Screenshots under `output/playwright/.playwright-cli/`:
`page-2026-10-17T17-15-58-832Z.png` (Summary) and
`page-2026-10-17T17-22-16-631Z.png` (Detailed). Both inspected. Browser console
contained a missing favicon and the deliberate stale-reader 409; no application
JavaScript error was observed. An automation selector initially used button role
for the Detailed tab; using its observed ID succeeded. This was not an app defect.

Offline scripts: `20261017_diagnose-readiness-smoke.py` and
`20261017_verify-readiness-smoke.py` completed successfully with zero provider
requests. Preserve pre-existing untracked `tests/test_climate_final_reader.py`
and all historical output. Do not stage raw artifacts or these local run helpers.

## Later offline repair of the contradiction

The user authorized addressing this failure. The change is confined to initial
review fallback and shared reader warning projection. An otherwise empty revise
can retain cores only when all core IDs explicitly pass valid source/record
admission, there are no admission errors, and reason codes, object IDs and issues
are explicitly empty arrays. A block, a substantive global concern, unknown
targets or missing/malformed coverage still uses existing withholding behavior.
Correction-review acceptance requirements are unchanged.

The result retains the raw revise verdict, validation attention and
SEMANTIC_REVIEW_VERDICT_INVALID. It does not certify a pass or start another model
call. The shared reader marks recommendations partial and uses the existing
Recommendations need review surfaces in browser, HTML and Word. Its notice says
automated recommendation review was inconclusive and asks for source checks before
sharing. It does not incorrectly say actions were withheld when all remain. A
short priority list cannot overwrite this warning with a generic coverage message.

No schema, field, prompt, call budget or normal-FCV behavior changed. Runtime
admission metadata is climate-review-v2.3 and renderer climate-reader-v2.22;
recommendation compiler v2.23, conditional-review prompt v2.21 and final-reader
review prompt v1.11 remain. Publication approval stays false.

Two regressions failed before implementation: the five-core case suppressed all
five, and the reader incorrectly labelled retained recommendations complete.
Four malformed/block boundary cases already passed. The connected pipeline,
reader/export and core-admission suite passed 252 checks. Two expanded warning
cases additionally cover a short list with several grounded gaps.

Final broader suite: 1,806 passed, four known hanging Chromium-driver tests
explicitly excluded, 339.83 seconds. No complete browser-suite pass is claimed.
JUnit artifact: output/20261016-ipf-pilot-live-preflight/20261017_review-contradiction-final-tests.xml.

The exact saved candidates and contradictory conditional response were replayed
with fake clients and socket access blocked. Upstream payloads were reconstructed
from admitted canonical records because raw upstream model responses are not all
available. Drafting was already merged in the saved candidates. This is a software
replay, not fresh generation or an identical replay of the whole live run.

All five candidates retained their original minimum action, narrative, limitation
and caution. The revise/attention result stayed visible and the separate final-reader
meaning failure remained a fallback. Packet generation returned 200; a cloned stale
reader returned 409; packet hashes and publication=false verified. Replay used the
real JSON boundary and existing canonical snapshot helper. Original Smoke files
were hashed before/after and were unchanged.

New untracked artifacts in the same output folder use prefix
20261017_review-contradiction-replay-: canonical.json, reader.json, browser.html,
report.html, review-packet.zip and audit.json. Snapshot SHA256:
e24fe6ec080ce7622a7614b1ad38b2ea0db8ef9d4460e75d8325cca7c3b13c69.
The helper is 20261017_replay-review-contradiction.py. All provider access was blocked.
Local Edge inspection confirmed the notice, all five priorities and the second
priority's Practical considerations. Screenshots inspected:
output/playwright/.playwright-cli/page-2026-10-17T17-50-01-964Z.png and
page-2026-10-17T17-51-11-574Z.png. Word warning and priority text checked in the packet;
no visual Word-layout acceptance is claimed.

The historical live Smoke remains incomplete. No paid call or deployment was made
for this repair. The independent reader financing feedback, earlier consequential
REC-004 detection miss, full Quality/live export acceptance and named human
version/file-bound approval remain outstanding.
