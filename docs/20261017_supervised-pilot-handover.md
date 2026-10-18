# Climate-FCV supervised-pilot handover — 17 October 2026

**Decision: retain as a supervised-pilot candidate; do not declare production
acceptance or merge/deploy production yet.** Useful app-wide improvements are
implemented and tested. The latest Quality run produced useful recommendations
and valid exports, but independent reader review did not execute successfully.
One consequential phase-selection ambiguity remains in its recommendations.

## Demonstrated improvements

- Recommendation compiler v2.23 produces five substantive priorities with visible
  document/section edits and preparation decisions. Practical considerations is
  task-team prose, rather than an evidence-chain checklist.
- Analysis v2.13, judgments v2.17 and reader v1.11 support qualified indirect peace,
  trust, institutional, livelihood and resilience dividends, plus credible
  maladaptation risks. The fresh Quality reader demonstrates this framing, but its
  text was withheld because independent reader review failed. Its generation is
  evidence of improved writing, not end-to-end reader acceptance.
- Reader review v1.13, conditional review v2.22, admission v2.5 and renderer v2.25
  distinguish minor issues from consequential ones. Valid minor findings retain
  prose with an explicit notice; consequential findings withhold affected sections.
  Structural invalidity and block still withhold. Missing legacy severity remains
  consequential. Raw revise never becomes pass.
- Surplus redundant aggregate review codes no longer discard otherwise complete,
  anchored findings; a metadata inconsistency notice remains. Missing codes,
  unknown codes, target mismatches and stale quotes still fail closed.
- Browser Summary/Detailed, HTML, Word and version-bound review packet carry the
  notice. Native readers no longer repeat the unreviewed executive precursor.
- Start new analysis now rotates the assessment ID. This shared session fix also
  applies to normal FCV; normal-FCV analytical prompts were not changed.
- SDK-wrapped local pilot guard rejections are diagnosed as
  `pilot_request_blocked` and are not retried. Spend controls are unchanged.

## Actual live evidence

| Check | Result |
|---|---|
| Smoke | Completed on 63ad51a; five priorities; eight native calls returned |
| Smoke reader | Three minor findings plus an orphan aggregate reason code; exact offline replay after metadata fix retains opening and three answers with notices |
| Quality | Submitted once on f58c67a; five priorities; nine native calls returned; API stages completed |
| Quality reader | Generated, then withheld: both independent review attempts failed locally in 2–3 ms; no review pass |
| Research | Bank-only context; web research did not complete under the plain-text-only pilot guard |
| Exports | Word, standalone HTML, session and packet downloaded; packet hashes and snapshot binding verified; drift rejected with HTTP409 |
| Word layout | All 12 pages rendered read-only in Word and inspected as a contact sheet; no obvious clipping or empty page |
| Browser | Summary/Detailed switched; second priority closed and reopened; screenshot inspected; saved Quality session restored with exact ID, five priorities and original failure |
| Publication | `publication_approved=false`; no named human approval claimed |

Quality assessment: `6eac65e2-d1eb-4480-a98d-467a20c6c3e4`.
Quality snapshot SHA256:
`6ea0b4a95fbadb37789752151f85a19d3fff80caa338728b526fdb910ebd7e10`.
Smoke reused an old tab's assessment ID; distinguish its evidence by candidate,
timestamp and snapshot. The subsequent session-ID repair was verified live before
Quality and the Quality ID is new.

The guard reserved USD4.877094 of USD5 for Quality. An offline lower-bound replay,
omitting every source passage, still requires USD0.377404 for reader review against
USD0.122906 remaining. The SDK wraps this local rejection as APIConnectionError;
the offline SDK regression reproduced the misleading retry before the fix. This is
a testing-budget failure, not evidence of provider outage or successful review.
Research requests use a server web-search tool, which the current conservative
plain-text guard intentionally rejects. Do not call this full live research acceptance.

## Human source review before sharing

The latest Quality REC-001 credits five selected Phase 1 airstrips in one paragraph
but also describes an unsettled airstrip list and remaining airstrip options. PID
physical page 6, footnote 10 explicitly identifies five selected Phase 1 airstrips;
footnote 11 leaves cities under discussion. Separate already-selected assets from
open city/activity choices and later-phase sequencing. Preserve the useful advice
on applying hazard, displacement and jurisdiction considerations to design.

