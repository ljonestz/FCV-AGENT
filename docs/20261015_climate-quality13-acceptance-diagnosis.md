# Climate quality13: production acceptance failed

## Method and result

Freeze the reviewer repair, run the full offline suite and exact-commit CodeQL,
calibrate the reviewer against saved failure classes, then submit one complete
public Great Lakes AF/IPF document through the normal paid service UI. Check the
native trace and accepted actions against the uploaded source, inspect presentation
and actual exports, and restore the original production deployment.

**The candidate is not production ready.** The one newly authorized full run is
consumed; all six separately approved reviewer-only calls are also consumed. No
further paid assessment or reviewer call is authorized. Do not merge to main,
deploy to ITS, admit this saved result as clean, or issue a successful ITS handover.

| Check | Evidence |
|---|---|
| Candidate | f463684a3c771a9e3c5d3119d9971c9aa02c4735 |
| Paid service deployment | dep-db87l10n74is73e456hg; live 07:03:36 UTC |
| Full run | 09c194d6-a4f0-40a7-bc9b-3eccfc952f6a |
| Submission | One; 2026-10-15 07:05:48.448 UTC |
| Completion | HTTP200; 07:10:45.692 UTC |
| Accepted priorities | Four; two contain material source-scope errors |
| Initial Summary | 198 words; no mechanical precheck defects |
| Native reader | Withheld; one meaning review, one rejected correction, no subsequent meaning review |
| Research | Failed; zero admitted claims |
| Offline suite | 1,591 passed in 339.79s; 157 checked source/fixture hashes unchanged |
| CodeQL | Success on exact candidate; workflow 38695745182, job 116291796296 |

The pipeline manifest reports 504,590 input and 39,478 output tokens across 13 call
metrics. This is manifest accounting, not a complete provider billing statement.
No second full assessment or diagnostic reviewer retry was submitted.

## Source-backed analytical blockers

File page numbers below refer to the 15-page public input, SHA256
70238ba18f619c36e0d678468779427134c5a3c77572c6e6cdfb3fd7457579c3.

1. REC-001 applies the Haut-Katanga market feasibility studies to Kasindi as well
   as Kasumbalesa/Kipushi. File p. 10 paragraph 22 and file p. 13 paragraph 27 limit those
   studies to the latter two sites. Kasindi is retained separately for Goma-fund
   redeployment. A useful screening question still needs the correct site/activity
   routing; usefulness does not cure the misstatement.
2. REC-005 proposes one prioritization rule across Burundi completion, Haut-Katanga
   works and Angola-axis sites. File p. 7 paragraphs 11-13 explicitly separate Burundi's
   US$60 million AF grant from DRC's restructuring within its existing envelope, affecting
   different recipients. A shared financing tradeoff is unsupported. A possible
   narrower DRC-only question has not been generated and independently accepted.
3. Readiness DIF-003 mistakes whole-million 59/1 and more precise 59.025/0.975
   presentations of the same 60 million allocation for a contradiction. The flag itself
   asks whether the figures are rounded. Explicit semantic acceptance admitted it
   despite the prompt's comparability rule.
4. DIF-004 treats a requirement to update ESCPs and a later statement of an updated
   ESCP as inconsistent. A requirement and completion can coexist. There may be a
   status clarification question, but these passages do not prove a contradiction.

DIF-002's different Component 1/3 amounts are not rounding variants and can justify
verification. REC-002's qualified O&M/flood-continuity question and REC-004's revised
outreach question are defensible. The old blanket no-siting-criteria claim and
unsupported displaced-trader/cancelled-site linkage did not survive in the four
accepted priorities. Extraction now retains the explicit criteria as PF-020.

## Reader review and correction failure

The meaning review mixed a real status defect with false positives:
- NARR-dividends calls infrastructure flood-ready although cited evidence only
  establishes revised specifications. That is a valid status objection.
