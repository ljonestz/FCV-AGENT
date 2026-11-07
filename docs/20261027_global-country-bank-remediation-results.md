# Global Climate-FCV country-bank remediation

This records the draft-only remediation stage. The subsequent qualified
routine-use approval, normal app pin, approved profile support and final activation
checks are recorded in [the activation note](20261027_global-country-bank-routine-activation.md).
The candidate artifacts and source-verification limits below remain unchanged.

## Scope, method and analytical limits

The remediation covers all 146 countries in the original depth manifest, including
inherited evidence and pathways. Every source, evidence record, pathway and profile
was inventoried and screened for reference integrity, geography, causal role,
projection qualifiers and coverage statements. Machine screening is recorded
separately from passage-to-claim verification. One selected source URL per country
was attempted; access, a readable excerpt and verification have distinct statuses.

Seventy inherited evidence claims were individually passage-checked. Four new
evidence claims and one bounded reverse pathway were separately adjudicated. The
result contains 2,643 evidence records and 241 pathways: 74 evidence records and
one pathway have claim-level verification; 2,569 evidence records and 240 pathways
retain explicit independent-verification limitations. All 146 whole-bank audit
dispositions remain `unresolved-limited`, and all candidates remain draft with
null human approval fields. Verification checks whether the cited passage supports
the scoped wording; source assertions and programme intent remain distinct from
evaluated effects. This is readiness for supervised testing and further
source review, not analytical certification or permission for operational use.

The reproducible transformation preserves complete statements in compact evidence,
adds projection scenarios where absent, qualifies unresolved records, and puts
verification limits first in profile gaps. It corrects stale generic no-pathway
statements where a pathway exists. Legitimate standalone evidence remains usable;
pathway counts do not define analytical sufficiency or hazard-only coverage.

## Adjudications

- **PNG:** the original UN report supports the disputed 12 areas/projects, 24
  communities, nine grants and over 16,000 expected beneficiaries. Numbers are
  retained with physical/printed-page locators and expected-versus-achieved limits.
  Hela programme evidence is not forced into the Carteret pathway. The unrelated
  Port Moresby survey is removed from that pathway and retained as bounded context.
- **Chad:** the flood/conflict statement remains direct source reporting with a
  report-level causal limit. New evidence and a pathway describe conflict-displaced
  settlement/service constraints and flood vulnerability. The food-security estimate
  retains its dated period and analysed-population denominator. Locations require
  separate verification; refugees are affected people, not a threat category.
- **Tuvalu:** the 2060 flood projection retains SSP2-4.5/SSP5-8.5. Official Falepili
  evidence covers voluntary bilateral mobility, staying at home and continuing
  sovereignty/statehood. Preliminary 2022 risk material predates treaty entry into
  force. No armed-conflict or inevitable state-extinction claim is introduced.
- **Somalia:** source-specific non-counterfactual limits, cooperative-member
  denominator, dated seasonal versus annual projections and the EIP locator/reuse
  terms are corrected. The mutable historical GIEWS edition remains unresolved.
- **Vietnam:** historical provincial names carry the 2025 reorganization qualifier;
  historical caseloads are not silently remapped. **Venezuela:** unauthenticated
  mirror claims remain low confidence and explicitly unresolved. **Uzbekistan:**
  the restricted atlas is not filled with speculative evidence.

Every country has a ledger row and record-level screening, even where no bespoke
content addition was justified. Missing source windows and inaccessible documents
are limitations, not evidence that a claim is false. No entire bank is labelled
source-verified from a sample.

## Shared app correction

The actual merged model prompt now retains evidence status/class/role, direction,
scenario, horizon, confidence, uncertainty, geographic/population scope and source
locators/publication metadata. Pathway alternatives and uncertainty also survive.
The selector admits complete evidence/source/support bundles that fit, rather than
removing direct evidence while trying to fit an oversized pathway.

The existing 6,000-character bank and 12,000-character combined grounding budgets
are unchanged. Grounding drops whole claims rather than separating qualifications
from them, and keeps a pathway only with all supporting evidence retained. Profile
coverage and gaps have separate bounded allocations within a 1,700-character compact
profile, with explicit truncation and missing-metadata notices. Older approved
bundles without profiles disclose that limit. Empty selected pathways do not imply
absence of a mechanism.