Other checked premises include the prior SURP II jobs record (not current targets),
the planned MOF platform (not established authority), early-warning links and the
proposed extension to community reach, indirect effects of works and O&M frameworks.
The remaining four recommendations are useful qualified proposals on these topics;
do not discard them solely because REC-001 requires correction. This source check
is not an exhaustive factual certificate or named organisational approval.

The older REC-004 claim that local airstrips are excluded from airport revenues
remains a recorded semantic miss. The newer run not repeating it does not establish
reliable detection. Synthetic calibration and structural checks cannot certify it.

For each pilot output, the reviewer should check the small set of decision-bearing
premises: phase/asset scope, funding availability or exclusion, existing authority,
commitments, beneficiary eligibility and claimed outcomes. Qualified mechanisms and
minor editorial differences do not need blanket rejection. Resolve known findings
in the final version and bind named approval in the existing authenticated workflow
to that version's packet hash and exact shared files. An edited report needs a new
bound packet; approval of an earlier snapshot is not transferable.

## Remaining acceptance and smallest next step

Do not start another detection architecture or another calibration loop. First make
the paid acceptance harness fit the actual pipeline offline: reserve the complete
stage/retry/correction path and explicitly handle web-tool pricing, or document and
approve a deliberately bank-only pilot scope. Preserve atomic ledgers, consumed
reservations and no-refund accounting. Do not remove the guard, increase a consumed
ledger, or silently assume leftover allowance authorizes a new campaign.

Then use the remaining full-run authorization only for a concretely prepared Quality
acceptance on the exact candidate, with independent reader review completing and
browser/export/session checks. A smaller isolated reader review could diagnose the
last stage cheaply, but would not replace that full-pipeline result. No paid action
is queued. No further call is justified simply to obtain a model pass.

Until then this is suitable for technical review and planning a supervised pilot,
not unconditional production release. Production promotion remains a separate
explicit user decision after the acceptance gap and human review are resolved.

## Verification, spending and deployment

- Full suite on f58c67a: **1,832 passed**, four known Chromium-driver hangs excluded,
  230.55 seconds. No complete browser-suite pass claimed.
- Final guard diagnostic fix on **03618ab85d05c5d08a1fb35d515a1887c703033b**:
  **50 focused tests passed**, including the actual SDK with a mock transport and
  zero network calls. Full suite was not repeated for this bounded adapter change.
- New campaign used **2 of 3 full app reviews; 0 of 5 smaller calls**. Upload helper
  calls are included in the full-run scope. The third full run remains unused.
- Conservative reservations: Smoke USD0.900999 + Quality USD4.877094 =
  **USD5.778093**, not invoice charges. Historical campaign spend is separate.
- Preview deployed 03618ab, branch `fix/climate-opcs-parity`, auto-deploy off.
  Post-campaign blocker restored: budget **1 microUSD**, new explicitly blocking
  ledger `/tmp/fcv-readiness-post-campaign-blocked-20261017.sqlite`. Health returned
  HTTP200, build 03618ab85d05, Quality mode. No provider call used to verify blocker.
- Production remains **1168a8f2ab2af0bcc6a3a174c4b2eeacd9403205**, unchanged.
  PR83 remains draft; branch/worktree retained. An earlier attempt to clear preview
  budget settings was rejected by automatic approval review; controls stayed active.

## Local review artifacts (not in Git)

All under `output/20261016-ipf-pilot-live-preflight/`:

- `readiness-20261017-f58c67a-quality-report.html` — actual exported reader,
  including honest fallback; not the unreleased generated narrative.
- Same prefix: `report.docx`, `report.pdf`, `review-packet.zip`, `session.json`,
  `state.json`, `verification.json`, `guard-audit.json`, `summary.png`,
  `second-priority.png`, `word-contact.png`, `word-page-*.png`.
- `readiness-20261017-63ad51a-smoke-*` — first run and exports.
- `20261017_production-readiness-authorization.json` — campaign counts and scope.
- `20261017_readiness-final-full-tests.txt` — broader test result.

Keep raw outputs, reports, responses and screenshots untracked. Preserve pre-existing
untracked `tests/test_climate_final_reader.py`. No raw artifact belongs in PR83.
