# ITS handover: country bank, readout and Word changes

Date: 28 October 2026

**Target release:** [PR #90](https://github.com/ljonestz/FCV-AGENT/pull/90) on
Render `main`, including the final Word heading-parser security correction.
The PR's closing release comment records the exact merge SHA, deployment and
hosted acceptance. No ITS code or configuration was changed or validated here.

## Baselines and scope

There are three baselines to keep separate:

- **Deployed Render baseline:** `6f3d5e65e213ad47135a34f9410d90ea5dcb51c4`.
  Comparing this with the current Render head covers PR #85's documentation
  update, merged PR #89, and PR #90.
- **Render main before PR #90:** `0a2ae95`. It includes PR #89, which pins the
  approved global bank and contains the readout presentation simplification.
  The immediate PR #90 delta starts at `0a2ae95`; its Word checkpoints are
  `add9711` and `622a518`, followed by the final heading-parser security fix
  and this handover. Use the PR merge SHA as the final comparison endpoint.
- **ITS:** the latest baseline recorded in the 20 September standard-FCV
  handover is ITS-reported QA commit `f8e8142` on
  `codex/climate-summary-quality-fixes`, with implementation branch
  `codex/nairobi-project-screener`. No current ITS head was verified. Check the active ITS branch and commit
  before deciding which changes it still needs.

PR #90 restores the approved full Word template and moves the compact
sensitivity/responsiveness graphic to the top of both Word routes. This is a Word
presentation change. The earlier PR #89 delta is broader: it adds qualified
country-bank and Climate research behavior, plus Summary, Detailed, copy and
export changes. An ITS handover based only on PR #90 would omit that work if the
active ITS baseline predates PR #89.

Before porting, compare the current ITS checkout with the September handover and
check the October supervised-pilot and Step-by-Step handovers for any changes ITS
may have adopted. Do not assume those changes are already in its branch.

## Shared behavior to assess for ITS

### Country bank and Climate research

PR #89 pins the approved 146-country bank, release
`2026.10.27.approved-global-country-bank`, schema 1.1.0, at bank commit
`72ce351e0f19fe52ff786196b516e6dc4a684290`, with 146 country profiles, 2,643
evidence records and 241 pathways. Profiles carry coverage and known gaps. Climate evidence selection retains source scope and qualification,
filters expired current evidence and dependent pathways, and carries explicit
limitations when material is omitted. Country-level review dates do not reset
individual evidence expiry. The bounded prompt handoff retains evidence class and
status, direction, scenario and horizon, confidence and uncertainty, geographic
and population scope, source locators and publication metadata. Whole evidence/source
bundles are capped at 6,000 bank characters and 12,000 combined; a pathway is kept
only when all supporting evidence remains. PID beneficiary country names and lists
are parsed separately and preserved.

For the Climate-FCV route, live research remains the code default. The separate
Climate search can use bounded bank coverage, known gaps and dated-source context
to seek current information. `bank_only` continues to suppress providers and
cached live context. The existing two-search limit, source gates, failure
messages and spend controls remain. The supervised-test spend guard reserves
web-search costs as well as model costs, including retries; tests must not
inherit an unlimited search allowance. Mirror the accounting semantics in ITS
when running a similarly bounded test, using its own ledger and cost schedule. Search results do not write back to the bank.
Normal FCV keeps its existing retrieval flow. The research-model setting is
explicit; the Render release uses Haiku 5.5 research and Sonnet 5.5 Quality
assessment/review. ITS must map those roles to its approved provider setup.

Routine-use approval authorizes qualified use; it does not verify every source
claim. The review record reports claim-level checks of 74 evidence records and
one pathway, while all 146 country audit dispositions remain `unresolved-limited`.
Source review, current-context checks and human approval remain separate from
structural tests. Preserve the adjudicated bank records: zero assembled pathways
does not establish hazard-only evidence, and later source checks supported the
disputed PNG figures. Do not reapply earlier review recommendations blindly.

If ITS adopts this work, mirror the shared bank schema, expiry/omission and
qualification rules, coverage/gap handoff and country parsing behavior. Keep the
ITS PPF/OPCS retrieval and its provider, routing and infrastructure choices. Do not
copy Render's public web-research implementation into the ITS service.

Relevant Render references include `sector_lenses/climate_bank.py`,
`sector_lenses/climate_bank_selector.py`, `sector_lenses/climate_context_adapter.py`,
`sector_lenses/climate_grounding.py`, `sector_lenses/climate_verified_prompts.py`,
`sector_lenses/climate_verified_pipeline.py` and `sector_lenses/research.py`. The bank and evidence decisions are documented in
[approved-country-bank integration](docs/20261026_approved-country-bank-integration.md),
[global bank routine activation](docs/20261027_global-country-bank-routine-activation.md)
and the [remediation results](docs/20261027_global-country-bank-remediation-results.md).

### Summary and Detailed presentation

PR #89 simplifies the readout presentation while keeping the canonical assessment
and priority content. Summary uses compact priority cards with regular-weight
suggested actions and links to full priority details. It omits the duplicate
sensitivity sentence, specialist-reference section and watch-items section;
those details remain available in Detailed where applicable. The Summary links
open the matching complete priority, including non-first cards. Generic opening review and preparation notices are omitted from
Summary, Detailed, Copy and Word/HTML exports. Concrete verification notes,
incomplete-analysis warnings, smoke/candidate warnings and actual route gates
remain.

Detailed retains complete priorities, distinct timing, practical considerations
and suggested text. The optional-priorities advisory appears with the priority
introduction on both routes, explaining that suggestions are optional and
should be selected using sector and country expertise. The detailed panel is
labelled "Practical considerations and Suggested Text" and carries project-cycle
guidance. Use `fcv_presentation.priority_advisory_text` as the wording contract,
including its design/implementation variants. One Copy control follows the selected tab; Word and HTML downloads
continue to contain the full Detailed report regardless of the selected tab.

Review `index.html` behavior and the Python export contract as output references;
implement the same behavior through the ITS portal and routes. Do not copy the
Render page or Flask handlers.

### Word export

PR #90 restores the approved Banner Report design for normal FCV and Climate-FCV
Word downloads: Mark C logo, navy/blue masthead, Arial typography, numbered
headings, running page furniture, linked priority overview, blue priority cards,
practical notes and Suggested Text boxes. Supplied project/run metadata appears
in the subtitle; missing identity, assessment date or classification is not
invented.

The final order is masthead, LLM warning, compact rating graphic, then the
assessment. Detailed rating explanations stay below findings. Genuine status
warnings remain before assessment content when applicable. Specific source notes
and drafting-route gates remain in the exported report.

The live implementation composes Report components directly from application
fields. Original filenames survive session reopen/resave and supply missing
project metadata. The banner is flush to the physical top of page one in both
routes, while later-page running headers retain their spacing. For ITS, mirror the visible report behavior in its own Word exporter and
preserve all current content and route conditions. Adapt shared helpers to the ITS package layout; do not transplant Flask
handlers or treat this presentation change as an analysis or rating change.

The detailed design and verification record is
[Word export design and release record](docs/20261028_climate-word-layout.md).
The preceding UI changes are in
[readout presentation simplification](docs/20261028_readout-presentation-simplification.md).

## Port and acceptance sequence

1. Record the active ITS branch, head SHA, deployed QA baseline and any work
   already adopted from the October 18 handovers. Compare that checkout with
   `f8e8142` only as a historical reference.
2. Separate the PR #89 bank/research and readout changes from the PR #90 Word
   presentation change. Port only the shared semantics that are missing from ITS. Keep the final heading-parser security fix: detect the
   Markdown prefix, then trim trailing markers with string operations; do not
   restore the overlapping whitespace regex from the earlier Word commit.
3. Preserve the ITS FastAPI routes, PPF/OPCS retrieval, Gemini/Claude configuration,
   authorization, storage and hosting. Keep the existing search and spend limits.
4. Add or update ITS-specific checks for approved bank loading, evidence expiry,
   whole qualification/coverage handoff, bank-only behavior, no bank writeback,
   summary/detail/export parity, and visible source notes and route gates.
5. Use representative documents to check the resulting reports against their
   sources. Structural tests and Word layout checks do not establish factual
   accuracy or publication approval. Any hosted or paid assessment requires its
   own agreed authorization and operating allowance.

Useful Render regression references are `tests/test_climate_bank_global_activation.py`,
`tests/test_climate_research.py`, `tests/test_climate_prompt_qualifiers.py`,
`tests/test_readout_ui_simplification.py`, `tests/test_climate_verified_render.py`,
`tests/test_climate_word_layout.py`, `tests/test_word_style.py` and
`tests/test_pilot_web_spend_guard.py`. These tests
show the contracts to reproduce; they are not evidence that ITS passes them.

## Render-only items and release limits

Do not copy Render service settings, URLs, deployment procedures, the
`render_build.py` entry point, the local unapproved-bank preview launcher or its
test configuration into ITS. The approved routine bank is distinct from the
short-lived unapproved test artifact. Keep ITS retrieval separate from Render's
public search path. If ITS adopts the approved Word design, use its own implementation
and confirm that the visual assets meet ITS requirements.

The final Render suite recorded 2,091 passed, two skipped and four
documented headless browser hangs deselected. The four have prior headed-browser
coverage. Native Microsoft Word review covered 11 Climate and 15 normal pages.
No new paid assessment calls were made. The final ten-test Word layout module and the full suite passed after the
heading-parser security correction; source/test hashes remained unchanged
during the full run. These checks cover Render
output and presentation; ITS parity and analytical acceptance remain untested.

The release checkpoint and hosted evidence are recorded on PR #90; the previous
production reference was `6f3d5e65e213ad47135a34f9410d90ea5dcb51c4`.
Country-source limitations and the need for separate source and human review
remain. Do not report an ITS port, deployment, or validation until it has been
performed and checked against the active ITS branch and service.