Only unapproved test artifacts add `country_profiles`. The production builder and
schema remain unchanged and reject this artifact as a normal runtime release.
ITS must adopt the shared semantics separately while preserving its own retrieval;
no ITS port or hosted acceptance is claimed.

## Reproducible bank artifacts

The bank was committed and pushed first at
`7a89952dee352b408f6b79132ba61406b8981cb2`. The app's immutable submodule pin uses
that commit. Existing bank PR5 and app PR89 retain their original bases and draft
status; neither is merged.

Bank version: `countries/<ISO3>/candidates/2026.10.27.remediated/`.
The earlier `2026.10.26.deep` snapshot is preserved.

- `research/20261027_remediation/README.md`: method, limits and reproduction steps.
- `research/20261027_remediation/overrides.json`: source-grounded adjudications,
  locators, methods, access dates and global qualification rules.
- `research/20261027_remediation/audit/<ISO3>.json` and `aggregate.json`: complete
  inherited inventory and selective verification dispositions.
- `research/20261027_remediation/TEST_INPUTS.json`: exact 146 candidate directories.
- `reviews/20261027_remediated-country-ledger.json`: per-country transformations,
  decisions, limits and file identities.
- `reviews/20261027_remediated-review-manifest.json` and
  `20261027_remediated-approval-table.md`: regenerated review identities/index.

From the bank worktree, `python -m scripts.remediate_depth_candidates --check-only`
rebuilds all countries in temporary staging and compares every published output.
Without that option it publishes only absent outputs and refuses overwrite.
`python research/20261027_remediation/audit_sources.py --check` validates the frozen
audit inventory. Reproduction uses tracked frozen inputs; mutable source-access
collection is not rerun. Hashes attest identity, not source accuracy or approval.

Candidate totals are 146 countries, 1,096 source-metadata records, 2,643 evidence
records and 241 pathways. The bundle includes 1,045 referenced sources; unreferenced
source metadata remains in candidate files.

## Fresh local test bundle

Ignored artifact: `releases/testing/20261027_global146-remediated-test.json` in the
bank worktree and matching pinned app submodule. It is not committed or promoted.

| Field | Value |
|---|---|
| Version | `2026.10.27.global146-remediated-test` |
| Generated UTC | `2026-10-27T10:55:08Z` |
| Expiry | `2026-10-30` |
| Kind | `unapproved-country-bank-test`; `candidate=true` |
| Bytes | 8,609,267 |
| Byte and UTF-8/LF SHA-256 | `0dfc90df2422c769e07a715fd338d82dc2ab3d42143506060145bf329cf4a6df` |
| Source checksum | `e72a1c766cedcd8e6a8eefa2a040afca082d34eff4a0f596e97e73fd11daf4bf` |

Build command used from the bank worktree:

```powershell
python -m scripts.build_test_bundle --country-manifest research/20261027_remediation/TEST_INPUTS.json --generated-at 2026-10-27T10:55:08Z --test-expires-on 2026-10-30 --content-version 2026.10.27.global146-remediated-test --output releases/testing/20261027_global146-remediated-test.json
```

For later regeneration choose the actual current UTC generation time, a new output
filename/version and an expiry zero to seven days later. Do not overwrite the old
artifact, fake its time or weaken the expiry guards.

## Verified checks

- Final offline app suite: **1,979 passed, two skipped, four deselected in 579.52
  seconds**. Only the four previously documented Chromium hangs were deselected.
  Afterward, launcher validation was strengthened to reject empty coverage/gap
  sections: **all six launcher tests passed in 14.52 seconds**, including two new
  negative cases first shown to fail. Shared runtime compaction was unchanged.
- Full bank suite: **697 passed in 759.19 seconds** with
  `python -X utf8 -m pytest tests -q -p no:cacheprovider`. Repository `testpaths`
  is `tests`, which contains all tracked test modules.
- Connected app tests: **121 passed in 60.45 seconds**, no exclusions. This includes
  the unchanged frozen 24-country regression, selector/grounding, final-prompt and
  budget-edge qualification tests, profile limits, loader/production/preview guards.
