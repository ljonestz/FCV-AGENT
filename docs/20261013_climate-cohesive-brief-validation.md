# Climate standalone brief review

## Findings and repair

Reviewing the complete editorial preview revealed two problems before another
paid assessment. Context, findings and priorities repeated the same project history
and gap inventory. More significantly, a sentence beginning "Links" was rejected
as an unsupported entity. That silently selected the older dividends finding,
which criticized the absence of documented peace or social dividends.

The capitalization check now recognizes a bounded vocabulary of generic sentence
openings and inflections of existing permitted prose terms, only in analytical
paraphrase mode and at sentence boundaries. Multiword names, acronyms, numbers,
dates, markup and action checks still apply. Strict Summary mode is unchanged.
Regression cases cover the opening words, unknown Links Cooperative, unknown
LINKS acronym, unsupported figures and the existing strict Summary rejection.

Judgment instructions give the context a clear editorial role: explain the setting
and principal delivery challenge, credit a shared response once, and reserve detail
for findings and checks. The three answers develop the brief from delivery to wider
benefits to inclusion rather than repeat the context's investment inventory.
Recommendation prose explains the purpose of the change without retelling the
findings. Versions: judgments2.12, recommendations2.14, reader2.12.
No calls, token budgets, schema fields or deadlines were added.

## Editorial preview

New local artifacts under `output/playwright/`:

- `20261013-cohesive-climate-browser-report.html`: actual browser HTML download.
- `20261013-cohesive-climate-report.html` and `...-report.docx`: Python exports.
- `20261013-cohesive-climate-session.json` and `...-reader.json`: editorial replay.
- `20261013-cohesive-climate-findings.png`: browser screenshot.
- `20261013_replay_cohesive_brief.py`: reproducible preview, with an assertion that
  all three intended narrative answers pass admission rather than use fallback.

Context is 201 words. Evidence references, original scores and two accepted actions
are retained. The visible note explains that prose was edited using saved evidence.
This is not new model generation. A new action was not invented to fill the count.

The browser confirms three intended paragraphs, including the conditional dividend
assessment, and no old missing-dividends-language finding. Its HTML download was
checked and the screenshot inspected. Layout is unchanged from the preceding
candidate. Word is generated structurally; pagination is not visually certified.

## Verification and remaining acceptance

The false rejection was reproduced by a failing test before the repair. Focused
checks passed: 30 initially, then 32 covering the final opening-word refinement,
strict schema/Summary controls, prompts and version transport. Full suite: **1,467 passed in 633.02 seconds (10m33s)**.
Log: `output/20261013-cohesive-brief-full-regression.txt`. The full run began before the last small opening-word
refinement; the final 32 checks cover that refinement directly.

No paid assessment or paid review was used. Previously authorized extra runs are
consumed. A fresh authorized quality run must demonstrate coherent prose and at
least three substantive supported priorities for the Great Lakes case before
rollout acceptance. Test deployment status is recorded in PR #83 and the private
parity record. Production/main and ITS remain unchanged.
