# Climate OPCS parity validation - 12 October 2026

Base: main `1168a8f`. Candidate branch: `fix/climate-opcs-parity`.

## Scope and method

Verified Climate context, guidance, prompts, recommendation validation and shared
reader. No standard-route changes. The maintainer authorized local OPCS source
access for this session. Policy sources were read locally; no source PDFs or raw
internal text are included in the repository.

## Policy basis

- IPF and PforR One-step / Two-step Preparation procedures (April 2026), Section I:
  OIS boundaries, risk rules, AF, MPA, FMRF and hybrid component distinctions.
- DPF Procedure (May 2026), Section I and processing tables: April 18 boundary,
  Program Document and instrument-specific processing.
- Environmental and Social Directive/Procedure for IPF (January 2026), scope and
  Annex III: ESF trigger, exceptions and PforR IPF-component E&S instruments.
- Multiphase Programmatic Approach Guidance (November 2021 revision), page 4:
  DPF cannot finance an MPA.
- Preparation of IPF Guidance (June 2026), page 15: climate co-benefits and the
  climate-indicator check when the evidenced share is at least 20%.
- Preparing the IPF Project Paper (July 2026), page 11, and PforR Program Paper
  (June 2026), page 13: Paris Alignment and climate appraisal evidence.

The curated October index warns that it lags the live PPF library. These changes
are grounded in inspected local documents, not certification of all latest policy
revisions. OIS-as-Concept-Decision wording and the exact April 17 boundary retain
the existing Help Desk caveats. TA applicability and guarantee routing remain
outside resolved coverage; no automatic TA-to-IPF conversion was added.

## Verification

- Original audit: 264 existing tests passed; additional probes exposed gaps.
- New regressions initially reproduced 16 failures (2 cases already passed).
- Focused candidate tests: 229 passed after final MPA/FMRF and E&S hardening.
- Full suite on 7d1296a: 1,355 passed, 8 failed (906 seconds). Three stale
  wording assertions were aligned with the applicable-review label and scoped
  PforR hybrid exception; all 113 tests in those three files then passed.
  The remaining five frontend fixture failures reproduce on the untouched
  checkout: two missing SR_TERM_S_TIP fixtures, two obsolete horizon-render
  fixtures, and a null checkpoint fixture. The full suite is not green.
- Live smoke completed on the original candidate; quality is held. Only `fcv-agent-climate-smoke`, service
  `srv-d6gsivcr85hc73a2833g`, URL `https://fcv-agent-1.onrender.com`, is authorized
  for these checks. The service now tracks `fix/climate-opcs-parity`, candidate
  `7d1296ab0597`, with smoke mode confirmed by /health.
- Production and ITS have not been deployed or modified.

## Shared-build implications

Mirror verified Climate resolver, registry, prompt, hybrid validator and reader
changes together only after acceptance. Preserve ITS retrieval differences.
Do not port just the component prompt exception without its deterministic guard.
No external payload field, delimiter, rating or provider-call change is intended.

## Great Lakes live result and remaining acceptance limits

The user replaced the Somalia test with the original checkout's
`test_documents/P174814-great-lakes-pid-20261007.pdf`. This 15-page appraisal PID
is internally dated 10 July 2026 and concerns P174814 Additional Financing Request
1. It names Burundi and DRC and identifies IPF. No explicit OIS creation date or
processing-model marker was found; the filename date is not an OIS date.

Smoke assessment `6a02d352-3456-4ef6-af4f-4bd379c0ccbf` started at 13:23:41 UTC
on 12 October and completed all three stages. Extraction returned 48,288 characters
with no warnings. The initial country was Unknown, the bank was unavailable, and
web research passed its gate on the second attempt (research-only grounding).
The saved reader correctly identifies AF/IPF but incorrectly labels country scope
single while its narrative names Burundi and DRC. Preparation regime remains
unresolved and processing model unknown. This run therefore does not establish
new-appraisal routing or quality acceptance. Do not run quality until the scope
defect is resolved; no quality call was made. The five-point scale added afterward
has deterministic verification only, not a fresh live model run.

Local artifacts: `output/playwright/.playwright-cli/fcv-session-2026-10-12.json`,
the Summary screenshot `page-2026-10-12T13-30-41-595Z.png`, and subsequent compact
layout screenshots `20261012-compact-climate-summary.png` and
`20261012-compact-climate-mobile.png`. Raw artifacts are not committed.
Standalone export acceptance is still pending.

## Approved sidebar follow-up

Both normal FCV and verified Climate now retain sidebars in Summary and Detailed.
Climate cards have short glosses and collapsed full rationale; mobile retains a
collapsed ratings section. Responsiveness is an additional contribution whose
expectation depends on scope, often a sign of going above and beyond.

At the user's request, the Climate responsiveness contract changed to five points:
very_limited, limited, moderate, strong, very_strong; not_expected and unclear remain
unscored. Prompt/schema version is climate-judgments-v2.5. This supersedes the
no-rating-change statement above. Historical Emerging results remain legacy and
unscored in the UI, requiring reassessment. Normal FCV's existing scale is unchanged.

Follow-up verification: 99 focused pipeline/schema/runtime/sidebar tests passed;
8 final sidebar tests passed. Two missing frontend fixture constants were repaired;
the three other pre-existing full-suite failures remain outside this change.
The full suite has not been rerun after this follow-up. Local saved-session replay
confirmed desktop Summary/Details and the mobile disclosure. The local static
preview has expected API 404s and is not a backend acceptance run.