- SUM-001 lists trader registration and Component 3 support separately. It does not
  assign registration to Component 3; that objection misreads a coordinated list.
- NARR-design's resource shift is documented explicitly in file p. 7 paragraph12 and
  file p. 10 paragraph 22 and entailed by cited facts. Treating it as an invented link
  repeats the reviewer calibration failure.
- The trust mechanism is expressly conditional and says the document makes no
  peace claim. A proposed action's possible future contribution is also conditional;
  neither statement treats the proposal as proof of an existing design feature.

The single text correction added US$152m and Components 1/3 to NARR-design. Its
original permitted numeric tokens were 2023, 2024 and 2. The application correctly
rejected the patch before merge/review with READER_CORRECTION_SUMMARY_NUMBER_UNSUPPORTED
and FINAL_READER_CORRECTION_SCOPE_INVALID. No repaired paragraph gained a clean
meaning pass. The validator must remain in place; relaxing it would hide the failure.

The targeted cases passed their specific expectations but overpredicted full-report
generalization. More isolated wording cases or another full paid rerun are not
supported as the immediate next step by this evidence.

## Research limitation and what telemetry does not establish

The search logged 18 citations, 2 search-result blocks and 4 packet sources, followed
by zero admitted passage selections and a failed research bundle. This proves
search activity and failed admission, not usable coverage of both countries.

The diagnostic fields_present=none is stale telemetry: it recognizes legacy
status/sources/claims fields, while the current classifier returns selections.
A valid selections object can produce that diagnostic. The raw packet/selection
response and rejection counts are not retained in the failed bundle, so the record
cannot distinguish missing short proof, empty selections and invalid selections.
Do not claim malformed JSON or a proven provider outage from these logs.

The code retains a nonempty partial bundle for inspection when a selection survives;
this run had none. Multi-country bank withholding is expected and separate. An
unrecognized composite country produces bank_country_unavailable before the
single-country bank scope check. No external claim is rescued or fabricated here.

## Presentation, exports and restoration

Summary correctly displays an unverified-brief fallback and a review-needed notice;
paired ratings and four initially open priority cards are present. Detailed/Summary
tab switching and closing/reopening the second Summary card passed. Specialist
subsections remain closed. Actual standalone HTML and DOCX contain all four titles,
the withholding notice and no private machine delimiters. These exports preserve
the analytical defects; agreement is not evidence of correctness.

The Word export rendered to 11 nonempty pages. A contact-sheet inspection found no
obvious overlap or overflow. No successful ITS handover Word document was authored.

Rollback dep-db87rsm89jmc73ciiij0 restored original main 1168a8f, live at
2026-10-15 07:17:29.278912 UTC. Render metadata verifies branch main and On Commit;
HTTP200 health verifies build1168a8f2ab2a. Preview remains 23958ae, auto-deploy off.
The feature branch/worktree and draft PR83 are preserved. No ITS deployment occurred.

## Evidence and next bounded work

Raw evidence stays local under output/playwright, including:
- 20261015-quality13-071143-state.json and quality13-session.json
- quality13-summary-browser.html and quality13-detailed-browser.html
- quality13-actual.html/.docx, summary/detailed screenshots and rendered Word pages
- 20261015-quality13-render-logs.json (12 ID-filtered entries)

Checksums/check results are in output/20261015-quality13-acceptance.json;
usage and rollback evidence are beside it. Source hashes still match the frozen
suite after the live run. Historical quality12 and targeted raw archives are intact.

Before any further paid validation, the saved full payload must drive an offline
repair design with explicit acceptance cases for site/activity scope, recipient and
financing scope, rounded amounts, compatible status statements, coordinated lists,
qualified mechanisms and correction expansion. Correction must preserve original
unaffected wording and prevent the present whole-record expansion failure. Research
failure diagnostics should count the current selections and retain bounded rejection
counts without source text. These are outstanding requirements, not implemented or
validated fixes. Further model usage needs a new explicit allowance; none is requested
or assumed by this record.
