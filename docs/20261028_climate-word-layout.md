# Word export design and release record

## Final behavior

Both normal FCV and Climate-FCV detailed Word downloads use the approved
Option 1 / Banner package from `Downloads/fcv_screener_word_export_handoff.zip`
and its FCV STAR and Climate Somalia reference reports. They compose the existing
Report components directly from application data: unchanged Mark C logo, navy/blue
masthead, Arial typography, numbered headings, linked priority overview, blue
priority cards, practical notes, Suggested Text boxes and running page furniture.
Management briefs retain their separate style. There is no HTML/DOCX parser in
the live export path and no hosted ITS URL added to the Render version.

The masthead touches the physical page top. Native Word previously added its
0.4-inch header distance to the floating banner, leaving 28.8pt of white space.
Header distance is now zero; running-header paragraph spacing retains the
later-page position. The project line beneath Recommendations Note uses supplied
identity or the original project filename stem, country, document type,
instrument and an explicitly labelled export date. No project identity,
classification or assessment date is invented. Session load/save preserves
original filenames in both current and legacy saves.

Final order follows the user's last clarification: masthead, LLM warning,
compact sensitivity/responsiveness summary graphic, assessment. Genuine partial,
incomplete, smoke and candidate warnings precede the assessment when applicable.
Detailed rating explanations remain below the findings (section 03 for Climate).
The top graphic applies to both live routes and both offline builders.
Generic draft/human-review/preparation preambles remain removed. Specific inline
source qualifications, route gates and snapshot traceability remain. Both routes
retain the full optional-priorities advisory. Prompts, canonical assessments,
retrieval, bank pin and approved design ancestry are unchanged by this correction.

## Verification

Actual saved-session Word downloads returned HTTP 200 in headed Edge with no
browser errors or assessment attempts. Source saves and canonical Climate
payloads stayed unchanged; reopened/resaved filenames are preserved.

Native Microsoft Word rendered 11 Climate and 15 normal pages. All pages of the
full-template versions were reviewed. Moving the summary graphic changed only
Climate pages 1–3 and normal pages 1–2; those pages received fresh review, and
all later pages are pixel-identical to the previously accepted reports. All body
text values and nonbody Word package parts remain identical across this move.
The masthead is flush at 0pt on both routes. A long-subtitle fixture also fits.

The final full suite passed: **2,091 passed, two skipped, four deselected** in
368.11s after the security correction. The four documented headless browser hangs have prior headed Edge
coverage in the presentation handoff. The run's HEAD, modified source/test path
set and all 20 source/test hashes stayed unchanged. Final top-scorecard layout
contracts passed (ten tests); Python compilation, JS syntax and diff checks
also passed. Earlier failed and interrupted runs remain as diagnostic records
and are superseded by this final full run. CodeQL identified a polynomial-time
heading regex in the Word exporter. It now matches only the heading prefix and
uses string trimming for closing markers. A long-whitespace Word-download
regression passes; the fix leaves the normal report structure unchanged.

Artifacts remain ignored under `output/20261028-climate-word-layout/`:
- `template-fidelity/top-scorecard/`: final local Word examples, native Word
  renders, browser metadata checks, content comparison and visual acceptance.
- `template-fidelity/live/` and `normal-timing/`: earlier full-template checks;
  their lower-scorecard placement is superseded by the final user clarification.
- `template-fidelity/security-final/`: final full-suite log and unchanged
  source/test hash record after the heading-parser correction.
- `template-fidelity/top-scorecard/final-suite/` and `final-suite/`: earlier suites.
- `template-fidelity/production/`: hosted acceptance helper and release artifacts.
- `template-fidelity/`: original references and banner-gap comparison.
The initial full-suite failure record is under `output/20261028-template-fidelity/`.

## Release scope and limitations

Bank PR #5 and app PR #89 are already merged (05b5a097 and 0a2ae95). This correction
is PR #90 on `fix/climate-word-parity-20261028`. The immutable bank pin remains
72ce351e0f19fe52ff786196b516e6dc4a684290. User authority covers merge and production
deployment after verification, retaining auto-deploy off and existing resources.

No new paid assessment calls: the earlier conservative USD10.729492 debit is
unchanged. The Syria example is a historical ITS-to-UI adapter; the Somalia
example is the saved Quality assessment with its specific source qualifications.
These checks establish presentation and export behavior, not new analytical
acceptance. ITS was not changed or validated; existing bank/source limitations
remain. Preserve earlier worktrees and unrelated root work.

Production promotion and hosted acceptance are pending at this checkpoint.
The closing release comment on PR #90 records the exact merge commit, deployment
and hosted checks. The ITS porting note is
`20261028_ITS_handover_main_release.md`; it distinguishes the full delta from the
previous deployed/main version and the narrower PR #90 Word change.
