# Climate quality7 paid acceptance and follow-up

## Outcome

One user-authorized paid run was submitted on 2026-10-14 at 10:37:36.284Z.
Assessment ID: 64d33aed-a786-4d29-a2ad-4fb550ce1afc.
Test build: 3805f7506dd5f9b4003016cf247623f8dec17d26, quality mode.
Source: latest Great Lakes AF PID, 414,268 bytes, SHA256
70238ba18f619c36e0d678468779427134c5a3c77572c6e6cdfb3fd7457579c3.

The run FAILED acceptance at 10:41:41Z in Stage 2 with
READER_INTEGRITY: CURRENT_DRAFTING_INCOMPLETE. Stage 3 did not complete.
No retry or second paid generation was submitted. The new paid allowance is consumed.
Main/production and ITS remain held; PR 83 stays draft.

## Observed evidence and limits

Research passed on its bounded second attempt: two sources, four exact received
passages, both beneficiary countries covered, accepted research-only grounding.
The regional country bank was unavailable with the explicit bank_country_unavailable
reason. This is separate from research failure. Received research spans a 2022 World
Bank Burundi report and a DRC flood-operation source titled 2024; it is contextual
historical evidence, not confirmation of current project-site conditions.

The completed native assessment was lost at the runtime reader gate. A plain
ValueError was raised before the assessment or manifest reached the browser; the
workflow emitted only the error. No assessment cache or recovery endpoint exists.
Therefore accepted action count, correction recovery, native Summary and semantic
findings cannot be reviewed or accepted for this run. Do not infer quality success
from research admission, processing duration or the specific reader error.

Available original session and failure screen are preserved under output/playwright:
20261014-quality7-failed-session.json / 20261014-quality7-failed-screen.png.
Submission metadata, assessment-filtered Render logs and source extraction are saved separately. Raw outputs are
untracked; do not commit source documents, sessions, logs or generated reports.

## Reproductions and follow-up fixes

- The actual native core-only three-decision fixture was extended through runtime
  normalization, reader validation, HTML and Word. It reproduced the exact paid
  failure. The reader still required optional drafting on a confirmed route.
- Reader 2.17 carries final-reader-v1 into its validation model. Absent optional
  wording no longer erases accepted native decisions. Supplied malformed wording
  still fails; legacy readers retain their strict contract and all core guards remain.
- Native final prose now requires the complete design/dividends/inclusion theme
  package. A supported Summary with an empty or partial findings array is withheld.
- A typed reader-integrity error carries the completed assessment to the same caller
  in a diagnostic-only SSE event. Manual Save Session preserves it separately.
  It never activates a reader, enters report/follow-on payloads or automatic local
  storage, and raw text stays out of exception messages/server logs. Load/reset/new
  run lifecycle is tested. This cannot retroactively recover quality7.
- The stale completed-session label is cleared on reset. Summary no longer promises
  draft wording where it was withheld.
- Native context now preserves all cited source metadata, evidence limitations and
  relevance horizons. Missing publication dates leave current conditions unverified;
  present-tense historical quotes cannot establish a currently affected project site.
  Quotes and source/reference entitlements are unchanged. No extra model call added.

## Verification and release decision

Reader/diagnostic focused run: 277 passed before the later context metadata change.
Context-focused run passed 220 checks and exposed an old manifest-version fixture.
All eight metadata/manifest checks passed after aligning its expected prompt versions.
Full regression: **1,502 passed, one isolated session-load fixture failed**, in
989.57 seconds. That fixture lacked the new diagnostic global/helper. After
alignment and explicit diagnostic-only load assertions, all 13 checks in the
session module/related helpers passed in 24.70 seconds. No runtime code changed
after the full run. Final research-module check: 52 passed in 120.38 seconds,
including four official-domain regressions; existing packet guards already reject
look-alike publishers, so no domain-classifier code change was needed.
Static read-only review found no further null-draft rendering/export blockers.
The previous 1,493-test full result did not exercise the native no-draft runtime
reader gate; the extended integration regression now closes that coverage gap.

A subsequent offline correction and test deployment can establish this deterministic
failure is repaired. They cannot establish that the lost paid output meets the
source-based three-priority/native-Summary quality benchmark. Rollout remains held.
No additional paid assessment is authorized in this session.


## Public-source verification limits

The Burundi temperature-series timeframe and the report's 2022 publication were
checked against the [World Bank report](https://documents1.worldbank.org/curated/en/099930006302237433/pdf/P17682007885e00780b1cc093a09277df1a.pdf).
The [DRC flood-operation citation](https://reliefweb.int/report/democratic-republic-congo/drc-floods-tanganyika-2024-dref-operation-mdrcd044)
was received with exact source excerpts, but independent opening failed through
both web verification and Edge. Its title names 2024; the received publication date
was blank. Do not treat these passages as verified current project-site status.

The final bounded static review found no remaining diagnostic-publication or
nullable-draft blocker. It did not run tests, access servers or call a provider.
