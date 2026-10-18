# ITS handover: bank-based supervised IPF pilot

## Decision

Recommend handing over the tested reference application for a controlled,
human-supervised IPF pilot. This is bounded acceptance of the bank-based workflow,
not certification of automated factual detection, live web research, an ITS model
port, or unrestricted publication. Production has not been promoted. PR83 remains
draft and the branch/worktree are preserved.

The user accepted bank-based operation on 18 October and capped the final run at
USD5. All three authorized full-run slots are now consumed; zero separately
submitted smaller calls were used in this readiness campaign. Do not submit a
fourth full run or reuse any consumed lock/ledger.

## Exact candidate and evidence

- Application: `856f583d0aa64e896f58b55d75d7a47d47a791ee`.
- Bank: `12a804fe92bacfdaf0bec7926725d8a7a9376fe4`.
- Preview: `https://fcv-agent-1.onrender.com`, branch `fix/climate-opcs-parity`,
  auto-deploy off; acceptance deployment `dep-dba8493rjlhs7399an8g`.
- Quality assessment: `e81c8845-2780-493d-b367-477aa7254cec`, standard complete
  Somalia STAIRP concept PID, 18 October 08:29:07-08:32:37 UTC.
- Explicit `CLIMATE_RESEARCH_MODE=bank_only`; both assessment and reviewer used
  `claude-sonnet-5-5`. Ten native calls returned, including bounded correction and
  final re-review; all three stages completed without a transport error.
- Conservative reservations: USD4.467768 against USD5, including upload helpers.
  These are reservations, not invoice charges. Prior campaign reservations remain
  separate; no ledger was refunded or replenished.
- Packet snapshot SHA256:
  `5efa1e5f25ad4ed9a5c6b90089c6fb0705128387f085b46bdab6adaaa5009c20`.

Raw evidence is untracked under `output/20261016-ipf-pilot-live-preflight/`, prefix
`its-bank-20261018-856f583-quality-`. It includes observed API/SSE, state, actual
HTML/Word downloads, review packet, saved session, Render logs, browser screenshots,
Word PDF/page images and `verification.json`. No raw reports or screenshots belong
in Git.

## Demonstrated improvements

Four priorities survived. Their visible prose names a document section, concrete
edit and preparation decision. The urban priority expressly excludes reopening
already-selected Phase 1 airstrips. Maintenance advice asks how responsibilities
and financing reach the assets; it does not assert the historical unsupported
airport-revenue exclusion. Hiring advice treats SURP II figures as precedent;
platform participation and decision roles remain proposals. Peace/social dividend
and inclusion answers offer useful conditional livelihood, cooperation, trust and
fair-access pathways. Off-footprint flood and settlement impacts are risks to
examine, not asserted harm.

Direct source comparison used printed PID pages 5-6, including footnotes 10-12:
five selected airstrips, open city choices, prior-operation employment shares,
planned coordination platform and O&M/revenue frameworks. This fresh case improves
generation; it does not prove the earlier semantic detection miss is solved.

## Remaining limitations and human disposition

The conditional recommendation reviewer returned pass; the final reader reviewer
returned **revise**, with one minor opening issue and one consequential designation
for wording that implied planned airstrip upgrades were underway. The application
retained the opening with a notice and replaced only the first core-answer prose
with its shorter evidence-based fallback. The other answers and all priorities
remain. Do not describe this as a clean model pass or complete native narrative.

The objection to criteria-based identification of nine airstrips is overstrict:
footnote 10 supports selection using those criteria. The implementation-tense issue
is reasonably qualified as planned work, but the automated reviewer classified it
more severely. A human should review that disposition before sharing. Existing
precision cleanup also removes some valid phase/pillar digits in suggested drafting
(for example, "Phase would build"). This is an editorial defect; verify labels
before copying draft text. No further paid calibration is proposed today.

Reviewers must confirm consequential project scope, funding, mandate, commitment,
eligibility and outcome claims against the source, and check current context against
current sources. The bank is a preview evidence release, not approved current
intelligence. Keep the visible limitation. Record named approval in the existing
authenticated organisational workflow against the exact packet and file hashes.
`publication_approved` remains false. An edited report needs a newly bound review
record; do not silently alter these acceptance artifacts.

## Verification and release boundary

- Full candidate suite: 1,846 passed; four previously hanging Chromium-driver tests
  explicitly deselected. No complete browser-suite pass is claimed.
- Actual Summary/Detailed tabs and a non-first priority/disclosure exercised.
  Practical considerations use readable prose. An initial click closed an already
  open card; state-aware retry succeeded, with no application change.
- HTML, Word, review packet and session downloaded. All packet hashes verified,
  snapshot stamps present in packet HTML/Word, deliberate reader drift rejected409.
- Saved session reloaded with the same assessment, four priorities and revise status.
- Word rendered through Microsoft Word: 12 nonempty pages visually inspected, with
  no visible clipping. Long priorities span pages; that is retained for this pilot.
- Explicit no-live-web limitation appears in browser-derived report data, HTML and
  Word. Live research was not exercised or accepted.

Preview spending was returned to a 1-microUSD blocker through deployment
`dep-dba8bp0m7kps73fsasd0`, confirmed live with health200 on the same candidate. The consumed
USD5 ledger must never be reused. Production remains `1168a8f2ab2af0bcc6a3a174c4b2eeacd9403205`.
Production promotion requires the user's explicit decision on the tested candidate
and an agreed operational spending allowance. No automatic merge/deploy or ITS
message is authorized by this handover.

## Delivery

Source archive: `20261018_ITS-Climate-FCV-856f583-source.zip`, 609 tracked files
including the pinned bank; SHA256
`15591a762342a85252a9da8f72cb9be1079d2caf73bf785d3c3f9d9faa24314b`.
The archive is the tested application revision. Later handover-only commits do not
change it. Follow `docs/20261018_ITS_bank-pilot-operating-guide.md` for installation,
model/mode settings, human review, ITS port boundaries and rollback. No credentials
are included. Reference acceptance does not certify a FastAPI/Gemini port or change
ITS-specific OPCS retrieval.
