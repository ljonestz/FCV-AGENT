# Climate reader simplification

## Approved scope

The user approved flowing, first-reader-friendly context and findings, removal of
project-detail disclosures and supporting analysis, and main-FCV-style priority
cards. This supersedes the visible supporting appendix in the earlier narrative
findings candidate. Internal evidence, canonical questions and validation remain.

## Implementation

- Judgment instructions no longer request a four-dimension recap or explicit
  rating labels in context and Summary prose. They discourage semicolons and
  label-and-colon verdicts, and explain unfamiliar concepts in plain language.
- Recommendation instructions specify a first paragraph explaining the gap or
  opportunity and subsequent paragraphs describing action and the concrete result.
  Literal completion cues such as "Done looks like" are prohibited in narrative.
- Browser and Python HTML priority cards use "Why this matters" and "What the
  team could do", with structured fields, drafting and project-cycle details in
  the closed Recommendation details panel. Word uses the same sections followed
  by its detail block. Existing saves use complete structured text when needed.
- Three question-led findings remain. Per-theme project detail and the supporting
  analysis/watch appendix are removed from Detailed, HTML and Word. Summary watch
  behavior is unchanged. Method retains coverage, limitations and sources without
  repeating pathway analysis. The full case has six visible sections.
- Mobile priority and reference-panel padding is reduced. Print opens retained
  disclosures and restores their prior state.
- Versions: judgments 2.11, recommendations 2.13, reader 2.11. Other prompts and
  schema/admission/deadline contracts are unchanged. No extra provider calls.

## Preview and checks

New artifacts under `output/playwright/` (untracked):

- `20261013-simplified-climate-browser-report.html`: actual browser HTML download.
- `20261013-simplified-climate-report.html` and `...-report.docx`: Python exports.
- `20261013-simplified-climate-session.json` and `...-reader.json`: editorial replay.
- `20261013-simplified-priorities-final.png` and `...-mobile-final.png`: screenshots.
- `20261013_replay_simplified_reader.py`: reproducible editorial preview.

The preview rewrites context, overview, finding narratives and recommendation prose
from the saved evidence. It preserves the original scores and two accepted actions.
It is labelled as editorial, not fresh model generation. No third action is invented.
The operational context is 232 words.

Edge confirms six sections, no removed disclosures, paired priority zones, HTML
download, no overflow at 320/390px, and print restoration from
`[true,false,false,false,false]` through all-open back to the original state.
The final mobile priority-zone padding is 12px by 8px. Screenshots were inspected.
Only the static server's expected glossary and sector-lens API 404s were observed.
Word was generated and structurally checked; pagination is not visually certified.

Focused checks: initial failures reflected superseded section/wording expectations
and a duplicated-text locator after adding the action fallback. Updated tests check
the new structure, internal evidence retention, complete paragraphs, existing-save
fallbacks, escaped output and print behavior. Final focused checks passed (90 passing
checks followed by five passing checks resolving the last two changed expectations).
Full suite: **1,464 passed, 2 failed in 787.41 seconds (13m07s)**. Both failures
were obsolete expectations for the removed pathway/core-question appendix. The
method assertion was corrected during the run; the DOCX route assertion was
corrected afterward. The final targeted rerun of both passes. No application code
changed after the full-suite snapshot. Log:
`output/20261013-simplification-full-regression.txt`.
Standalone downloaded HTML was also opened in Edge and visually inspected. It
contains both rating cards, all six sections and no removed supporting disclosures.
Implementation commit: `389026fe70b74e5e4a6a5386e2992c7ee36d8553`, pushed to
`fix/climate-opcs-parity`. Before push, Render confirmed that
`fcv-agent-climate-smoke` (`srv-d6gsivcr85hc73a2833g`) follows this branch and
uses commit-triggered deployment at https://fcv-agent-1.onrender.com.
The final deployment SHA and health result are recorded in draft PR #83 and the
private FCV build-parity record after the deployment completes.

## Remaining acceptance

No paid assessment was run. Both previously authorized extra runs remain consumed.
A newly authorized generated assessment must still demonstrate the new prose and
at least three substantive supported priorities for the Great Lakes case. Restricted
OPCS policy currency was not recertified during this presentation follow-up.
PR #83 remains draft. Production/main and ITS remain unchanged.
