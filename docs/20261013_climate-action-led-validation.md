# Climate action-led report: validation and remaining acceptance

## Status

User approved implementation on 13 October. PR #83 remains draft, rollout held.
No additional provider calls or paid reviews were used. Both previously authorized
additional assessment runs were already consumed. Production/main and ITS are unchanged.

## Changes

- Detailed assessment groups complete, evidence-validated gap statements into climate
  design/delivery, access/inclusion/harm, and wider dividends where relevant. Uses
  existing question IDs and evidence links rather than guessed text classifications.
- Findings link to actual accepted priorities or proportionate evidence follow-up.
  Summary retains five full gaps; Detailed retains up to twelve validated findings.
  Full question coverage and watch cues remain in supporting analysis / Word appendix.
- Recommendation compilation targets three to five distinct material decisions when
  supported. Document hygiene does not count as a substantive priority by itself.
- An explicit, individually explained revise verdict allows one correction attempt
  using the same compiler/schema and original facts/scope. Corrected candidates pass
  the shared normalization, validation and admission gates, then independent review.
  Block/unresolved verdicts do not trigger correction. Passed actions are preserved;
  new IDs, duplicate IDs or expanded evidence references cannot replace them.
  Timeout/invalid correction output falls back to retained accepted actions;
  cancellation propagates. All calls retain the original absolute pipeline deadline.
- Both ratings use compact five-point cards in browser/export and a paired Word
  table. Unclear, Not expected and legacy Emerging remain unscored. Wider dividends
  stay optional and depend on scope. The old large sensitivity-only panel is removed.
- Removed duplicate normal-FCV priority cards shown after switching Climate to Detailed.
- New operational context targets 180–260 words. Older complete saved prose remains
  readable; no generated text is shortened by cutting sentences or qualifications.
- Several findings with fewer than three accepted priorities now show a review notice.

## Offline evidence

Focused correction cases prove one attempt, independent re-review, continued rejection,
unaffected-action preservation on timeout, rejection of expanded evidence, and cancellation.
Reader checks cover full findings, links, malformed saved references, exports and legacy scores.
Final full suite: **1,452 passed, 2 failed in 3,057.79s**. The two failures were
`test_result_download_header_wraps_inside_phone_card` and
`test_result_session_bar_wraps_inside_phone_viewport`: both stalled at
`Browser.close()` after gathering measurements, and their test helpers were stopped.
They were not counted as passes. The exact fixture HTML and the same geometry
assertions were subsequently checked in the existing connected Edge session:
header PASS at 320/390px; session bar PASS at 390px (button right edges 161/268/374,
inside the 390px viewport). A separate headless Edge retry was also interrupted;
it did not establish a clean standalone headless run. Final focused checks on the
last export/sidebar changes: **20 passed**. Git diff whitespace checks passed.
All five historical saved sessions also render through HTML and Word with their
original accepted-action counts preserved (0, 1, 1, 0, 2), paired ratings and complete
selected gap statements. This does not rerun or revalidate their underlying analysis.

Local Edge replay of the latest paid result confirms Summary and Detailed switching,
Priority 2 navigation/expansion, no duplicate card area, and no horizontal overflow at
320px and 390px. Local static preview has expected missing-API 404s; no hosted generation was invoked.
The browser's standalone HTML was downloaded. Word was generated via the actual writer
and checked structurally; Word pagination has not been visually certified.

Artifacts (untracked): output/playwright/20261013-action-led-replay-session.json,
20261013-action-led-browser-report.html, 20261013-action-led-report.docx,
20261013-action-led-summary.png, 20261013-action-led-detailed-v2.png,
20261013-action-led-mobile.png. Reproduction: 20261013_replay_action_led.py in that folder.
Final test log: output/20261013-action-led-final-regression.txt.

## Test deployment

Implementation commit e4e272914c4fedae3c1a6da714b6db45aac0e0c1 was deployed
to the branch test service only. Render deploy dep-db6vagajnfac73eda3n0 became
live at 2026-10-13T09:10:43Z. The /health response confirmed build e4e272914c4f,
status ok, quality mode and 150-second research budget. Analyze Python and CodeQL
passed for this implementation commit. PR #83 remains draft.

## Remaining acceptance

The saved example still has its original two actions, scores and seven gaps. It is a
presentation replay, not proof of new analytical breadth. A fresh authorized run must
produce at least three distinct supported recommendations for this case, show useful
coverage of material findings, and pass expert review. Do not fill the count with
minor document corrections or restore unreviewed candidates. Latest policy currency
has not been independently recertified against the restricted OPCS corpus.