- Fresh bundle check: **146 countries x three sectors = 438 final merged prompts**
  passed qualification, canonical-field, source-locator, support and budget checks.
  **344 unique identifiers** cover all **363 ISO/name/alias entries**, including
  19 duplicate entries. Names, aliases and selection aliases match the old bundle.
  The final rerun used the bundle regenerated inside the pinned submodule and the
  strengthened nonempty-profile guard, with the same 438/344 passing results.
- All 146 real compact profiles retain nonempty coverage and their leading audit
  disclosure; maximum serialized profile size is 1,514 characters against the 1,700
  cap. Regeneration from the immutable app submodule pin matches the bundle byte hash.
- Independent identity checks: all 146 prior nine-file review identities, all 146
  new country identities and review-artifact hashes, all 878 frozen baseline files,
  draft/null fields, inherited deadlines and stale generic pathway-gap checks passed.
- Post-publish reconstruction matched all 876 candidate files and four review/input
  artifacts. Freeze-manifest SHA-256:
  `844304142d4f34a47274d7f38b1a35befa4fca5fec777230f9341691931d0144`.
- Staged bank scope review: 1,034 text files, including 876 candidate files; only
  the test-bundle builder and its test modify existing tracked files. No generated
  bundle, downloaded document, binary, private-path or secret-pattern match was staged.

Offline app suite command:

```powershell
python -X utf8 -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-* --deselect=tests/test_climate_lens_frontend.py::test_chromium_print_opens_exported_disclosures_and_restores_screen_state --deselect=tests/test_climate_lens_frontend.py::test_result_stage_tabs_do_not_overflow_phone_viewport --deselect=tests/test_climate_lens_frontend.py::test_result_download_header_wraps_inside_phone_card --deselect=tests/test_climate_lens_frontend.py::test_result_session_bar_wraps_inside_phone_viewport
```

Managed Windows Temp/named-pipe and generated-file reads required normal process
permissions. Sandbox access failures were not treated as application regressions.
Preview banner/cache headers were checked by the fixture-backed local HTTP tests;
there was no fresh browser or actual-server acceptance run.

The approved runtime remains schema 1.1.0, version
`2026.10.26.approved-country-bank`, 24 countries, 272 sources, 531 evidence records
and 168 pathways. Normalized UTF-8/LF SHA-256:
`12f0a7b5c8267ec3a8ed8033f3e4716af69024a9290e023e5264a94ed35ebda8`.
Source checksum:
`b421effc50cf0a46da126ee4deba481ea1b3ea379b846954a45c780ad6023988`.

## Supervised testing

Use the preserved app worktree `.worktrees/global-country-depth-app-20261026`
on `feat/global-country-bank-depth-20261026`, not an unrelated working checkout.
Initialize the pinned submodule, verify the bundle fingerprint/expiry, then run:

```powershell
python -m scripts.run_country_bank_test --bundle data/climate-fcv-country-bank/releases/testing/20261027_global146-remediated-test.json --check
python -m scripts.run_country_bank_test --bundle data/climate-fcv-country-bank/releases/testing/20261027_global146-remediated-test.json --serve
```

The launcher manages all three preview guards and binds `127.0.0.1:5001` without
debugger/reloader. Check the UNAPPROVED banner before use. Preview HTML must use
`no-store` and omit ETag/Last-Modified. Never set these guards in normal startup,
Render or ITS. Stop the local server when finished. Serving this bundle does not
authorize paid model calls or operational reliance.

For separately authorized supervised assessments, inspect Chad Water/Lac and
Eastern Chad location limits; PNG Agriculture/Water with Hela separated from
Carteret; Tuvalu Urban with scenarios, treaty timing and voluntary mobility;
Somalia Agriculture with dated projections and BRCiS source-specific outcomes;
Vietnam historical boundaries; Venezuela mirror limits; and Uzbekistan atlas
coverage. Compare the selected records and actual model-facing prompt before
judging the generated narrative. Check source grounding, local applicability,
expected versus achieved outcomes and sensitivity versus demonstrated responsiveness.
The standard public Somalia IPF check is
`test_documents/live_acceptance/somalia-stairp-p513127-concept-pid-20260207.pdf`.

No merge, bank approval, deployment, hosted configuration change or paid/live model
assessment was performed. No fresh browser/model, DOCX visual or hosted acceptance
is claimed. The four known Chromium hangs remain an explicit offline-suite exclusion.
